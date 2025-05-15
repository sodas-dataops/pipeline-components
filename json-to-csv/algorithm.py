import json
import csv
import re
import time
import pandas as pd
import os
from datetime import datetime

def clean_text(text):
    """텍스트에서 불필요한 공백을 제거합니다."""
    if not isinstance(text, str):
        return text
    return re.sub(r'\s+', ' ', text.strip())

def flatten_json(nested_json, parent_key='', sep='_'):
    """중첩된 JSON 구조를 평탄화합니다."""
    items = []
    for k, v in nested_json.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_json(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # 리스트는 문자열로 변환
            items.append((new_key, str(v)))
        elif v is None:
            items.append((new_key, ''))
        else:
            items.append((new_key, clean_text(str(v))))
    return dict(items)

def generate_report(json_data: list, csv_data: pd.DataFrame, input_filename: str, output_filename: str, 
                  json_size: int, csv_size: int, elapsed_time: float) -> str:
    """
    작업 보고서를 생성하는 함수.
    
    Parameters:
    - json_data (list): 입력 JSON 데이터
    - csv_data (pd.DataFrame): 변환된 CSV 데이터
    - input_filename (str): 입력 파일 경로
    - output_filename (str): 출력 파일 경로
    - json_size (int): JSON 데이터 크기 (bytes)
    - csv_size (int): CSV 데이터 크기 (bytes)
    - elapsed_time (float): 소요 시간 (초)
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    report = f"""# JSON to CSV 변환 작업 보고서

## 1. 작업 개요
- **작업 유형**: JSON 리스트를 CSV로 변환
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **입력 파일**: {input_filename}
- **데이터 크기**: {json_size / 1024:.2f} KB
- **데이터 구조**: 
```json
{json.dumps(json_data[0] if json_data else {}, indent=2, ensure_ascii=False)}
```

## 3. 변환 결과
- **출력 파일**: {output_filename}
- **파일 크기**: {csv_size / 1024:.2f} KB
- **행 수**: {len(csv_data)}
- **열 수**: {len(csv_data.columns)}
- **열 이름**: {', '.join(csv_data.columns)}

## 4. 성능 지표
- **처리 속도**: {json_size / elapsed_time / 1024:.2f} KB/s
- **압축률**: {(1 - csv_size / json_size) * 100:.2f}%
- **변환 효율**: {len(csv_data) / elapsed_time:.2f} 행/초

## 5. 작업 상태
- **상태**: 성공
- **변환 결과**: JSON 데이터가 성공적으로 CSV로 변환됨
"""
    return report

def solution(input_filename: str, output_filename: str):
    """
    JSON 파일을 CSV로 변환하는 함수.
    
    Parameters:
    - input_filename (str): 입력 JSON 파일 경로
    - output_filename (str): 출력 CSV 파일 경로
    
    Returns:
    - tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] JSON to CSV 변환 작업을 시작합니다.")
    
    # JSON 데이터 로드
    print("\n[1/3] JSON 파일을 로드합니다...")
    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        print(f"- JSON 데이터 로드 완료: {len(json_data)}개 항목")
    except Exception as e:
        raise ValueError(f"JSON 파일 로드 실패: {str(e)}")
    
    # JSON 데이터 크기 확인
    json_size = os.path.getsize(input_filename)
    print(f"- JSON 파일 크기: {json_size / 1024:.2f} KB")
    
    # DataFrame으로 변환
    print("\n[2/3] JSON을 DataFrame으로 변환합니다...")
    try:
        df = pd.DataFrame(json_data)
        print(f"- 변환 완료: {len(df)}행 x {len(df.columns)}열")
    except Exception as e:
        raise ValueError(f"DataFrame 변환 실패: {str(e)}")
    
    # CSV로 저장
    print("\n[3/3] DataFrame을 CSV로 저장합니다...")
    try:
        df.to_csv(output_filename, index=False, encoding='utf-8')
        print(f"- CSV 저장 완료: {output_filename}")
    except Exception as e:
        raise IOError(f"CSV 저장 실패: {str(e)}")
    
    # CSV 파일 크기 확인
    csv_size = os.path.getsize(output_filename)
    print(f"- CSV 파일 크기: {csv_size / 1024:.2f} KB")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\n[요약]")
    print(f"- 입력 파일: {input_filename}")
    print(f"- 출력 파일: {output_filename}")
    print(f"- 처리된 항목 수: {len(json_data)}")
    print(f"- 생성된 행 수: {len(df)}")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    
    # 보고서 생성
    report = generate_report(json_data, df, input_filename, output_filename, 
                           json_size, csv_size, elapsed_time)
    
    return output_filename, report