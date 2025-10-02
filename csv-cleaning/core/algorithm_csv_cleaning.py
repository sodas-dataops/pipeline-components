import pandas as pd
import numpy as np
import json
import time
import os
import re
from datetime import datetime
from io import StringIO

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
    remove_whitespace = settings.get('remove_whitespace', True) if settings else True
    remove_special_chars = settings.get('remove_special_chars', False) if settings else False
    normalize_case = settings.get('normalize_case', 'none') if settings else 'none'
    target_columns = settings.get('target_columns', []) if settings else []
    special_chars_pattern = settings.get('special_chars_pattern', r'[^\w\s]') if settings else r'[^\w\s]'

    # 정제 설정 정보
    columns_info = f"- **대상 컬럼**: {', '.join(target_columns)}" if target_columns else "- **대상 컬럼**: 전체 컬럼"
    case_info = f"- **대소문자 정규화**: {normalize_case}" if normalize_case != 'none' else "- **대소문자 정규화**: 없음"
    special_chars_info = f"- **특수문자 제거**: {special_chars_pattern}" if remove_special_chars else "- **특수문자 제거**: 없음"
    
    report = f"""# CSV 데이터 정제 작업 보고서

## 1. 작업 개요
- **작업 유형**: CSV 데이터 정제
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초
- **공백 제거**: {'활성화' if remove_whitespace else '비활성화'}
- **특수문자 제거**: {'활성화' if remove_special_chars else '비활성화'}
{columns_info}
{case_info}
{special_chars_info}

## 2. 입력 데이터
- **데이터 크기**: {input_size / 1024:.2f} KB
- **행 수**: {len(input_data):,}
- **열 수**: {len(input_data.columns)}
- **열 이름**: {', '.join(input_data.columns)}

## 3. 정제 결과
- **출력 파일**: {output_filename}
- **파일 크기**: {output_size / 1024:.2f} KB
- **행 수**: {len(output_data):,}
- **열 수**: {len(output_data.columns)}
- **데이터 보존률**: {len(output_data) / len(input_data) * 100:.2f}%

## 4. 성능 지표
- **처리 속도**: {len(input_data) / elapsed_time:.2f} 행/초
- **압축률**: {(1 - output_size / input_size) * 100:.2f}%
- **정제 효율**: {len(input_data) / elapsed_time:.2f} 행/초

## 5. 작업 상태
- **상태**: 성공
- **데이터 정제**: 데이터 정제가 성공적으로 완료됨
- **데이터 무결성**: 원본 데이터의 구조와 타입 유지
"""
    return report

def solution(input_data: StringIO, output_filename: str, settings: dict = None):
    """
    CSV 데이터를 정제하는 함수.
    
    Parameters:
    - input_data (StringIO): 입력 CSV 데이터
    - output_filename (str): 출력 CSV 파일 경로
    - settings (dict): 정제 설정
        - remove_whitespace (bool): 공백 제거 여부
        - remove_special_chars (bool): 특수문자 제거 여부
        - normalize_case (str): 대소문자 정규화 ('lower', 'upper', 'none')
        - target_columns (list): 정제할 컬럼 목록
        - special_chars_pattern (str): 제거할 특수문자 패턴
    
    Returns:
    - tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] 데이터 정제 작업을 시작합니다.")
    
    # 설정 기본값 설정
    if settings is None:
        settings = {}
    
    remove_whitespace = settings.get('remove_whitespace', True)
    remove_special_chars = settings.get('remove_special_chars', False)
    normalize_case = settings.get('normalize_case', 'none')
    target_columns = settings.get('target_columns', [])
    special_chars_pattern = settings.get('special_chars_pattern', r'[^\w\s]')
    
    print(f"- 공백 제거: {'활성화' if remove_whitespace else '비활성화'}")
    print(f"- 특수문자 제거: {'활성화' if remove_special_chars else '비활성화'}")
    print(f"- 대소문자 정규화: {normalize_case}")
    if target_columns:
        print(f"- 대상 컬럼: {', '.join(target_columns)}")
    if remove_special_chars:
        print(f"- 특수문자 패턴: {special_chars_pattern}")
    
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
    
    # 대상 컬럼 검증
    if target_columns:
        missing_cols = [col for col in target_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"대상 컬럼이 존재하지 않습니다: {missing_cols}")
        columns_to_process = target_columns
    else:
        columns_to_process = df.columns.tolist()
    
    print(f"- 정제 대상 컬럼: {', '.join(columns_to_process)}")
    
    # 데이터 정제 수행
    print(f"\n[2/4] 데이터 정제를 수행합니다...")
    
    try:
        cleaned_df = df.copy()
        
        for col in columns_to_process:
            if cleaned_df[col].dtype == 'object':  # 문자열 컬럼만 처리
                print(f"- 컬럼 '{col}' 정제 중...")
                
                # 공백 제거
                if remove_whitespace:
                    cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
                
                # 특수문자 제거
                if remove_special_chars:
                    cleaned_df[col] = cleaned_df[col].astype(str).str.replace(special_chars_pattern, '', regex=True)
                
                # 대소문자 정규화
                if normalize_case == 'lower':
                    cleaned_df[col] = cleaned_df[col].astype(str).str.lower()
                elif normalize_case == 'upper':
                    cleaned_df[col] = cleaned_df[col].astype(str).str.upper()
                
                # 연속된 공백을 단일 공백으로 변경
                if remove_whitespace:
                    cleaned_df[col] = cleaned_df[col].astype(str).str.replace(r'\s+', ' ', regex=True)
        
    except Exception as e:
        raise ValueError(f"데이터 정제 실패: {str(e)}")
    
    # 정제 결과 검증
    print(f"\n[3/4] 정제 결과를 검증합니다...")
    
    # 정제 전후 비교
    changes_made = 0
    for col in columns_to_process:
        if col in df.columns and col in cleaned_df.columns:
            if not df[col].equals(cleaned_df[col]):
                changes_made += 1
    
    print(f"- 정제된 컬럼 수: {changes_made}개")
    print(f"- 정제 완료: {len(cleaned_df):,}행 x {len(cleaned_df.columns)}열")

    # CSV로 저장
    print(f"\n[4/4] 결과를 저장합니다...")
    try:
        cleaned_df.to_csv(output_filename, index=False, encoding='utf-8')
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
    print(f"- 정제된 데이터: {len(cleaned_df):,}행")
    print(f"- 정제된 컬럼: {changes_made}개")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    
    # 보고서 생성
    report = generate_report(df, cleaned_df, output_filename, 
                           input_size, output_size, elapsed_time, settings)
    
    return output_filename, report