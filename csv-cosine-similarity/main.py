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

def get_npz(s3_resource, bucket_name: str, object_path: str, local_path: str):
    try:
        obj = s3_resource.Object(bucket_name, object_path)
        obj.download_file(local_path)
        print(f"Downloaded {object_path} to {local_path}")
    except Exception as e:
        print(f"Error downloading {object_path}: {e}")
        raise

def put_file(s3_resource, local_path: str, bucket_name: str, object_path: str):
    try:
        obj = s3_resource.Object(bucket_name, object_path)
        obj.upload_file(local_path)
        print(f"Uploaded {local_path} to {object_path}")
    except Exception as e:
        print(f"Error uploading {local_path}: {e}")
        raise

if __name__ == '__main__' :
    print("Cosine Similarity Matcher")
    print('args:', args)
    
    # 임시 파일 경로 설정
    query_local = "./tmp/query.npz"
    candidate_local = "./tmp/candidate.npz"
    result_path = "./tmp/result.json"
    report_path = "./tmp/task_report.md"
    os.makedirs(os.path.dirname(query_local), exist_ok=True)

    # Object Storage 클라이언트 생성
    s3_q = create_s3_client(
        rook_ceph_base_url=args['query_embeddings_data']['end_point'],
        access_key=args['query_embeddings_data']['access_key'],
        secret_key=args['query_embeddings_data']['secret_key']
    )
    s3_c = create_s3_client(
        rook_ceph_base_url=args['candidate_embeddings_data']['end_point'],
        access_key=args['candidate_embeddings_data']['access_key'],
        secret_key=args['candidate_embeddings_data']['secret_key']
    )
    s3_o = create_s3_client(
        rook_ceph_base_url=args['output1']['end_point'],
        access_key=args['output1']['access_key'],
        secret_key=args['output1']['secret_key']
    )

    # 입력 파일 다운로드
    get_npz(s3_q, args['query_embeddings_data']['bucket_name'], args['query_embeddings_data']['object_path'], query_local)
    get_npz(s3_c, args['candidate_embeddings_data']['bucket_name'], args['candidate_embeddings_data']['object_path'], candidate_local)

    # 코사인 유사도 계산 및 결과 저장
    results, report_content = algorithm.solution(
        query_local, 
        candidate_local, 
        result_path, 
        args['settings']['top_n'], 
        args['settings']['threshold']
    )
    
    # 보고서 저장
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    print(f'\n보고서가 생성되었습니다: {report_path}')

    # 결과 파일 업로드
    put_file(s3_o, result_path, args['output1']['bucket_name'], args['output1']['object_path'])
    
    # 보고서 업로드
    put_file(s3_o, report_path, args['task_report']['bucket_name'], args['task_report']['object_path'])
