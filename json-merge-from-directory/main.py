import os
import boto3
import json
import time
from io import StringIO
from config.config import args
import algorithm
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

env = 'development' if not 'APP_ENV' in os.environ else os.environ['APP_ENV']
args = args[env]

# 로그 출력을 위한 글로벌 변수와 락
print_lock = Lock()
total_files = 0
processed_files = 0
last_progress_time = 0
PROGRESS_INTERVAL = 2  # 진행률 출력 간격(초)

def create_s3_client(rook_ceph_base_url, access_key, secret_key):
    return boto3.resource(
        's3',
        endpoint_url=rook_ceph_base_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        use_ssl=False,
        verify=False
    )

def print_progress(force=False):
    """진행률을 출력합니다. PROGRESS_INTERVAL 간격으로만 출력됩니다."""
    global last_progress_time
    current_time = time.time()
    
    if force or (current_time - last_progress_time >= PROGRESS_INTERVAL):
        with print_lock:
            progress = (processed_files / total_files * 100) if total_files > 0 else 0
            print(f"\r- 진행률: {progress:.1f}% ({processed_files}/{total_files} 파일 처리됨)", 
                  end='' if not force else '\n')
            last_progress_time = current_time

def process_json_file(args):
    """단일 JSON 파일을 처리하는 함수"""
    global processed_files
    obj, bucket_name = args
    
    try:
        content = obj.get()['Body'].read().decode('utf-8')
        json_data = json.loads(content)
        
        # 진행률 업데이트
        with print_lock:
            processed_files += 1
        print_progress()
        
        return json_data
    except Exception as e:
        with print_lock:
            print(f"\n- 경고: {obj.key} 처리 중 오류 발생: {str(e)}")
            processed_files += 1
        return None

def get_objects_from_directory(s3_resource, bucket_name: str, directory_path: str) -> list:
    """
    S3/MinIO의 특정 디렉토리에서 모든 JSON 파일을 병렬로 가져옵니다.
    
    Args:
        s3_resource: S3 리소스 객체
        bucket_name (str): 버킷 이름
        directory_path (str): 디렉토리 경로
        
    Returns:
        list: JSON 객체들의 리스트
    """
    global total_files, processed_files
    start_time = time.time()
    
    try:
        bucket = s3_resource.Bucket(bucket_name)
        
        # # 디렉토리 경로가 '/'로 끝나도록 보장
        # if not directory_path.endswith('/'):
        #     directory_path += '/'
            
        print(f"\n[1/2] 디렉토리 {directory_path}에서 JSON 파일을 검색하고 로드합니다...")
        
        # JSON 파일 목록 수집
        json_objects = [(obj, bucket_name) for obj in bucket.objects.filter(Prefix=directory_path)
                       if obj.key.endswith('.json')]
        total_files = len(json_objects)
        
        if not json_objects:
            print(f"- 경고: 디렉토리 {directory_path}에서 JSON 파일을 찾을 수 없습니다.")
            return []
            
        print(f"- {total_files}개의 JSON 파일을 발견했습니다.")
        
        # 병렬로 파일 처리
        json_data_list = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_json = {executor.submit(process_json_file, args): args for args in json_objects}
            
            for future in as_completed(future_to_json):
                result = future.result()
                if result is not None:
                    json_data_list.append(result)
        
        # 최종 진행률 출력
        print_progress(force=True)
        
        # 처리 결과 요약
        end_time = time.time()
        print(f"\n- 처리 완료: {len(json_data_list)}개 파일 성공 ({total_files - len(json_data_list)}개 실패)")
        print(f"- 총 소요 시간: {end_time - start_time:.2f}초")
        print(f"- 평균 처리 시간: {(end_time - start_time) / total_files:.2f}초/파일")
        
        return json_data_list
        
    except Exception as e:
        print(f'\n- 오류: {bucket_name}/{directory_path} 처리 중 실패: {e}')
        raise

def put_object(s3_resource, local_file_path: str, bucket_name: str, object_path: str):
    try:
        obj = s3_resource.Object(bucket_name, object_path)
        obj.upload_file(local_file_path)
        print(f'- 파일 업로드 완료: {bucket_name}/{object_path}')
    except Exception as e:
        print(f'- 오류: {local_file_path} 업로드 실패: {e}')
        raise

if __name__ == '__main__':
    print('JSON Merge from Directory')
    start_time = time.time()
    local_file_path = './tmp/output.json'
    
    try:
        # Step 1: Read input JSON files from directory
        input = args['input1']
        s3_client_input = create_s3_client(input['end_point'], input['access_key'], input['secret_key'])
        input_data_list = get_objects_from_directory(
            s3_resource=s3_client_input,
            bucket_name=input['bucket_name'],
            directory_path=input['object_path']
        )
        
        if not input_data_list:
            raise ValueError("처리할 JSON 데이터가 없습니다.")
        
        # Step 2: Merge JSON files
        algorithm.solution(
            input_data_list,
            local_file_path
        )
        
        # Step 3: Save output JSON
        output1 = args['output1']
        s3_client_output1 = create_s3_client(output1['end_point'], output1['access_key'], output1['secret_key'])
        put_object(
            s3_resource=s3_client_output1,
            local_file_path=local_file_path,
            bucket_name=output1['bucket_name'],
            object_path=output1['object_path']
        )
        
        # 전체 처리 시간 출력
        total_time = time.time() - start_time
        print(f"\n[완료] 전체 처리 시간: {total_time:.2f}초")
    except Exception as e:
        print(f"\n- 오류: 전체 처리 중 실패: {e}")
