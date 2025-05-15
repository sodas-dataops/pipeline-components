from io import StringIO
import pandas as pd
import re
import time
from datetime import datetime

def generate_report(
    df: pd.DataFrame,
    target_column: str,
    regex_pattern: str,
    output_column: str,
    input_filename: str,
    output_filename: str,
    elapsed_time: float,
    total_rows: int,
    matched_rows: int
) -> str:
    """
    정규식 처리 작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - target_column (str): 대상 컬럼명
    - regex_pattern (str): 적용된 정규식 패턴
    - output_column (str): 출력 컬럼명
    - input_filename (str): 입력 파일 경로
    - output_filename (str): 출력 파일 경로
    - elapsed_time (float): 소요 시간 (초)
    - total_rows (int): 총 처리된 행 수
    - matched_rows (int): 정규식 매칭된 행 수
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    report = f"""# CSV 정규식 처리 작업 보고서

## 1. 작업 개요
- **작업 유형**: CSV 정규식 처리
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **입력 파일**: {input_filename}
- **행 수**: {total_rows:,}행
- **컬럼 수**: {len(df.columns)}개
- **컬럼 목록**: {', '.join(df.columns)}

## 3. 정규식 설정
- **대상 컬럼**: {target_column}
- **정규식 패턴**: `{regex_pattern}`
- **출력 컬럼**: {output_column}

## 4. 처리 결과
- **출력 파일**: {output_filename}
- **총 처리 행**: {total_rows:,}행
- **매칭된 행**: {matched_rows:,}행 ({matched_rows/total_rows*100:.1f}%)
- **매칭 실패 행**: {total_rows - matched_rows:,}행 ({(total_rows - matched_rows)/total_rows*100:.1f}%)

## 5. 성능 지표
- **처리 속도**: {total_rows / elapsed_time:.2f} 행/초
- **메모리 사용량**: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB

## 6. 작업 상태
- **상태**: 성공
- **처리 결과**: 정규식이 성공적으로 적용됨
"""
    return report

def solution(input_data: StringIO, target_column: str, regex_pattern: str, output_column: str, output_csv_path: str) -> tuple:
    """
    CSV 데이터에서 특정 컬럼에 regex를 적용해 새로운 컬럼 생성.

    Parameters:
    - input_data: CSV 데이터 (StringIO 객체).
    - target_column: regex를 적용할 컬럼명.
    - regex_pattern: 적용할 정규식 패턴.
    - output_column: 생성할 새로운 컬럼명.
    - output_csv_path: 저장할 CSV 파일 경로.
    
    Returns:
    - tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    
    try:
        # CSV 데이터 로드
        df = pd.read_csv(input_data)

        # 정규식 적용
        def apply_regex(value):
            if pd.isna(value):
                return None
            match = re.search(regex_pattern, str(value))
            return match.group(0) if match else None

        df[output_column] = df[target_column].apply(apply_regex)

        # 결과 저장
        df.to_csv(output_csv_path, index=False)
        print(f"Regex applied and data saved to {output_csv_path}")
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # 매칭된 행 수 계산
        matched_rows = df[output_column].notna().sum()
        
        # 보고서 생성
        report = generate_report(
            df=df,
            target_column=target_column,
            regex_pattern=regex_pattern,
            output_column=output_column,
            input_filename=input_data.name if hasattr(input_data, 'name') else str(input_data),
            output_filename=output_csv_path,
            elapsed_time=elapsed_time,
            total_rows=len(df),
            matched_rows=matched_rows
        )
        
        return output_csv_path, report
        
    except Exception as e:
        print(f"Failed to process CSV data: {e}")
        raise
