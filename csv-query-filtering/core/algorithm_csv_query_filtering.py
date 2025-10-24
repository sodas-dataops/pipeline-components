import pandas as pd
import numpy as np
import json
import time
import os
import re
from datetime import datetime
from io import StringIO
from typing import Dict, Any, List, Union, Optional

def generate_report(input_data: pd.DataFrame, output_data: pd.DataFrame, 
                   output_filename: str, 
                   input_size: int, output_size: int, elapsed_time: float, 
                   settings: dict = None) -> str:
    """
    작업 보고서를 생성하는 함수.
    
    Parameters:
    - input_data (pd.DataFrame): 입력 데이터
    - output_data (pd.DataFrame): 출력 데이터
    - output_filename (str): 출력 파일 경로
    - input_size (int): 입력 데이터 크기 (bytes)
    - output_size (int): 출력 데이터 크기 (bytes)
    - elapsed_time (float): 소요 시간 (초)
    - settings (dict): 설정
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    # 필터 조건 정보 추출
    filters = settings.get('filters', []) if settings else []
    filter_count = len(filters)
    filter_info = ""
    
    if filters:
        filter_info = "\n- **적용된 필터 조건**:"
        for i, filter_condition in enumerate(filters, 1):
            column = filter_condition.get('column', '')
            operator = filter_condition.get('operator', '')
            value = filter_condition.get('value', '')
            filter_info += f"\n  {i}. {column} {operator} {value}"
    
    report = f"""# CSV 쿼리 필터링 작업 보고서

## 1. 작업 개요
- **작업 유형**: CSV 쿼리 필터링
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초
- **필터 조건 수**: {filter_count}개{filter_info}

## 2. 입력 데이터
- **데이터 크기**: {input_size / 1024:.2f} KB
- **행 수**: {len(input_data):,}행
- **열 수**: {len(input_data.columns)}개
- **열 이름**: {', '.join(input_data.columns)}

## 3. 필터링 결과
- **출력 파일**: {output_filename}
- **파일 크기**: {output_size / 1024:.2f} KB
- **행 수**: {len(output_data):,}행
- **열 수**: {len(output_data.columns)}개
- **필터링 비율**: {(len(output_data) / len(input_data) * 100):.2f}%

## 4. 성능 지표
- **처리 속도**: {len(input_data) / elapsed_time:.2f} 행/초
- **압축률**: {(1 - output_size / input_size) * 100:.2f}%
- **데이터 보존률**: {len(output_data) / len(input_data) * 100:.2f}%

