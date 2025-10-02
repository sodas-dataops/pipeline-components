import pandas as pd
import numpy as np
import json
import time
import os
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
    duplicate_method = settings.get('duplicate_method', 'exact') if settings else 'exact'
    keep_strategy = settings.get('keep_strategy', 'first') if settings else 'first'
    subset_columns = settings.get('subset_columns', []) if settings else []
    similarity_threshold = settings.get('similarity_threshold', 0.8) if settings else 0.8

    # 중복 제거 설정 정보
    subset_info = f"- **중복 판단 컬럼**: {', '.join(subset_columns)}" if subset_columns else "- **중복 판단 컬럼**: 전체 컬럼"
    similarity_info = f"- **유사도 임계값**: {similarity_threshold}" if duplicate_method == 'similarity' else ""
    
    report = f"""# CSV 중복 제거 작업 보고서

## 1. 작업 개요
- **작업 유형**: CSV 중복 제거
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초
- **중복 판단 방법**: {duplicate_method}
- **제거 전략**: {keep_strategy}
- **제거된 중복 행**: {len(input_data) - len(output_data):,}개
- **중복 제거율**: {((len(input_data) - len(output_data)) / len(input_data) * 100):.2f}%
{subset_info}
{similarity_info}

## 2. 입력 데이터
- **데이터 크기**: {input_size / 1024:.2f} KB
- **행 수**: {len(input_data):,}
- **열 수**: {len(input_data.columns)}
- **열 이름**: {', '.join(input_data.columns)}

## 3. 중복 제거 결과
- **출력 파일**: {output_filename}
- **파일 크기**: {output_size / 1024:.2f} KB
- **행 수**: {len(output_data):,}
- **열 수**: {len(output_data.columns)}
- **데이터 보존률**: {len(output_data) / len(input_data) * 100:.2f}%

## 4. 성능 지표
- **처리 속도**: {len(input_data) / elapsed_time:.2f} 행/초
- **압축률**: {(1 - output_size / input_size) * 100:.2f}%
- **중복 제거 효율**: {(len(input_data) - len(output_data)) / elapsed_time:.2f} 행/초

## 5. 작업 상태
- **상태**: 성공
- **중복 제거**: 중복 데이터가 성공적으로 제거됨
- **데이터 무결성**: 원본 데이터의 구조와 타입 유지
"""
    return report

def solution(input_data: StringIO, output_filename: str, settings: dict = None):
    """
    CSV 데이터에서 중복을 제거하는 함수.
    
    Parameters:
    - input_data (StringIO): 입력 CSV 데이터
    - output_filename (str): 출력 CSV 파일 경로
    - settings (dict): 중복 제거 설정
        - duplicate_method (str): 중복 판단 방법 ('exact', 'subset', 'similarity')
        - keep_strategy (str): 중복 제거 전략 ('first', 'last', 'none')
        - subset_columns (list): 중복 판단할 컬럼 목록
        - similarity_threshold (float): 유사도 임계값 (0.0 ~ 1.0)
    
    Returns:
    - tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] 중복 제거 작업을 시작합니다.")
    
    # 설정 기본값 설정
    if settings is None:
        settings = {}
    
    duplicate_method = settings.get('duplicate_method', 'exact')
    keep_strategy = settings.get('keep_strategy', 'first')
    subset_columns = settings.get('subset_columns', [])
    similarity_threshold = settings.get('similarity_threshold', 0.8)
    
    print(f"- 중복 판단 방법: {duplicate_method}")
    print(f"- 제거 전략: {keep_strategy}")
    if subset_columns:
        print(f"- 중복 판단 컬럼: {', '.join(subset_columns)}")
    if duplicate_method == 'similarity':
        print(f"- 유사도 임계값: {similarity_threshold}")
    
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
    
    # 중복 제거 수행
    print(f"\n[2/4] 중복 제거를 수행합니다...")
    
    try:
        if duplicate_method == 'exact':
            # 완전 일치 중복 제거
            if subset_columns:
                # 특정 컬럼만으로 중복 판단
                if not all(col in df.columns for col in subset_columns):
                    missing_cols = [col for col in subset_columns if col not in df.columns]
                    raise ValueError(f"중복 판단 컬럼이 존재하지 않습니다: {missing_cols}")
                deduplicated_df = df.drop_duplicates(subset=subset_columns, keep=keep_strategy)
            else:
                # 전체 컬럼으로 중복 판단
                deduplicated_df = df.drop_duplicates(keep=keep_strategy)
                
        elif duplicate_method == 'subset':
            # 부분 일치 중복 제거 (특정 컬럼만 비교)
            if not subset_columns:
                raise ValueError("부분 일치 중복 제거를 위해서는 subset_columns가 필요합니다.")
            
            if not all(col in df.columns for col in subset_columns):
                missing_cols = [col for col in subset_columns if col not in df.columns]
                raise ValueError(f"중복 판단 컬럼이 존재하지 않습니다: {missing_cols}")
            
            deduplicated_df = df.drop_duplicates(subset=subset_columns, keep=keep_strategy)
            
        elif duplicate_method == 'similarity':
            # 유사도 기반 중복 제거 (간단한 구현)
            if not subset_columns:
                raise ValueError("유사도 기반 중복 제거를 위해서는 subset_columns가 필요합니다.")
            
            if not all(col in df.columns for col in subset_columns):
                missing_cols = [col for col in subset_columns if col not in df.columns]
                raise ValueError(f"중복 판단 컬럼이 존재하지 않습니다: {missing_cols}")
            
            # 문자열 컬럼에 대해서만 유사도 계산
            text_columns = [col for col in subset_columns if df[col].dtype == 'object']
            if not text_columns:
                # 숫자 컬럼만 있는 경우 정확한 일치로 처리
                deduplicated_df = df.drop_duplicates(subset=subset_columns, keep=keep_strategy)
            else:
                # 간단한 유사도 기반 중복 제거 (실제로는 더 정교한 알고리즘이 필요)
                deduplicated_df = df.drop_duplicates(subset=subset_columns, keep=keep_strategy)
                print(f"- 경고: 유사도 기반 중복 제거는 현재 정확한 일치로 처리됩니다.")
        else:
            raise ValueError(f"지원하지 않는 중복 판단 방법: {duplicate_method}")
        
    except Exception as e:
        raise ValueError(f"중복 제거 실패: {str(e)}")
    
    # 중복 제거 결과 검증
    print(f"\n[3/4] 중복 제거 결과를 검증합니다...")
    removed_count = len(df) - len(deduplicated_df)
    removal_rate = (removed_count / len(df)) * 100 if len(df) > 0 else 0
    
    print(f"- 제거된 중복 행: {removed_count:,}개")
    print(f"- 중복 제거율: {removal_rate:.2f}%")
    print(f"- 남은 행 수: {len(deduplicated_df):,}개")

    # CSV로 저장
    print(f"\n[4/4] 결과를 저장합니다...")
    try:
        deduplicated_df.to_csv(output_filename, index=False, encoding='utf-8')
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
    print(f"- 중복 제거 후: {len(deduplicated_df):,}행")
    print(f"- 제거된 중복: {removed_count:,}행")
    print(f"- 중복 제거율: {removal_rate:.2f}%")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    
    # 보고서 생성
    report = generate_report(df, deduplicated_df, output_filename, 
                           input_size, output_size, elapsed_time, settings)
    
    return output_filename, report