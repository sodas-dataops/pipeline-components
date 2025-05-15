import os
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


def download_file(s3_resource, bucket_name, object_path, local_file_path):
    """
    Download a file from object storage to a local path.
    """
    try:
        obj = s3_resource.Object(bucket_name, object_path)
        obj.download_file(local_file_path)
        print(f"Downloaded {object_path} to {local_file_path}")
    except Exception as e:
        print(f"Failed to download file: {e}")
        raise

def save_report(s3_resource, report_content: str, bucket_name: str, object_path: str):
    try:
        obj = s3_resource.Object(bucket_name, object_path)
        obj.put(Body=report_content.encode('utf-8'))
        print(f'Successfully uploaded report to {bucket_name}/{object_path}')
    except Exception as e:
        print(f'Failed to upload report to {bucket_name}/{object_path}: {e}')
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
    print('CSV Word Count Program')
    print('args:', args)
    local_file_path = './tmp/input_file'

    input1 = args['input1']
    s3_client_input1 = create_s3_client(input1['end_point'], input1['access_key'], input1['secret_key'])
    # Download file from object storage
    download_file(
        s3_client_input1,
        bucket_name=input1['bucket_name'],
        object_path=input1['object_path'],
        local_file_path=local_file_path
    )
    
    settings = args['settings']
    local_file_path, report = algorithm.solution(
        api_url=settings['api_url'],
        file_path_query=settings['file_path_query'],
        local_file_path=local_file_path
    )

    # Save report
    task_report = args['task_report']
    s3_client_task_report = create_s3_client(task_report['end_point'], task_report['access_key'], task_report['secret_key'])
    save_report(
        s3_resource=s3_client_task_report,
        report_content=report,
        bucket_name=task_report['bucket_name'],
        object_path=task_report['object_path']
    )

    # Optionally delete input file
    if args['delete_input']:
        delete_object(
            s3_resource=s3_client_input1,
            bucket_name=input1['bucket_name'],
            object_path=input1['object_path']
        )