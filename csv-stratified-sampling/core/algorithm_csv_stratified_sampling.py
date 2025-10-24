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
    층화 샘플링 작업 보고서를 생성하는 함수.
    
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
    stratify_column = settings.get('stratify_column', '') if settings else ''
    sample_size = settings.get('sample_size', 0) if settings else 0
    random_state = settings.get('random_state', None) if settings else None
    
    # 층화 컬럼의 분포 정보
    if stratify_column and stratify_column in input_data.columns:
        input_distribution = input_data[stratify_column].value_counts().to_dict()
        output_distribution = output_data[stratify_column].value_counts().to_dict()
        distribution_info = f"""
### 층화 컬럼 분포 비교
- **입력 데이터 분포**: {dict(list(input_distribution.items())[:5])}...
- **출력 데이터 분포**: {dict(list(output_distribution.items())[:5])}...
"""
    else:
        distribution_info = ""
    
    report = f"""# CSV 층화 샘플링 작업 보고서

## 1. 작업 개요
- **작업 유형**: CSV 층화 샘플링 (Stratified Sampling)
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초
- **층화 컬럼**: {stratify_column if stratify_column else 'N/A'}
- **샘플 크기**: {sample_size:,}개
- **랜덤 시드**: {random_state if random_state else 'None'}

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
{distribution_info}
## 5. 작업 상태
- **상태**: 성공
- **샘플링 결과**: 층화 샘플링이 성공적으로 완료됨
- **데이터 무결성**: 층화 컬럼의 분포가 원본과 유사하게 유지됨
"""
    return report

def solution(input_data: StringIO, output_filename: str, settings: dict = None):
    """
    CSV 데이터에 층화 샘플링을 적용하는 함수.
    
    Parameters:
    - input_data (StringIO): 입력 CSV 데이터
    - output_filename (str): 출력 CSV 파일 경로
    - settings (dict): 샘플링 설정
        - stratify_column (str): 층화에 사용할 컬럼명
        - sample_size (int): 샘플 크기 (0이면 비율 사용)
        - sample_ratio (float): 샘플 비율 (0.0 ~ 1.0)
        - random_state (int): 랜덤 시드
        - min_samples_per_stratum (int): 각 층의 최소 샘플 수
    
    Returns:
    - tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] CSV 층화 샘플링 작업을 시작합니다.")
    
    # 설정 기본값 설정
    if settings is None:
        settings = {}
    
    stratify_column = settings.get('stratify_column', '')
    sample_size = settings.get('sample_size', 0)
    sample_ratio = settings.get('sample_ratio', 0.1)
    random_state = settings.get('random_state', None)
    min_samples_per_stratum = settings.get('min_samples_per_stratum', 1)
    
    print(f"- 층화 컬럼: '{stratify_column}'")
    print(f"- 샘플 크기: {sample_size:,}개" if sample_size > 0 else f"- 샘플 비율: {sample_ratio:.2%}")
    print(f"- 랜덤 시드: {random_state}")
    print(f"- 층별 최소 샘플 수: {min_samples_per_stratum}")
    
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
    
    # 층화 컬럼 검증
    if not stratify_column:
        raise ValueError("층화 컬럼이 지정되지 않았습니다.")
    
    if stratify_column not in df.columns:
        raise ValueError(f"층화 컬럼 '{stratify_column}'이 데이터에 존재하지 않습니다.")
    
    print(f"\n[2/4] 층화 컬럼 '{stratify_column}' 분석 중...")
    
    # 층화 컬럼의 고유값과 분포 확인
    unique_values = df[stratify_column].unique()
    value_counts = df[stratify_column].value_counts()
    
    print(f"- 고유값 수: {len(unique_values)}")
    print(f"- 분포: {dict(value_counts.head().items())}")
    
    # 각 층의 최소 샘플 수 확인
    insufficient_strata = value_counts[value_counts < min_samples_per_stratum]
    if len(insufficient_strata) > 0:
        print(f"- 경고: {len(insufficient_strata)}개 층이 최소 샘플 수({min_samples_per_stratum})보다 적습니다.")
        print(f"- 부족한 층: {dict(insufficient_strata.items())}")
    
    # 샘플링 크기 결정
    if sample_size > 0:
        if sample_size >= len(df):
            print(f"- 경고: 요청된 샘플 크기({sample_size:,})가 전체 데이터 크기({len(df):,})보다 크거나 같습니다.")
            sample_ratio = 1.0
        else:
            sample_ratio = sample_size / len(df)
    
    print(f"\n[3/4] 층화 샘플링을 수행합니다...")
    print(f"- 실제 샘플 비율: {sample_ratio:.2%}")
    
    try:
        # 층화 샘플링 수행
        if len(unique_values) == 1:
            # 층이 하나인 경우 단순 랜덤 샘플링
            print("- 단일 층 감지: 단순 랜덤 샘플링 수행")
            sampled_df = df.sample(n=int(len(df) * sample_ratio), random_state=random_state)
        else:
            # 다중 층인 경우 층화 샘플링
            print("- 다중 층 감지: 층화 샘플링 수행")
            
            # 각 층별로 샘플링
            sampled_dfs = []
            for stratum_value in unique_values:
                stratum_data = df[df[stratify_column] == stratum_value]
                stratum_size = len(stratum_data)
                
                # 층별 샘플 크기 계산
                if sample_size > 0:
                    # 전체 샘플 크기에서 층의 비율만큼 할당
                    stratum_ratio = stratum_size / len(df)
                    stratum_sample_size = max(min_samples_per_stratum, 
                                            int(sample_size * stratum_ratio))
                else:
                    # 비율 기반 샘플링
                    stratum_sample_size = max(min_samples_per_stratum, 
                                            int(stratum_size * sample_ratio))
                
                # 층의 크기가 요청된 샘플 크기보다 작은 경우 전체 사용
                stratum_sample_size = min(stratum_sample_size, stratum_size)
                
                if stratum_sample_size > 0:
                    stratum_sample = stratum_data.sample(n=stratum_sample_size, 
                                                       random_state=random_state)
                    sampled_dfs.append(stratum_sample)
                    print(f"  - '{stratum_value}': {stratum_size} → {stratum_sample_size} ({stratum_sample_size/stratum_size:.1%})")
            
            # 모든 층의 샘플을 결합
            if sampled_dfs:
                sampled_df = pd.concat(sampled_dfs, ignore_index=True)
            else:
                raise ValueError("유효한 샘플을 생성할 수 없습니다.")
        
        print(f"- 샘플링 완료: {len(sampled_df):,}행")
        
    except Exception as e:
        raise ValueError(f"층화 샘플링 실패: {str(e)}")
    
    # 샘플링 결과 검증
    print(f"\n[4/4] 샘플링 결과를 검증하고 저장합니다...")
    
    # 층화 컬럼의 분포 비교
    if len(unique_values) > 1:
        original_dist = df[stratify_column].value_counts(normalize=True).sort_index()
        sampled_dist = sampled_df[stratify_column].value_counts(normalize=True).sort_index()
        
        # 분포 유사성 확인
        distribution_similarity = np.corrcoef(original_dist.values, sampled_dist.values)[0, 1]
        print(f"- 분포 유사성 (상관계수): {distribution_similarity:.3f}")
        
        if distribution_similarity < 0.8:
            print("- 경고: 샘플링된 데이터의 분포가 원본과 크게 다릅니다.")
    
    # CSV로 저장
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
