from io import BytesIO
import pandas as pd
import time
from datetime import datetime

def generate_report(
    df: pd.DataFrame,
    input_filename: str,
    output_filename: str,
    elapsed_time: float
) -> str:
    """
    Parquet to CSV 변환 작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - input_filename (str): 입력 파일 경로
    - output_filename (str): 출력 파일 경로
    - elapsed_time (float): 소요 시간 (초)
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    report = f"""# Parquet to CSV 변환 작업 보고서

## 1. 작업 개요
- **작업 유형**: Parquet to CSV 변환
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **입력 파일**: {input_filename}
- **행 수**: {len(df):,}행
- **컬럼 수**: {len(df.columns)}개
- **컬럼 목록**: {', '.join(df.columns)}

## 3. 처리 결과
- **출력 파일**: {output_filename}
- **변환된 행 수**: {len(df):,}행
- **변환된 컬럼 수**: {len(df.columns)}개

## 4. 성능 지표
- **처리 속도**: {len(df) / elapsed_time:.2f} 행/초

## 5. 작업 상태
- **상태**: 성공
- **처리 결과**: Parquet 데이터가 성공적으로 CSV로 변환됨
"""
    return report

def solution(input_data: BytesIO, output_csv_path: str) -> tuple:
    """
    Parquet 데이터를 CSV로 변환하는 함수.

    Parameters:
    - input_data: BytesIO 객체로, Parquet 데이터.
    - output_csv_path: 변환된 CSV 파일의 저장 경로.
    
    Returns:
    - tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    
    try:
        # Parquet 데이터 읽기
        parquet_df = pd.read_parquet(input_data)

        # CSV 파일로 저장
        parquet_df.to_csv(output_csv_path, index=False)
        print(f"Parquet data successfully converted to CSV and saved to {output_csv_path}")
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # 보고서 생성
        report = generate_report(
            df=parquet_df,
            input_filename=input_data.name if hasattr(input_data, 'name') else str(input_data),
            output_filename=output_csv_path,
            elapsed_time=elapsed_time
        )
        
        return output_csv_path, report
        
    except Exception as e:
        print(f"Failed to process Parquet data: {e}")
        raise
