import os
import boto3
import json
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

def get_object(s3_resource, bucket_name: str, object_path: str) -> list:
    try:
        obj = s3_resource.Object(bucket_name, object_path)
        data = obj.get()
        content = data['Body'].read().decode('utf-8')
        json_data = json.loads(content)
        print(f"Successfully retrieved and parsed JSON object: {object_path}")
        return json_data
    except Exception as e:
        print(f'Failed to download or parse JSON from {bucket_name}/{object_path}: {e}')
        raise

def put_object(s3_resource, local_file_path: str, bucket_name: str, object_path: str):
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

if __name__ == '__main__':
    print('JSON Merge')
    print('args:', args)
    local_file_path = './tmp/output.json'

    # Step 1: Read input JSON
    input_data_frames = []
    number_of_input = args['number_of_input']
    for i in range(number_of_input):
        input = args['input{}'.format(i+1)]
        s3_client_input = create_s3_client(input['end_point'], input['access_key'], input['secret_key'])
        input_data = get_object(
            s3_resource=s3_client_input,
            bucket_name=input['bucket_name'],
            object_path=input['object_path']
        )  # data read
        input_data_frames.append(input_data)
    
    # Step 2: Apply regex transformation
    algorithm.solution(
        input_data_frames,
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
    )  # data write

    # Step 4: Optionally delete input file
    if args['delete_input']:
        for i in range(number_of_input):
            input = args['input{}'.format(i)]
            s3_client_input1 = create_s3_client(input['end_point'], input['access_key'], input['secret_key'])
            delete_object(
                s3_resource=s3_client_input1,
                bucket_name=input['bucket_name'],
                object_path=input['object_path']
            )
