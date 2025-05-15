import os
import json
import asyncio
from algorithm import solution

async def test_sodas_append_dataset():
    """
    SODAS 데이터셋 추가 기능을 테스트하는 함수.
    """
    # 테스트용 설정
    settings = {
        'datahub_api_url': 'http://sodas-profile.221.154.134.31.traefik.me:10017',
        'governance_api_url': 'http://api.221.154.134.31.traefik.me:10019',
        'datasetseries_id': '5c8bccde-86a8-4b05-8fd2-ff0a19825c36',
        'dataset_title': '테스트 데이터셋',
        'dataset_description': '테스트용 데이터셋입니다.',
        'distribution_bucket_name': 'jobs',
        'distribution_title': '테스트 분배',
        'distribution_description': '테스트용 데이터 분배입니다.',
        'type': 'http://purl.org/dc/dcmitype/Dataset',
        'access_rights': 'http://purl.org/eprint/accessRights/OpenAccess',
        'license': 'http://creativecommons.org/licenses/by/4.0/'
    }
    
    # 테스트용 입력 파일 생성
    test_input_path = './tmp/test_data.csv'
    
    try:
        # 솔루션 실행
        dataset_id, report = await solution(test_input_path, settings)
        
        # 결과 검증
        assert dataset_id is not None, "데이터셋 ID가 생성되지 않았습니다."
        assert report is not None, "보고서가 생성되지 않았습니다."
        assert 'SODAS 데이터셋 추가 작업 보고서' in report, "보고서 형식이 올바르지 않습니다."
        
        print("테스트 성공!")
        print(f"생성된 데이터셋 ID: {dataset_id}")
        
    except Exception as e:
        print(f"테스트 실패: {str(e)}")
        raise
    

if __name__ == '__main__':
    asyncio.run(test_sodas_append_dataset()) 