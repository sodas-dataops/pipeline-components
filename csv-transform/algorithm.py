from io import StringIO
import pandas as pd
import time
from datetime import datetime

def generate_report(
    df: pd.DataFrame,
    target_column: str,
    transform_function_str: str,
    output_column: str,
    input_filename: str,
    output_filename: str,
    elapsed_time: float,
    transformed_rows: int,
    null_rows: int
) -> str:
    """
    CSV 변환 작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - target_column (str): 대상 컬럼명
    - transform_function_str (str): 적용된 람다 함수 문자열
    - output_column (str): 출력 컬럼명
    - input_filename (str): 입력 파일 경로
    - output_filename (str): 출력 파일 경로
    - elapsed_time (float): 소요 시간 (초)
    - transformed_rows (int): 변환된 행 수
    - null_rows (int): NULL 값이 된 행 수
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    report = f"""# CSV 변환 작업 보고서

## 1. 작업 개요
- **작업 유형**: CSV 컬럼 변환
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **입력 파일**: {input_filename}
- **행 수**: {len(df):,}행
- **컬럼 수**: {len(df.columns)}개
- **컬럼 목록**: {', '.join(df.columns)}

## 3. 변환 설정
- **대상 컬럼**: {target_column}
- **출력 컬럼**: {output_column}
- **변환 함수**: `{transform_function_str}`

## 4. 처리 결과
- **출력 파일**: {output_filename}
- **총 처리 행**: {len(df):,}행
- **변환된 행**: {transformed_rows:,}행 ({transformed_rows/len(df)*100:.1f}%)
- **NULL 값 행**: {null_rows:,}행 ({null_rows/len(df)*100:.1f}%)

## 5. 성능 지표
- **처리 속도**: {len(df) / elapsed_time:.2f} 행/초
- **메모리 사용량**: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB

## 6. 작업 상태
    Parameters:
    - input_data: CSV 데이터 (StringIO 객체).
    - target_column: 람다 함수를 적용할 컬럼명.
    - transform_function_str: 적용할 람다 함수 문자열.
    - output_column: 생성할 새로운 컬럼명.
    - output_csv_path: 저장할 CSV 파일 경로.
    """
    return report

def solution(input_data: StringIO, target_column: str, transform_function_str: str, output_column: str, output_csv_path: str) -> tuple:
    """
    CSV 데이터를 변환하고 보고서를 생성하는 함수.
    
    Parameters:
    - input_data: CSV 데이터 (StringIO 객체).
    - target_column: 람다 함수를 적용할 컬럼명.
    - transform_function_str: 적용할 람다 함수 문자열.
    - output_column: 생성할 새로운 컬럼명.
    - output_csv_path: 저장할 CSV 파일 경로.
    
    Returns:
    - tuple: (출력 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    
    try:
        # CSV 데이터 로드
        df = pd.read_csv(input_data)

        try:
            transform_function = eval(transform_function_str)
            if not callable(transform_function):
                raise ValueError(f"The provided lambda function is not callable: {transform_function_str}")
        except Exception as e:
            raise ValueError(f"Failed to parse lambda function: {e}")
        
        # 대상 컬럼을 문자열로 변환
        df[target_column] = df[target_column].fillna('').astype(str)

        # 람다 함수 적용
        df[output_column] = df[target_column].apply(transform_function)

        # 통계 계산
        transformed_rows = df[output_column].notna().sum()
        null_rows = df[output_column].isna().sum()

        # 결과 저장
        df.to_csv(output_csv_path, index=False)
        print(f"Lambda function applied and data saved to {output_csv_path}")

        # 소요 시간 계산
        end_time = time.time()
        elapsed_time = end_time - start_time

        # 보고서 생성
        report = generate_report(
            df=df,
            target_column=target_column,
            transform_function_str=transform_function_str,
            output_column=output_column,
            input_filename=input_data.name if hasattr(input_data, 'name') else 'input_data',
            output_filename=output_csv_path,
            elapsed_time=elapsed_time,
            transformed_rows=transformed_rows,
            null_rows=null_rows
        )

        return output_csv_path, report

    except Exception as e:
        print(f"Failed to process CSV data: {e}")
        raise
