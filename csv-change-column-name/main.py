import os
from config.config import args
import boto3
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
        object_path: str
    ) -> bytes:
    try:
        obj = s3_resource.Object(bucket_name, object_path)
        data = obj.get()
        content = data['Body'].read().decode('utf-8')

        print(f"Successfully retrieved object: {object_path}")
        return StringIO(content)
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

def delete_object(s3_resource, bucket_name: str, object_path: str):
    try:
        obj = s3_resource.Object(bucket_name, object_path)
        obj.delete()
        print(f"Successfully deleted object: {bucket_name}/{object_path}")
    except Exception as e:
        print(f'Failed to delete {bucket_name}/{object_path}: {e}')
        raise

if __name__ == '__main__' :
    print('CSV Column Name Change!')
    print('args:', args)
    
    # 임시 파일 경로 설정
    local_file_path = './tmp/output.csv'
    report_file_path = './tmp/task_report.md'
    os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

    # Step 1: Read input CSV
    input1 = args['input1']
    s3_client_input1 = create_s3_client(input1['end_point'], input1['access_key'], input1['secret_key'])
    input1_data = get_object(
        s3_resource=s3_client_input1,
        bucket_name=input1['bucket_name'],
        object_path=input1['object_path']
    ) # data read

    # Step 2: Apply lambda transformation
    settings = args['settings']
    output_file, report_content = algorithm.solution(
        input1_data,
        settings['input_cols'],
        settings['output_cols'],
        local_file_path
    )
    
    # 보고서 저장
    with open(report_file_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    print(f'\n보고서가 생성되었습니다: {report_file_path}')

    # Step 3: Upload output CSV
    output1 = args['output1']
    s3_client_output1 = create_s3_client(output1['end_point'], output1['access_key'], output1['secret_key'])
    put_object(
        s3_resource=s3_client_output1,
        local_file_path=local_file_path,
        bucket_name=output1['bucket_name'], 
        object_path=output1['object_path']
    ) # data write
    
    # Step 4: Upload report
    task_report = args['task_report']
    put_object(
        s3_resource=s3_client_output1,
        local_file_path=report_file_path,
        bucket_name=task_report['bucket_name'],
        object_path=task_report['object_path']
    )

    # Step 5: Optionally delete input file
    if args['delete_input']:
        delete_object(
            s3_resource=s3_client_input1,
            bucket_name=input1['bucket_name'],
            object_path=input1['object_path']
        )
