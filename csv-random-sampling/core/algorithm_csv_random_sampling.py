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
    랜덤 샘플링 작업 보고서를 생성하는 함수.
    
    Parameters:
    - input_data (pd.DataFrame): 입력 데이터
    - output_data (pd.DataFrame): 샘플링된 출력 데이터
    - output_filename (str): 출력 파일 경로
    - input_size (int): 입력 데이터 크기 (bytes)
    - output_size (int): 출력 데이터 크기 (bytes)
    - elapsed_time (float): 소요 시간 (초)
    - settings (dict): 샘플링 설정
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    sample_size = settings.get('sample_size', 0) if settings else 0
    sample_ratio = settings.get('sample_ratio', 0.1) if settings else 0.1
    random_state = settings.get('random_state', None) if settings else None
    sampling_method = settings.get('sampling_method', 'simple') if settings else 'simple'
    
    # 샘플링 방법별 설명
    method_description = {
        'simple': '단순 랜덤 샘플링 (Simple Random Sampling)',
        'systematic': '계통 샘플링 (Systematic Sampling)',
        'weighted': '가중 랜덤 샘플링 (Weighted Random Sampling)'
    }.get(sampling_method, '단순 랜덤 샘플링')
    
    # 가중치 컬럼 정보
    weight_column = settings.get('weight_column', '') if settings else ''
    weight_info = f"- **가중치 컬럼**: {weight_column}" if weight_column else ""
    
    report = f"""# CSV 랜덤 샘플링 작업 보고서

## 1. 작업 개요
- **작업 유형**: CSV 랜덤 샘플링 (Random Sampling)
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초
- **샘플링 방법**: {method_description}
- **샘플 크기**: {sample_size:,}개
- **샘플 비율**: {sample_ratio:.2%}
- **랜덤 시드**: {random_state if random_state else 'None'}
{weight_info}

## 2. 입력 데이터
- **데이터 크기**: {input_size / 1024:.2f} KB
- **행 수**: {len(input_data):,}
- **열 수**: {len(input_data.columns)}
- **열 이름**: {', '.join(input_data.columns)}

## 3. 샘플링 결과
- **출력 파일**: {output_filename}
- **파일 크기**: {output_size / 1024:.2f} KB
- **행 수**: {len(output_data):,}
- **열 수**: {len(output_data.columns)}
- **샘플링 비율**: {(len(output_data) / len(input_data) * 100):.2f}%

## 4. 성능 지표
- **처리 속도**: {len(input_data) / elapsed_time:.2f} 행/초
- **압축률**: {(1 - output_size / input_size) * 100:.2f}%
- **데이터 보존률**: {len(output_data) / len(input_data) * 100:.2f}%

## 5. 작업 상태
- **상태**: 성공
- **샘플링 결과**: 랜덤 샘플링이 성공적으로 완료됨
- **데이터 무결성**: 원본 데이터의 무작위성 유지
"""
    return report

