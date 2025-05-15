import os
import boto3
import numpy as np
from io import StringIO
from config.config import args
import algorithm

env = 'development' if not 'APP_ENV' in os.environ else os.environ['APP_ENV']
args = args[env]
    

def create_s3_client(rook_ceph_base_url, access_key, secret_key):
    return boto3.resource(
        's3',
        endpoint_url=rook_ceph_base_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        use_ssl=False,
        verify=False
    )

def get_object(
        s3_resource,
        bucket_name: str,
        object_path: str,
        is_npz: bool = False
    ):
    try:
        obj = s3_resource.Object(bucket_name, object_path)
        data = obj.get()
        content = data['Body'].read()
        
        if is_npz:
            # npz 파일을 메모리에서 직접 로드
            import io
            npz_data = np.load(io.BytesIO(content), allow_pickle=True)
            return {'idxs': npz_data['idxs'], 'embeddings': npz_data['embeddings']}
        else:
            return StringIO(content.decode('utf-8'))
            
        print(f"Successfully retrieved object: {object_path}")
    except Exception as e:
        print(f'Failed to download from {bucket_name}/{object_path}: {e}')
        raise

def put_object(
        s3_resource,
        local_file_path: str,
        bucket_name: str,
        object_path: str
    ):
    try:
        obj = s3_resource.Object(bucket_name, object_path)
        obj.upload_file(local_file_path)
        
        print(f'Successfully uploaded {local_file_path} to {bucket_name}/{object_path}')
    except Exception as e:
        print(f'Failed to upload {local_file_path} to {bucket_name}/{object_path}: {e}')
        raise

def save_report(
        s3_resource,
        report_content: str,
        bucket_name: str,
        object_path: str
    ):
    try:
        obj = s3_resource.Object(bucket_name, object_path)
        obj.put(Body=report_content.encode('utf-8'))
        
        print(f'Successfully uploaded report to {bucket_name}/{object_path}')
    except Exception as e:
        print(f'Failed to upload report to {bucket_name}/{object_path}: {e}')
        raise

if __name__ == '__main__' :
    print('CSV Embedding Generator')
    print('args:', args)
    local_file_path = './tmp/embeddings.npz'

    # 기존 임베딩 결과 확인
    existing_embeddings = None
    try:
        output1 = args['output1']
        s3_client_output1 = create_s3_client(output1['end_point'], output1['access_key'], output1['secret_key'])
        existing_embeddings = get_object(
            s3_resource=s3_client_output1,
            bucket_name=output1['bucket_name'],
            object_path=output1['object_path'],
            is_npz=True
        )
        print("기존 임베딩 결과를 찾았습니다.")
    except Exception as e:
        print("기존 임베딩 결과가 없거나 읽을 수 없습니다:", e)

    # 입력 데이터 처리
    input1 = args['input1']
    s3_client_input1 = create_s3_client(input1['end_point'], input1['access_key'], input1['secret_key'])
    input1_obj = get_object(
        s3_resource=s3_client_input1,
        bucket_name=input1['bucket_name'],
        object_path=input1['object_path']
    )
    
    # 임베딩 실행
    output_filename, report = algorithm.solution(
        input1_obj, 
        local_file_path, 
        args['settings']['target_column'],
        args['settings']['idx_column'],
        args['settings']['model_name'],
        existing_embeddings
    )

    # 결과 저장
    output1 = args['output1']
    s3_client_output1 = create_s3_client(output1['end_point'], output1['access_key'], output1['secret_key'])
    put_object(
        s3_resource=s3_client_output1,
        local_file_path=local_file_path,
        bucket_name=output1['bucket_name'], 
        object_path=output1['object_path']
    )

    # 보고서 저장
    task_report = args['task_report']
    s3_client_task_report = create_s3_client(task_report['end_point'], task_report['access_key'], task_report['secret_key'])
    save_report(
        s3_resource=s3_client_task_report,
        report_content=report,
        bucket_name=task_report['bucket_name'],
        object_path=task_report['object_path']
    )