## 5. 작업 상태
- **상태**: 성공
- **결과**: 필터링이 성공적으로 완료됨
- **데이터 무결성**: 원본 데이터 구조 유지
"""
    return report

def apply_filter(df: pd.DataFrame, filter_condition: Dict[str, Any], case_sensitive: bool = True) -> pd.Series:
    """
    단일 필터 조건을 적용하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 입력 데이터프레임
    - filter_condition (dict): 필터 조건
        - column (str): 대상 컬럼명
        - operator (str): 연산자
        - value (any): 비교값
    - case_sensitive (bool): 대소문자 구분 여부 (문자열 연산자에만 적용)
    
    Returns:
    - pd.Series: 필터링 결과 (boolean mask)
    """
    column = filter_condition.get('column')
    operator = filter_condition.get('operator')
    value = filter_condition.get('value')
    
    if column not in df.columns:
        raise ValueError(f"컬럼 '{column}'이 데이터에 존재하지 않습니다.")
    
    # 컬럼 데이터 타입 확인 및 변환
    col_data = df[column]
    
    # 연산자별 필터링 로직
    if operator == 'eq' or operator == '==':
        if not case_sensitive and col_data.dtype == 'object':
            return col_data.astype(str).str.lower() == str(value).lower()
        return col_data == value
    elif operator == 'ne' or operator == '!=':
        if not case_sensitive and col_data.dtype == 'object':
            return col_data.astype(str).str.lower() != str(value).lower()
        return col_data != value
    elif operator == 'gt' or operator == '>':
        return col_data > value
    elif operator == 'ge' or operator == '>=':
        return col_data >= value
    elif operator == 'lt' or operator == '<':
        return col_data < value
    elif operator == 'le' or operator == '<=':
        return col_data <= value
    elif operator == 'in':
        if not isinstance(value, list):
            value = [value]
        if not case_sensitive and col_data.dtype == 'object':
            return col_data.astype(str).str.lower().isin([str(v).lower() for v in value])
        return col_data.isin(value)
    elif operator == 'not_in':
        if not isinstance(value, list):
            value = [value]
        if not case_sensitive and col_data.dtype == 'object':
            return ~col_data.astype(str).str.lower().isin([str(v).lower() for v in value])
        return ~col_data.isin(value)
    elif operator == 'contains':
        if case_sensitive:
            return col_data.astype(str).str.contains(str(value), na=False, regex=False)
        else:
            return col_data.astype(str).str.lower().str.contains(str(value).lower(), na=False, regex=False)
    elif operator == 'not_contains':
        if case_sensitive:
            return ~col_data.astype(str).str.contains(str(value), na=False, regex=False)
        else:
            return ~col_data.astype(str).str.lower().str.contains(str(value).lower(), na=False, regex=False)
    elif operator == 'regex':
        if case_sensitive:
            return col_data.astype(str).str.contains(str(value), na=False, regex=True)
        else:
            return col_data.astype(str).str.contains(str(value), na=False, regex=True, case=False)
    elif operator == 'starts_with':
        if case_sensitive:
            return col_data.astype(str).str.startswith(str(value), na=False)
        else:
            return col_data.astype(str).str.lower().str.startswith(str(value).lower(), na=False)
    elif operator == 'ends_with':
        if case_sensitive:
            return col_data.astype(str).str.endswith(str(value), na=False)
        else:
            return col_data.astype(str).str.lower().str.endswith(str(value).lower(), na=False)
    elif operator == 'is_null':
        return col_data.isnull()
    elif operator == 'is_not_null':
        return col_data.notnull()
    elif operator == 'between':
        if not isinstance(value, list) or len(value) != 2:
            raise ValueError("between 연산자는 [min, max] 형태의 리스트가 필요합니다.")
        return (col_data >= value[0]) & (col_data <= value[1])
    elif operator == 'not_between':
        if not isinstance(value, list) or len(value) != 2:
            raise ValueError("not_between 연산자는 [min, max] 형태의 리스트가 필요합니다.")
        return (col_data < value[0]) | (col_data > value[1])
    else:
        raise ValueError(f"지원하지 않는 연산자입니다: {operator}")

def solution(input_data: StringIO, output_filename: str, settings: dict = None):
    """
    CSV 데이터에 쿼리 필터링을 적용하는 함수.
    
    Parameters:
    - input_data (StringIO): 입력 CSV 데이터
    - output_filename (str): 출력 CSV 파일 경로
    - settings (dict): 필터링 설정
        - filters (list): 필터 조건 리스트
            - column (str): 대상 컬럼명
            - operator (str): 연산자 (eq, ne, gt, ge, lt, le, in, not_in, contains, not_contains, regex, starts_with, ends_with, is_null, is_not_null, between, not_between)
            - value (any): 비교값
        - logic (str): 필터 조건 결합 방식 ('AND' 또는 'OR', 기본값: 'AND')
        - case_sensitive (bool): 대소문자 구분 여부 (기본값: True)
    
    Returns:
    - tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] CSV 쿼리 필터링 작업을 시작합니다.")
    
    # 설정 기본값 설정
    if settings is None:
        settings = {}
    
    filters = settings.get('filters', [])
    logic = settings.get('logic', 'AND').upper()
    case_sensitive = settings.get('case_sensitive', True)
    
    if not filters:
        raise ValueError("필터 조건이 설정되지 않았습니다. 'filters' 파라미터를 확인해주세요.")
    
    print(f"- 필터 조건 수: {len(filters)}개")
    print(f"- 논리 연산: {logic}")
    print(f"- 대소문자 구분: {case_sensitive}")
    
    # CSV 데이터 로드
    print("\n[1/4] CSV 파일을 로드합니다...")
    try:
        df = pd.read_csv(input_data)
        print(f"- CSV 데이터 로드 완료: {len(df):,}행 x {len(df.columns)}열")
    except (ValueError, TypeError, pd.errors.EmptyDataError) as e:
        raise ValueError(f"CSV 파일 로드 실패: {str(e)}")
    
    # 입력 데이터 크기 확인
    input_size = len(df.to_csv().encode('utf-8'))
    print(f"- 입력 데이터 크기: {input_size / 1024:.2f} KB")
    
    # 필터 조건 검증
    print("\n[2/4] 필터 조건을 검증합니다...")
    for i, filter_condition in enumerate(filters, 1):
        column = filter_condition.get('column')
        operator = filter_condition.get('operator')
        value = filter_condition.get('value')
        
        if not column:
            raise ValueError(f"필터 {i}: 'column'이 설정되지 않았습니다.")
        if not operator:
            raise ValueError(f"필터 {i}: 'operator'가 설정되지 않았습니다.")
        
        print(f"- 필터 {i}: {column} {operator} {value}")
    
    # 필터링 수행
    print(f"\n[3/4] 필터링을 수행합니다...")
    try:
        # 각 필터 조건을 적용하여 boolean mask 생성
        filter_masks = []
        for i, filter_condition in enumerate(filters, 1):
            try:
                mask = apply_filter(df, filter_condition, case_sensitive)
                filter_masks.append(mask)
                print(f"- 필터 {i} 적용 완료: {mask.sum():,}개 행이 조건을 만족")
            except Exception as e:
                raise ValueError(f"필터 {i} 적용 실패: {str(e)}")
        
        # 논리 연산으로 필터 조건 결합
        if logic == 'AND':
            final_mask = filter_masks[0]
            for mask in filter_masks[1:]:
                final_mask = final_mask & mask
        elif logic == 'OR':
            final_mask = filter_masks[0]
            for mask in filter_masks[1:]:
                final_mask = final_mask | mask
        else:
            raise ValueError(f"지원하지 않는 논리 연산입니다: {logic}")
        
        # 필터링된 데이터 추출
        filtered_df = df[final_mask].copy()
        
        print(f"- 최종 필터링 결과: {len(filtered_df):,}행 (전체의 {len(filtered_df)/len(df)*100:.2f}%)")
        
    except Exception as e:
        raise ValueError(f"필터링 실패: {str(e)}")
    
    # CSV로 저장
    print(f"\n[4/4] 결과를 저장합니다...")
    try:
        filtered_df.to_csv(output_filename, index=False, encoding='utf-8')
        print(f"- CSV 저장 완료: {output_filename}")
    except (PermissionError, OSError, UnicodeEncodeError) as e:
        raise IOError(f"CSV 저장 실패: {str(e)}")
    
    # 출력 데이터 크기 확인
    output_size = os.path.getsize(output_filename)
    print(f"- 출력 데이터 크기: {output_size / 1024:.2f} KB")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\n[요약]")
    print(f"- 출력 파일: {output_filename}")
    print(f"- 원본 데이터: {len(df):,}행")
    print(f"- 필터링된 데이터: {len(filtered_df):,}행")
    print(f"- 필터링 비율: {len(filtered_df) / len(df):.2%}")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    
    # 보고서 생성
    report = generate_report(df, filtered_df, output_filename, 
                           input_size, output_size, elapsed_time, settings)
    
    return output_filename, report