def solution(input_data: StringIO, output_filename: str, settings: dict = None):
    """
    CSV 데이터에 랜덤 샘플링을 적용하는 함수.
    
    Parameters:
    - input_data (StringIO): 입력 CSV 데이터
    - output_filename (str): 출력 CSV 파일 경로
    - settings (dict): 샘플링 설정
        - sample_size (int): 샘플 크기 (0이면 비율 사용)
        - sample_ratio (float): 샘플 비율 (0.0 ~ 1.0)
        - random_state (int): 랜덤 시드
        - sampling_method (str): 샘플링 방법 ('simple', 'systematic', 'weighted')
        - weight_column (str): 가중치 컬럼명 (weighted 샘플링 시)
        - replace (bool): 복원 추출 여부 (기본값: False)
    
    Returns:
    - tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] CSV 랜덤 샘플링 작업을 시작합니다.")
    
    # 설정 기본값 설정
    if settings is None:
        settings = {}
    
    sample_size = settings.get('sample_size', 0)
    sample_ratio = settings.get('sample_ratio', 0.1)
    random_state = settings.get('random_state', None)
    sampling_method = settings.get('sampling_method', 'simple')
    weight_column = settings.get('weight_column', '')
    replace = settings.get('replace', False)
    
    print(f"- 샘플링 방법: {sampling_method}")
    print(f"- 샘플 크기: {sample_size:,}개" if sample_size > 0 else f"- 샘플 비율: {sample_ratio:.2%}")
    print(f"- 랜덤 시드: {random_state}")
    print(f"- 복원 추출: {'예' if replace else '아니오'}")
    if weight_column:
        print(f"- 가중치 컬럼: {weight_column}")
    
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
    
    # 샘플링 크기 결정
    if sample_size > 0:
        if sample_size >= len(df) and not replace:
            print(f"- 경고: 요청된 샘플 크기({sample_size:,})가 전체 데이터 크기({len(df):,})보다 크거나 같습니다.")
            print(f"- 복원 추출이 비활성화되어 있으므로 전체 데이터를 반환합니다.")
            sample_ratio = 1.0
        else:
            sample_ratio = sample_size / len(df)
    
    # 가중치 컬럼 검증 (weighted 샘플링인 경우)
    if sampling_method == 'weighted':
        if not weight_column:
            raise ValueError("가중치 샘플링을 위해서는 weight_column이 필요합니다.")
        
        if weight_column not in df.columns:
            raise ValueError(f"가중치 컬럼 '{weight_column}'이 데이터에 존재하지 않습니다.")
        
        # 가중치 값 검증
        weights = df[weight_column]
        if weights.isna().any():
            print(f"- 경고: 가중치 컬럼에 결측값이 있습니다. 결측값을 0으로 처리합니다.")
            weights = weights.fillna(0)
        
        if (weights < 0).any():
            raise ValueError("가중치 값은 0 이상이어야 합니다.")
        
        if weights.sum() == 0:
            raise ValueError("가중치의 합이 0입니다.")
        
        print(f"- 가중치 통계: 최소={weights.min():.3f}, 최대={weights.max():.3f}, 평균={weights.mean():.3f}")
    
    print(f"\n[2/4] 샘플링을 수행합니다...")
    print(f"- 실제 샘플 비율: {sample_ratio:.2%}")
    
    try:
        # 샘플링 방법에 따른 처리
        if sampling_method == 'simple':
            # 단순 랜덤 샘플링
            print("- 단순 랜덤 샘플링 수행")
            if sample_size > 0:
                sampled_df = df.sample(n=sample_size, random_state=random_state, replace=replace)
            else:
                sampled_df = df.sample(frac=sample_ratio, random_state=random_state, replace=replace)
        
        elif sampling_method == 'systematic':
            # 계통 샘플링
            print("- 계통 샘플링 수행")
            n = len(df)
            if sample_size > 0:
                k = n // sample_size
            else:
                k = int(1 / sample_ratio)
            
            if k < 1:
                k = 1
            
            # 시작점 랜덤 선택
            if random_state is not None:
                np.random.seed(random_state)
            start = np.random.randint(0, k)
            
            # 계통 샘플링 인덱스 생성
            indices = list(range(start, n, k))
            sampled_df = df.iloc[indices].copy()
            
            print(f"- 샘플링 간격: {k}, 시작점: {start}, 선택된 인덱스 수: {len(indices)}")
        
        elif sampling_method == 'weighted':
            # 가중치 랜덤 샘플링
            print("- 가중치 랜덤 샘플링 수행")
            weights = df[weight_column].fillna(0)
            
            if sample_size > 0:
                sampled_df = df.sample(n=sample_size, weights=weights, random_state=random_state, replace=replace)
            else:
                sampled_df = df.sample(frac=sample_ratio, weights=weights, random_state=random_state, replace=replace)
        
        else:
            raise ValueError(f"지원하지 않는 샘플링 방법: {sampling_method}")
        
        print(f"- 샘플링 완료: {len(sampled_df):,}행")
        
    except Exception as e:
        raise ValueError(f"랜덤 샘플링 실패: {str(e)}")
    
    # 샘플링 결과 검증
    print(f"\n[3/4] 샘플링 결과를 검증합니다...")
    
    # 기본 통계 비교
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    if len(numeric_columns) > 0:
        print("- 수치형 컬럼 통계 비교:")
        for col in numeric_columns[:3]:  # 처음 3개 컬럼만 비교
            original_mean = df[col].mean()
            sampled_mean = sampled_df[col].mean()
            diff_pct = abs(original_mean - sampled_mean) / original_mean * 100 if original_mean != 0 else 0
            print(f"  - {col}: 원본={original_mean:.3f}, 샘플={sampled_mean:.3f}, 차이={diff_pct:.1f}%")
    
    # 범주형 컬럼 분포 비교
    categorical_columns = df.select_dtypes(include=['object', 'category']).columns
    if len(categorical_columns) > 0:
        print("- 범주형 컬럼 분포 비교:")
        for col in categorical_columns[:2]:  # 처음 2개 컬럼만 비교
            original_dist = df[col].value_counts(normalize=True).head(3)
            sampled_dist = sampled_df[col].value_counts(normalize=True).head(3)
            print(f"  - {col}: 원본 상위3={dict(original_dist)}, 샘플 상위3={dict(sampled_dist)}")
    
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
    print(f"- 원본 데이터: {len(df):,}행")
    print(f"- 샘플링된 데이터: {len(sampled_df):,}행")
    print(f"- 샘플링 비율: {len(sampled_df) / len(df):.2%}")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    
    # 보고서 생성
    report = generate_report(df, sampled_df, output_filename, 
                           input_size, output_size, elapsed_time, settings)
    
    return output_filename, report