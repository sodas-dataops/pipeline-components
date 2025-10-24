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
    sample_size = settings.get('sample_size', 0) if settings else 0
    sample_ratio = settings.get('sample_ratio', 0.1) if settings else 0.1
    random_state = settings.get('random_state', None) if settings else None
    sort_column = settings.get('sort_column', '') if settings else ''

    # 샘플링 정보
    sample_info = f"- **샘플 크기**: {sample_size:,}개" if sample_size > 0 else f"- **샘플 비율**: {sample_ratio:.2%}"
    random_info = f"- **랜덤 시드**: {random_state}" if random_state else "- **랜덤 시드**: None"
    sort_info = f"- **정렬 컬럼**: {sort_column}" if sort_column else "- **정렬 컬럼**: 인덱스 순서"
    
    report = f"""# 체계적 샘플링 작업 보고서

## 1. 작업 개요
- **작업 유형**: 체계적 샘플링
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초
- **샘플링된 데이터**: {len(output_data):,}개
- **샘플링 비율**: {len(output_data) / len(input_data) * 100:.2f}%
{sample_info}
{random_info}
{sort_info}

## 2. 입력 데이터
- **데이터 크기**: {input_size / 1024:.2f} KB
- **행 수**: {len(input_data):,}
- **열 수**: {len(input_data.columns)}
- **열 이름**: {', '.join(input_data.columns)}

## 3. 체계적 샘플링 결과
- **출력 파일**: {output_filename}
- **파일 크기**: {output_size / 1024:.2f} KB
- **행 수**: {len(output_data):,}
- **열 수**: {len(output_data.columns)}
- **샘플링 비율**: {len(output_data) / len(input_data) * 100:.2f}%

## 4. 성능 지표
- **처리 속도**: {len(input_data) / elapsed_time:.2f} 행/초
- **압축률**: {(1 - output_size / input_size) * 100:.2f}%
- **데이터 보존률**: {len(output_data) / len(input_data) * 100:.2f}%

## 5. 작업 상태
- **상태**: 성공
- **체계적 샘플링**: 체계적 샘플링이 성공적으로 완료됨
- **데이터 무결성**: 원본 데이터의 순서 유지
"""
    return report

def solution(input_data: StringIO, output_filename: str, settings: dict = None):
    """
    데이터에 체계적 샘플링을 적용하는 함수.
    
    Parameters:
    - input_data (StringIO): 입력 CSV 데이터
    - output_filename (str): 출력 CSV 파일 경로
    - settings (dict): 체계적 샘플링 설정
        - sample_size (int): 샘플 크기 (0이면 sample_ratio 사용)
        - sample_ratio (float): 샘플 비율 (0.0 ~ 1.0)
        - random_state (int): 랜덤 시드
        - sort_column (str): 정렬할 컬럼 이름
    
    Returns:
    - tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] 체계적 샘플링 작업을 시작합니다.")
    
    # 설정 기본값 설정
    if settings is None:
        settings = {}
    
    sample_size = settings.get('sample_size', 0)
    sample_ratio = settings.get('sample_ratio', 0.1)
    random_state = settings.get('random_state', None)
    sort_column = settings.get('sort_column', '')
    
    print(f"- 샘플 크기: {sample_size:,}개" if sample_size > 0 else f"- 샘플 비율: {sample_ratio:.2%}")
    print(f"- 랜덤 시드: {random_state}")
    print(f"- 정렬 컬럼: {sort_column if sort_column else '인덱스 순서'}")
    
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
    
    # 정렬 컬럼 검증
    if sort_column and sort_column not in df.columns:
        raise ValueError(f"지정된 정렬 컬럼 '{sort_column}'이 데이터에 존재하지 않습니다.")
    
    # 샘플 크기 결정
    if sample_size > 0:
        if sample_size >= len(df):
            print(f"- 경고: 요청된 샘플 크기({sample_size:,})가 전체 데이터 크기({len(df):,})보다 크거나 같습니다.")
            print(f"- 전체 데이터를 반환합니다.")
            sample_ratio = 1.0
        else:
            sample_ratio = sample_size / len(df)
    
    print(f"\n[2/4] 체계적 샘플링을 수행합니다...")
    print(f"- 실제 샘플 비율: {sample_ratio:.2%}")
    
    try:
        # 데이터 정렬 (선택사항)
        if sort_column:
            df_sorted = df.sort_values(by=sort_column).reset_index(drop=True)
            print(f"- {sort_column} 컬럼으로 정렬 완료")
        else:
            df_sorted = df.reset_index(drop=True)
            print(f"- 인덱스 순서로 정렬 완료")
        
        # 체계적 샘플링
        total_rows = len(df_sorted)
        sample_count = int(total_rows * sample_ratio)
        
        if sample_count == 0:
            print("- 경고: 샘플 크기가 0입니다. 최소 1개 샘플을 반환합니다.")
            sample_count = 1
        
        # 간격 계산
        if sample_count >= total_rows:
            # 전체 데이터 반환
            sampled_df = df_sorted
        else:
            # 체계적 샘플링 간격
            interval = total_rows / sample_count
            
            # 시작점 결정 (랜덤 시드가 있으면 사용)
            if random_state is not None:
                np.random.seed(random_state)
                start_point = np.random.randint(0, int(interval))
            else:
                start_point = 0
            
            # 체계적 샘플링 인덱스 생성
            sample_indices = []
            current_index = start_point
            
            while current_index < total_rows and len(sample_indices) < sample_count:
                sample_indices.append(int(current_index))
                current_index += interval
            
            # 샘플링된 데이터 추출
            sampled_df = df_sorted.iloc[sample_indices].reset_index(drop=True)
        
        print(f"- 체계적 샘플링 완료: {len(sampled_df):,}개 샘플 추출")
        
    except Exception as e:
        raise ValueError(f"체계적 샘플링 실패: {str(e)}")
    
    # 결과 검증
    print(f"\n[3/4] 결과를 검증합니다...")
    print(f"- 원본 컬럼 수: {len(df.columns)}")
    print(f"- 결과 컬럼 수: {len(sampled_df.columns)}")
    print(f"- 행 수 변화: {len(df):,} → {len(sampled_df):,}")
    print(f"- 샘플링 비율: {len(sampled_df) / len(df):.2%}")
    
    # CSV로 저장
    print(f"\n[4/4] 결과를 저장합니다...")
    try:
        sampled_df.to_csv(output_filename, index=False, encoding='utf-8')
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
    print(f"- 원본 데이터: {len(df):,}행 x {len(df.columns)}열")
    print(f"- 샘플링된 데이터: {len(sampled_df):,}행 x {len(sampled_df.columns)}열")
    print(f"- 샘플링 비율: {len(sampled_df) / len(df):.2%}")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    
    # 보고서 생성
    report = generate_report(df, sampled_df, output_filename, 
                           input_size, output_size, elapsed_time, settings)
    
    return output_filename, report