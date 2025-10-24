import pandas as pd
import numpy as np
import json
import time
import os
from datetime import datetime
from io import StringIO
from sklearn.preprocessing import MinMaxScaler, RobustScaler, QuantileTransformer

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
    scaling_method = settings.get('scaling_method', 'min_max') if settings else 'min_max'
    target_columns = settings.get('target_columns', []) if settings else []
    feature_range = settings.get('feature_range', [0, 1]) if settings else [0, 1]
    quantile_range = settings.get('quantile_range', [0.25, 0.75]) if settings else [0.25, 0.75]

    # 스케일링 설정 정보
    columns_info = f"- **대상 컬럼**: {', '.join(target_columns)}" if target_columns else "- **대상 컬럼**: 전체 숫자형 컬럼"
    method_info = f"- **스케일링 방법**: {scaling_method}"
    range_info = f"- **특성 범위**: {feature_range}" if scaling_method == 'min_max' else ""
    quantile_info = f"- **분위수 범위**: {quantile_range}" if scaling_method == 'quantile' else ""
    
    report = f"""# CSV 데이터 스케일링 작업 보고서

## 1. 작업 개요
- **작업 유형**: CSV 데이터 스케일링
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초
- **스케일링된 컬럼**: {len(target_columns) if target_columns else '전체 숫자형 컬럼'}
{columns_info}
{method_info}
{range_info}
{quantile_info}

## 2. 입력 데이터
- **데이터 크기**: {input_size / 1024:.2f} KB
- **행 수**: {len(input_data):,}
- **열 수**: {len(input_data.columns)}
- **열 이름**: {', '.join(input_data.columns)}

## 3. 스케일링 결과
- **출력 파일**: {output_filename}
- **파일 크기**: {output_size / 1024:.2f} KB
- **행 수**: {len(output_data):,}
- **열 수**: {len(output_data.columns)}
- **데이터 보존률**: {len(output_data) / len(input_data) * 100:.2f}%

## 4. 성능 지표
- **처리 속도**: {len(input_data) / elapsed_time:.2f} 행/초
- **압축률**: {(1 - output_size / input_size) * 100:.2f}%
- **스케일링 효율**: {len(input_data) / elapsed_time:.2f} 행/초

## 5. 작업 상태
- **상태**: 성공
- **데이터 스케일링**: 데이터 스케일링이 성공적으로 완료됨
- **데이터 무결성**: 원본 데이터의 구조와 타입 유지
"""
    return report

def solution(input_data: StringIO, output_filename: str, settings: dict = None):
    """
    CSV 데이터를 스케일링하는 함수.
    
    Parameters:
    - input_data (StringIO): 입력 CSV 데이터
    - output_filename (str): 출력 CSV 파일 경로
    - settings (dict): 스케일링 설정
        - scaling_method (str): 스케일링 방법 ('min_max', 'robust', 'quantile')
        - target_columns (list): 스케일링할 컬럼 목록
        - feature_range (list): Min-Max 스케일링 범위 [min, max]
        - quantile_range (list): Quantile 스케일링 범위 [min, max]
    
    Returns:
    - tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] 데이터 스케일링 작업을 시작합니다.")
    
    # 설정 기본값 설정
    if settings is None:
        settings = {}
    
    scaling_method = settings.get('scaling_method', 'min_max')
    target_columns = settings.get('target_columns', [])
    feature_range = settings.get('feature_range', [0, 1])
    quantile_range = settings.get('quantile_range', [0.25, 0.75])
    
    print(f"- 스케일링 방법: {scaling_method}")
    if target_columns:
        print(f"- 대상 컬럼: {', '.join(target_columns)}")
    if scaling_method == 'min_max':
        print(f"- 특성 범위: {feature_range}")
    if scaling_method == 'quantile':
        print(f"- 분위수 범위: {quantile_range}")
    
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
    
    # 대상 컬럼 검증 및 선택
    if target_columns:
        missing_cols = [col for col in target_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"대상 컬럼이 존재하지 않습니다: {missing_cols}")
        columns_to_process = target_columns
    else:
        # 숫자형 컬럼만 선택
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        columns_to_process = numeric_columns
    
    if not columns_to_process:
        raise ValueError("스케일링할 숫자형 컬럼이 없습니다.")
    
    print(f"- 스케일링 대상 컬럼: {', '.join(columns_to_process)}")
    
    # 데이터 스케일링 수행
    print(f"\n[2/4] 데이터 스케일링을 수행합니다...")
    
    try:
        scaled_df = df.copy()
        
        # 결측값이 있는 경우 경고
        for col in columns_to_process:
            if scaled_df[col].isnull().any():
                print(f"- 경고: 컬럼 '{col}'에 결측값이 있습니다. 스케일링 전에 결측값을 처리해주세요.")
        
        if scaling_method == 'min_max':
            # Min-Max 스케일링
            scaler = MinMaxScaler(feature_range=tuple(feature_range))
            scaled_df[columns_to_process] = scaler.fit_transform(scaled_df[columns_to_process])
            print(f"- Min-Max 스케일링 완료: 범위={feature_range}")
            
        elif scaling_method == 'robust':
            # Robust 스케일링 (중앙값과 IQR 기반)
            scaler = RobustScaler()
            scaled_df[columns_to_process] = scaler.fit_transform(scaled_df[columns_to_process])
            print(f"- Robust 스케일링 완료: 중앙값=0, IQR=1")
            
        elif scaling_method == 'quantile':
            # Quantile 스케일링 (분위수 기반)
            scaler = QuantileTransformer(output_distribution='uniform', n_quantiles=1000)
            scaled_df[columns_to_process] = scaler.fit_transform(scaled_df[columns_to_process])
            print(f"- Quantile 스케일링 완료: 균등 분포로 변환")
            
        else:
            raise ValueError(f"지원하지 않는 스케일링 방법: {scaling_method}")
        
    except Exception as e:
        raise ValueError(f"데이터 스케일링 실패: {str(e)}")
    
    # 스케일링 결과 검증
    print(f"\n[3/4] 스케일링 결과를 검증합니다...")
    
    # 스케일링된 컬럼의 통계 정보 출력
    for col in columns_to_process:
        col_mean = scaled_df[col].mean()
        col_std = scaled_df[col].std()
        col_min = scaled_df[col].min()
        col_max = scaled_df[col].max()
        print(f"- 컬럼 '{col}': 평균={col_mean:.3f}, 표준편차={col_std:.3f}, 범위=[{col_min:.3f}, {col_max:.3f}]")

    # CSV로 저장
    print(f"\n[4/4] 결과를 저장합니다...")
    try:
        scaled_df.to_csv(output_filename, index=False, encoding='utf-8')
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
    print(f"- 스케일링된 데이터: {len(scaled_df):,}행")
    print(f"- 스케일링된 컬럼: {len(columns_to_process)}개")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    
    # 보고서 생성
    report = generate_report(df, scaled_df, output_filename, 
                           input_size, output_size, elapsed_time, settings)
    
    return output_filename, report