import os
import boto3
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

if __name__ == '__main__':
    print('JSON Upload to Object Storage')
    print('args:', args)
    
    # 임시 파일 경로 설정
    local_file_path = './tmp/output.json'
    report_file_path = './tmp/task_report.md'
    os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
    
    # JSON 데이터 처리 및 임시 파일 저장
    output_file, report_content = algorithm.solution(
        args['settings']['json_data'],
        local_file_path
    )
    
    # 보고서 저장
    with open(report_file_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    print(f'\n보고서가 생성되었습니다: {report_file_path}')
    
    # Object Storage에 결과 데이터 업로드
    output1 = args['output1']
    s3_client = create_s3_client(
        output1['end_point'],
        output1['access_key'],
        output1['secret_key']
    )
    
    put_object(
        s3_resource=s3_client,
        local_file_path=local_file_path,
        bucket_name=output1['bucket_name'],
        object_path=output1['object_path']
    )
    
    # Object Storage에 보고서 업로드
    task_report = args['task_report']
    put_object(
        s3_resource=s3_client,
        local_file_path=report_file_path,
        bucket_name=task_report['bucket_name'],
        object_path=task_report['object_path']
    ) 