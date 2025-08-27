import os
import base64
import tempfile
import boto3
from config.config import args
from core import algorithm_kubernetes_log_collector as algorithm

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

def put_object(s3_resource, local_file_path: str, bucket_name: str, object_path: str):
    try:
        obj = s3_resource.Object(bucket_name, object_path)
        obj.upload_file(local_file_path)
        print(f'Successfully uploaded {local_file_path} to {bucket_name}/{object_path}')
    except Exception as e:
        print(f'Failed to upload {local_file_path} to {bucket_name}/{object_path}: {e}')
        raise

def upload_log_file_to_s3(s3_resource, local_file_path, bucket_name, object_prefix):
    filename = os.path.basename(local_file_path)
    object_path = f"{object_prefix.rstrip('/')}/{filename}"
    put_object(s3_resource, local_file_path, bucket_name, object_path)

def decode_kubeconfig_from_env(kubeconfig_b64):
    if not kubeconfig_b64:
        raise RuntimeError('KUBECONFIG_BASE64 환경변수가 필요합니다.')
    kubeconfig_bytes = base64.b64decode(kubeconfig_b64)
    tmp = tempfile.NamedTemporaryFile(delete=False, mode='wb', suffix='.yaml')
    tmp.write(kubeconfig_bytes)
    tmp.close()
    return tmp.name

if __name__ == '__main__':
    print('Kubernetes Log Collector')
    print('args:', args)
    
    report_file_path = './tmp/task_report.md'
    os.makedirs('./tmp', exist_ok=True)

    output1 = args['output1']
    s3_client_output1 = create_s3_client(output1['end_point'], output1['access_key'], output1['secret_key'])

    def upload_callback(log_file):
        upload_log_file_to_s3(
            s3_resource=s3_client_output1,
            local_file_path=log_file,
            bucket_name=output1['bucket_name'],
            object_prefix=output1['object_path']
        )

    kubeconfig_path = decode_kubeconfig_from_env(args['settings']['kubeconfig_base64'])

    saved_files, report_content = algorithm.solution(
        settings=args['settings'],
        kubeconfig_path=kubeconfig_path,
        upload_callback=upload_callback
    )
    
    with open(report_file_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    print(f'\n보고서가 생성되었습니다: {report_file_path}')

    task_report = args['task_report']
    put_object(
        s3_resource=s3_client_output1,
        local_file_path=report_file_path,
        bucket_name=task_report['bucket_name'],
        object_path=task_report['object_path']
    ) 