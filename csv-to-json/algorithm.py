import pandas as pd
import json
import time
from datetime import datetime

def generate_report(
    df: pd.DataFrame,
    json_data: list,
    input_filename: str,
    output_filename: str,
    elapsed_time: float
) -> str:
    """
    CSV to JSON 변환 작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 입력 DataFrame
    - json_data (list): 변환된 JSON 데이터
    - input_filename (str): 입력 파일 경로
    - output_filename (str): 출력 파일 경로
    - elapsed_time (float): 소요 시간 (초)
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    report = f"""# CSV to JSON 변환 작업 보고서

## 1. 작업 개요
- **작업 유형**: CSV to JSON 변환
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **입력 파일**: {input_filename}
- **행 수**: {len(df):,}행
- **컬럼 수**: {len(df.columns)}개
- **컬럼 목록**: {', '.join(df.columns)}

## 3. 변환 결과
- **출력 파일**: {output_filename}
- **JSON 레코드 수**: {len(json_data):,}개
- **JSON 키 수**: {len(df.columns)}개
- **JSON 키 목록**: {', '.join(df.columns)}

## 4. 성능 지표
- **처리 속도**: {len(df) / elapsed_time:.2f} 행/초
- **메모리 사용량**: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB

## 5. 작업 상태
- **상태**: 성공
- **처리 결과**: CSV 파일이 성공적으로 JSON으로 변환됨
"""
    return report

def solution(input_data: object, output_file: str) -> tuple:
    """
    CSV 파일을 JSON 파일로 변환하여 저장하는 함수.

    Parameters:
    - input_data: CSV 데이터 (파일 경로 또는 Pandas DataFrame)
    - output_file: 저장할 JSON 파일 경로
    
    Returns:
    - tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    
    # CSV 데이터 로드
    data = pd.read_csv(input_data)

    # JSON으로 변환
    json_data = data.to_dict(orient='records')

    # JSON 파일 저장
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)

    print(f'Converted JSON saved to {output_file}')
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 보고서 생성
    report = generate_report(
        df=data,
        json_data=json_data,
        input_filename=input_data.name if hasattr(input_data, 'name') else str(input_data),
        output_filename=output_file,
        elapsed_time=elapsed_time
    )
    
    return output_file, report