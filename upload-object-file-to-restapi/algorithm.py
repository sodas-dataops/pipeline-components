import requests
import os
import time
from datetime import datetime

def generate_report(
    api_url: str,
    file_path_query: str,
    local_file_path: str,
    file_size: int,
    elapsed_time: float,
    status_code: int,
    response_text: str = None
) -> str:
    """
    파일 업로드 작업 보고서를 생성하는 함수.
    
    Parameters:
    - api_url (str): API 기본 URL
    - file_path_query (str): 파일 경로 쿼리
    - local_file_path (str): 로컬 파일 경로
    - file_size (int): 파일 크기 (바이트)
    - elapsed_time (float): 소요 시간 (초)
    - status_code (int): API 응답 상태 코드
    - response_text (str): API 응답 내용
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    report = f"""# 파일 업로드 작업 보고서

## 1. 작업 개요
- **작업 유형**: 파일 업로드
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 파일 정보
- **파일명**: {os.path.basename(local_file_path)}
- **파일 크기**: {file_size / 1024 / 1024:.2f} MB
- **전송 속도**: {file_size / elapsed_time / 1024 / 1024:.2f} MB/s

## 3. API 정보
- **API URL**: {api_url}
- **파일 경로 쿼리**: {file_path_query}
- **전체 URL**: {api_url}?file_path={file_path_query}

## 4. 처리 결과
- **상태 코드**: {status_code}
- **상태**: {'성공' if status_code == 200 else '실패'}
{f'- **응답 내용**: {response_text}' if response_text else ''}

## 5. 성능 지표
- **처리 속도**: {file_size / elapsed_time / 1024 / 1024:.2f} MB/s
- **응답 시간**: {elapsed_time:.2f}초

## 6. 작업 상태
- **상태**: {'성공' if status_code == 200 else '실패'}
- **처리 결과**: {'파일이 성공적으로 업로드됨' if status_code == 200 else '파일 업로드 실패'}
"""
    return report

def solution(api_url, file_path_query, local_file_path) -> tuple:
    """
    Upload a file to a specified REST API endpoint.

    Parameters:
    - api_url: The base URL of the API.
    - file_path_query: Query parameter to append to the API URL.
    - local_file_path: The path to the local file to be uploaded.
    
    Returns:
    - tuple: (로컬 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] 파일 업로드 작업을 시작합니다.")
    print(f"- API URL: {api_url}")
    print(f"- 파일 경로 쿼리: {file_path_query}")
    print(f"- 로컬 파일 경로: {local_file_path}")
    
    # 파일 존재 여부 확인
    print("\n[1/3] 업로드할 파일을 확인합니다...")
    if not os.path.exists(local_file_path):
        raise FileNotFoundError(f"업로드할 파일을 찾을 수 없습니다: {local_file_path}")
    
    file_size = os.path.getsize(local_file_path)
    print(f"- 파일 크기: {file_size / 1024 / 1024:.2f} MB")
    
    # API 요청 준비
    print("\n[2/3] API 요청을 준비합니다...")
    full_url = f"{api_url}?file_path={file_path_query}"
    headers = {
        'User-Agent': 'WorkflowComponent/1.0'
    }
    print(f"- 전체 URL: {full_url}")
    
    # 파일 업로드
    print("\n[3/3] 파일을 업로드합니다...")
    try:
        with open(local_file_path, 'rb') as file:
            files = {'file': file}
            print("- 파일 스트림을 열었습니다.")
            print("- API 요청을 전송합니다...")
            response = requests.post(full_url, headers=headers, files=files, timeout=30)
            
            if response.status_code == 200:
                print(f"- 업로드 성공! (상태 코드: {response.status_code})")
            else:
                print(f"- 업로드 실패 (상태 코드: {response.status_code})")
                print(f"- 응답 내용: {response.text}")
                raise Exception(f"API 요청 실패: {response.status_code}")

    except requests.exceptions.Timeout:
        print("- 업로드 시간 초과: 30초가 지났습니다.")
        raise
    except requests.exceptions.RequestException as e:
        print(f"- 네트워크 오류 발생: {str(e)}")
        raise
    except Exception as e:
        print(f"- 예상치 못한 오류 발생: {str(e)}")
        raise
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\n[요약]")
    print(f"- 업로드된 파일: {os.path.basename(local_file_path)}")
    print(f"- 파일 크기: {file_size / 1024 / 1024:.2f} MB")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    print(f"- 전송 속도: {file_size / elapsed_time / 1024 / 1024:.2f} MB/s")
    print(f"- 대상 URL: {full_url}")

    # 보고서 생성
    report = generate_report(
        api_url=api_url,
        file_path_query=file_path_query,
        local_file_path=local_file_path,
        file_size=file_size,
        elapsed_time=elapsed_time,
        status_code=response.status_code,
        response_text=response.text if response.status_code != 200 else None
    )

    return local_file_path, report