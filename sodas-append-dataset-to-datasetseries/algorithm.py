import os
import time
from datetime import datetime
from datetime import date
from sodas_sdk import Dataset, DatasetSeries, Distribution, configure_api_url

def generate_report(dataset_id: str, datasetseries_id: str, input_filename: str, 
                  file_size: int, elapsed_time: float) -> str:
    """
    작업 보고서를 생성하는 함수.
    
    Parameters:
    - dataset_id (str): 생성된 데이터셋 ID
    - datasetseries_id (str): 데이터셋 시리즈 ID
    - input_filename (str): 입력 파일 경로
    - file_size (int): 파일 크기 (bytes)
    - elapsed_time (float): 소요 시간 (초)
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    report = f"""# SODAS 데이터셋 추가 작업 보고서

## 1. 작업 개요
- **작업 유형**: 데이터셋 시리즈에 데이터셋 추가
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **입력 파일**: {input_filename}
- **파일 크기**: {file_size / 1024:.2f} KB

## 3. SODAS 설정
- **데이터셋 시리즈 ID**: {datasetseries_id}
- **생성된 데이터셋 ID**: {dataset_id}

## 4. 처리 결과
- **상태**: 성공
- **결과**: 데이터셋이 성공적으로 생성되고 데이터셋 시리즈에 추가됨

## 5. 성능 지표
- **처리 속도**: {file_size / elapsed_time / 1024:.2f} KB/s
"""
    return report

async def solution(input_filename: str, settings: dict):
    """
    SODAS에 데이터셋을 생성하고 데이터셋 시리즈에 추가하는 함수.
    
    Parameters:
    - input_filename (str): 입력 파일 경로
    - settings (dict): SODAS 설정
    
    Returns:
    - tuple: (생성된 데이터셋 ID, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] SODAS 데이터셋 추가 작업을 시작합니다.")
    
    # SODAS API URL 설정
    print("\n[1/5] SODAS API를 초기화합니다...")
    configure_api_url(
        settings['datahub_api_url'],
        settings['governance_api_url']
    )
    print(f"- DataHub API URL: {settings['datahub_api_url']}")
    print(f"- Governance API URL: {settings['governance_api_url']}")
    
    # 파일 크기 확인
    file_size = os.path.getsize(input_filename)
    print(f"- 입력 파일 크기: {file_size / 1024:.2f} KB")
    
    # 데이터셋 생성
    print("\n[2/5] 데이터셋을 생성합니다...")
    dataset = Dataset()
    
    # 기본 메타데이터 설정
    today_str = date.today().isoformat()  # '2025-04-23' 형식
    dataset.set_title(f"{settings['dataset_title']} {today_str}")
    dataset.set_description(settings['dataset_description'])
    dataset.type = settings['type']
    dataset.access_rights = settings['access_rights']
    dataset.license = settings['license']
    
    # 디스트리뷰션 생성
    print("\n[3/5] 디스트리뷰션을 생성합니다...")
    Distribution.configure_bucket_name(settings['distribution_bucket_name'])
    distribution = dataset.create_distribution()
    distribution.set_title(settings['distribution_title'])
    distribution.set_description(settings['distribution_description'])
    distribution.set_uploading_data(input_filename)
    distribution.byte_size = file_size
    
    # 데이터셋 생성 및 업로드
    print("\n[4/5] 데이터셋을 생성하고 업로드합니다...")
    await dataset.create_db_record()
    dataset_id = dataset.id
    print(f"- 데이터셋 ID: {dataset_id}")
    
    # 데이터셋 시리즈에 추가
    print("\n[5/5] 데이터셋 시리즈에 데이터셋을 추가합니다...")
    datasetseries = await DatasetSeries.get_db_record(settings['datasetseries_id'])
    datasetseries.append_series_member(dataset)
    await datasetseries.update_db_record()
    print(f"- 데이터셋 시리즈 ID: {settings['datasetseries_id']}")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\n[요약]")
    print(f"- 생성된 데이터셋 ID: {dataset_id}")
    print(f"- 데이터셋 시리즈 ID: {settings['datasetseries_id']}")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    
    # 보고서 생성
    report = generate_report(dataset_id, settings['datasetseries_id'], 
                           input_filename, file_size, elapsed_time)
    
    return dataset_id, report 