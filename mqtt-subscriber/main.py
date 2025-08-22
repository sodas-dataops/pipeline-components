#!/usr/bin/env python3
"""
MQTT 클라이언트 및 ThingSpeak IoT 데이터 실시간 수신기
"""

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

def put_object(s3_resource, local_file_path: str, bucket_name: str, object_path: str):
    try:
        obj = s3_resource.Object(bucket_name, object_path)
        obj.upload_file(local_file_path)
        print(f'Successfully uploaded {local_file_path} to {bucket_name}/{object_path}')
    except Exception as e:
        print(f'Failed to upload {local_file_path} to {bucket_name}/{object_path}: {e}')
        raise

def upload_json_file_to_s3(s3_resource, local_file_path, bucket_name, object_prefix):
    filename = os.path.basename(local_file_path)
    object_path = f"{object_prefix.rstrip('/')}/{filename}"
    put_object(s3_resource, local_file_path, bucket_name, object_path)

if __name__ == '__main__':
    print('MQTT Subscriber')
    print('args:', args)
    
    # 임시 디렉토리 및 파일 경로
    report_file_path = './tmp/task_report.md'
    os.makedirs('./tmp', exist_ok=True)

    # Object Storage S3 클라이언트 준비
    output1 = args['output1']
    s3_client_output1 = create_s3_client(output1['end_point'], output1['access_key'], output1['secret_key'])

    # 업로드 콜백 정의: json 파일 생성 시마다 S3 업로드
    def upload_callback(json_file):
        upload_json_file_to_s3(
            s3_resource=s3_client_output1,
            local_file_path=json_file,
            bucket_name=output1['bucket_name'],
            object_prefix=output1['object_path']
        )

    # MQTT 구독 및 메시지 저장 (json 파일 생성 시마다 업로드)
    saved_files, report_content = algorithm.solution(
        settings=args['settings'],
        upload_callback=upload_callback
    )
    
    # 보고서 저장
    with open(report_file_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    print(f'\n보고서가 생성되었습니다: {report_file_path}')

    # Object Storage에 보고서 업로드
    task_report = args['task_report']
    put_object(
        s3_resource=s3_client_output1,
        local_file_path=report_file_path,
        bucket_name=task_report['bucket_name'],
        object_path=task_report['object_path']
    ) 