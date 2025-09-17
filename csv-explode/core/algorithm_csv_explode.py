from io import StringIO
import pandas as pd
import time
import json
import ast
import re
from datetime import datetime

def parse_list_data(value):
    """
    문자열을 리스트로 파싱하는 함수.
    JSON 형태, Python 리스트 형태, 구분자로 분리된 문자열을 지원.
    """
    if pd.isna(value) or value == '':
        return []
    
    value_str = str(value).strip()
    
    # 빈 문자열 처리
    if not value_str:
        return []
    
    # JSON 형태의 리스트 파싱 시도
    try:
        parsed = json.loads(value_str)
        if isinstance(parsed, list):
            return parsed
    except (json.JSONDecodeError, ValueError):
        pass
    
    # Python 리스트 형태 파싱 시도 (ast.literal_eval)
    try:
        parsed = ast.literal_eval(value_str)
        if isinstance(parsed, list):
            return parsed
    except (ValueError, SyntaxError):
        pass
    
    # 구분자로 분리된 문자열 처리 (쉼표, 세미콜론, 파이프 등)
    separators = [',', ';', '|', '\n', '\t']
    for sep in separators:
        if sep in value_str:
            items = [item.strip() for item in value_str.split(sep) if item.strip()]
            if len(items) > 1:
                return items
    
    # 단일 값인 경우 리스트로 반환
    return [value_str]

def parse_json_data(value):
    """
    JSON 객체를 파싱하여 키-값 쌍의 리스트로 변환하는 함수.
    """
    if pd.isna(value) or value == '':
        return []
    
    value_str = str(value).strip()
    
    try:
        parsed = json.loads(value_str)
        if isinstance(parsed, dict):
            return [(k, v) for k, v in parsed.items()]
    except (json.JSONDecodeError, ValueError):
        pass
    
    return []

def parse_delimited_data(value, delimiter=','):
    """
    구분자로 분리된 데이터를 파싱하는 함수.
    """
    if pd.isna(value) or value == '':
        return []
    
    value_str = str(value).strip()
    items = [item.strip() for item in value_str.split(delimiter) if item.strip()]
    return items

def explode_dataframe(df, target_column, column_type, output_column):
    """
    DataFrame을 explode하는 함수.
    """
    exploded_rows = []
    
    for idx, row in df.iterrows():
        original_row = row.to_dict()
        target_value = original_row[target_column]
        
        # 컬럼 타입에 따라 데이터 파싱
        if column_type == 'list':
            parsed_data = parse_list_data(target_value)
        elif column_type == 'json':
            parsed_data = parse_json_data(target_value)
        elif column_type == 'delimited':
            delimiter = ','  # 기본 구분자, 필요시 파라미터로 받을 수 있음
            parsed_data = parse_delimited_data(target_value, delimiter)
        else:
            # 기본적으로 리스트로 처리
            parsed_data = parse_list_data(target_value)
        
        # 파싱된 데이터가 없으면 원본 행 유지 (빈 값으로)
        if not parsed_data:
            new_row = original_row.copy()
            new_row[output_column] = ''
            exploded_rows.append(new_row)
        else:
            # 각 파싱된 항목에 대해 새로운 행 생성
            for item in parsed_data:
                new_row = original_row.copy()
                if column_type == 'json' and isinstance(item, tuple):
                    # JSON의 경우 키-값 쌍을 처리
                    new_row[output_column] = f"{item[0]}: {item[1]}"
                else:
                    new_row[output_column] = str(item)
                exploded_rows.append(new_row)
    
    return pd.DataFrame(exploded_rows)

def generate_report(
    df: pd.DataFrame,
    target_column: str,
    column_type: str,
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
    - column_type (str): 컬럼 타입
    - output_column (str): 출력 컬럼명
    - input_filename (str): 입력 파일 경로
    - output_filename (str): 출력 파일 경로
    - elapsed_time (float): 소요 시간 (초)
    - transformed_rows (int): 변환된 행 수
    - null_rows (int): NULL 값이 된 행 수
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    report = f"""# CSV Explode 작업 보고서

## 1. 작업 개요
- **작업 유형**: CSV 데이터 Explode (분해/확장)
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **입력 파일**: {input_filename}
- **원본 행 수**: {len(df):,}행
- **컬럼 수**: {len(df.columns)}개
- **컬럼 목록**: {', '.join(df.columns)}

## 3. Explode 설정
- **대상 컬럼**: {target_column}
- **출력 컬럼**: {output_column}
- **데이터 타입**: `{column_type}`

## 4. 처리 결과
- **출력 파일**: {output_filename}
- **최종 행 수**: {len(df):,}행
- **변환된 행**: {transformed_rows:,}행
- **NULL 값 행**: {null_rows:,}행 ({null_rows/len(df)*100:.1f}%)

## 5. 성능 지표
- **처리 속도**: {len(df) / elapsed_time:.2f} 행/초
- **메모리 사용량**: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB

## 6. 작업 상태
**성공적으로 완료됨**
- 데이터가 성공적으로 explode되어 저장되었습니다.
- 새로운 컬럼 '{output_column}'이 생성되었습니다.
"""
    return report

def solution(input_data: StringIO, target_column: str, column_type: str, output_column: str, output_csv_path: str) -> tuple:
    """
    CSV 데이터를 explode하고 보고서를 생성하는 함수.
    
    Parameters:
    - input_data: CSV 데이터 (StringIO 객체).
    - target_column: explode할 대상 컬럼명.
    - column_type: 데이터 타입 ('list', 'json', 'delimited' 등).
    - output_column: 생성할 새로운 컬럼명.
    - output_csv_path: 저장할 CSV 파일 경로.
    
    Returns:
    - tuple: (출력 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    
    try:
        # CSV 데이터 로드
        df = pd.read_csv(input_data)
        original_row_count = len(df)
        
        # 대상 컬럼 존재 확인
        if target_column not in df.columns:
            raise ValueError(f"Target column '{target_column}' not found in CSV data")
        
        # 대상 컬럼을 문자열로 변환 (NaN 값 처리)
        df[target_column] = df[target_column].fillna('').astype(str)

        # explode 실행
        exploded_df = explode_dataframe(df, target_column, column_type, output_column)
        
        # 통계 계산
        transformed_rows = len(exploded_df)
        null_rows = exploded_df[output_column].isna().sum()

        # 결과 저장
        exploded_df.to_csv(output_csv_path, index=False)
        print(f"Data exploded and saved to {output_csv_path}")
        print(f"Original rows: {original_row_count}, Exploded rows: {transformed_rows}")

        # 소요 시간 계산
        end_time = time.time()
        elapsed_time = end_time - start_time

        # 보고서 생성
        report = generate_report(
            df=exploded_df,
            target_column=target_column,
            column_type=column_type,
            output_column=output_column,
            input_filename=input_data.name if hasattr(input_data, 'name') else 'input_data',
            output_filename=output_csv_path,
            elapsed_time=elapsed_time,
            transformed_rows=transformed_rows,
            null_rows=null_rows
        )

        return output_csv_path, report

    except (KeyError, UnicodeDecodeError, ValueError) as e:
        print(f"Failed to process CSV data: {e}")
        raise
