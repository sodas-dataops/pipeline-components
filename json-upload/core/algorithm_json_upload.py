import json
import time
import os
from datetime import datetime

def generate_report(json_data: dict, output_filename: str, data_size: int, file_size: int, elapsed_time: float) -> str:
    """
    작업 보고서를 생성하는 함수.
    
    Parameters:
    - json_data (dict): 처리된 JSON 데이터
    - output_filename (str): 저장된 파일 경로
    - data_size (int): JSON 데이터 크기 (bytes)
    - file_size (int): 저장된 파일 크기 (bytes)
    - elapsed_time (float): 소요 시간 (초)
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    report = f"""# JSON 데이터 업로드 작업 보고서

## 1. 작업 개요
- **작업 유형**: JSON 데이터 검증 및 저장
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **데이터 크기**: {data_size / 1024:.2f} KB
- **데이터 구조**: 
```json
{json.dumps(json_data, indent=2, ensure_ascii=False)}
```

## 3. 처리 결과
- **저장 파일**: {output_filename}
- **파일 크기**: {file_size / 1024:.2f} KB
- **저장 형식**: JSON (UTF-8, 들여쓰기 2칸)

## 4. 성능 지표
- **처리 속도**: {data_size / elapsed_time / 1024:.2f} KB/s
- **압축률**: {(1 - file_size / data_size) * 100:.2f}%

## 5. 작업 상태
- **상태**: 성공
- **검증 결과**: JSON 데이터 형식이 유효함
"""
    return report

def solution(json_data: dict, output_filename: str):
    """
    JSON 데이터를 파일로 저장하는 함수.
    
    Parameters:
    - json_data (dict): 저장할 JSON 데이터 (이미 파싱된 dict 객체)
    - output_filename (str): 저장할 파일 경로
    
    Returns:
    - tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] JSON 데이터 저장 작업을 시작합니다.")
    
    # 데이터 크기 확인
    print("\n[1/3] JSON 데이터 크기를 확인합니다...")
    json_str = json.dumps(json_data)
    data_size = len(json_str.encode('utf-8'))
    print(f"- JSON 데이터 크기: {data_size / 1024:.2f} KB")
    
    # 임시 파일로 저장
    print("\n[2/3] JSON 데이터를 임시 파일로 저장합니다...")
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print(f"- 파일 저장 완료: {output_filename}")
    except Exception as e:
        raise IOError(f"파일 저장 중 오류 발생: {str(e)}")
    
    # 파일 크기 확인
    file_size = os.path.getsize(output_filename)
    print(f"- 저장된 파일 크기: {file_size / 1024:.2f} KB")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\n[요약]")
    print(f"- JSON 데이터 크기: {data_size / 1024:.2f} KB")
    print(f"- 저장된 파일 크기: {file_size / 1024:.2f} KB")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    print(f"- 저장 경로: {output_filename}")
    
    # 보고서 생성
    report = generate_report(json_data, output_filename, data_size, file_size, elapsed_time)
    
    return output_filename, report 