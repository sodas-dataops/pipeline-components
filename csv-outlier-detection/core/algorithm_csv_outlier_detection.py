import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from scipy import stats
import time
import os
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List
from io import StringIO

def detect_outliers_iqr(df: pd.DataFrame, columns: List[str], 
                       iqr_multiplier: float = 1.5) -> pd.DataFrame:
    """
    IQR 방법을 사용하여 이상치를 탐지하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 입력 데이터프레임
    - columns (List[str]): 이상치 탐지할 컬럼들
    - iqr_multiplier (float): IQR 배수
    
    Returns:
    - pd.DataFrame: 이상치 정보가 추가된 데이터프레임
    """
    result_df = df.copy()
    result_df['is_outlier_iqr'] = False
    result_df['outlier_reason_iqr'] = ''
    
    for col in columns:
        if col in df.columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - iqr_multiplier * IQR
            upper_bound = Q3 + iqr_multiplier * IQR
            
            outliers = (df[col] < lower_bound) | (df[col] > upper_bound)
            result_df.loc[outliers, 'is_outlier_iqr'] = True
            result_df.loc[outliers, 'outlier_reason_iqr'] += f'{col} out of range; '
    
    return result_df

def detect_outliers_zscore(df: pd.DataFrame, columns: List[str], 
                          z_threshold: float = 3.0) -> pd.DataFrame:
    """
    Z-Score 방법을 사용하여 이상치를 탐지하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 입력 데이터프레임
    - columns (List[str]): 이상치 탐지할 컬럼들
    - z_threshold (float): Z-Score 임계값
    
    Returns:
    - pd.DataFrame: 이상치 정보가 추가된 데이터프레임
    """
    result_df = df.copy()
    result_df['is_outlier_zscore'] = False
    result_df['outlier_reason_zscore'] = ''
    
    for col in columns:
        if col in df.columns:
            z_scores = np.abs(stats.zscore(df[col].dropna()))
            outliers = z_scores > z_threshold
            
            # 원본 인덱스에 맞춰서 이상치 표시
            outlier_indices = df[col].dropna().index[outliers]
            result_df.loc[outlier_indices, 'is_outlier_zscore'] = True
            result_df.loc[outlier_indices, 'outlier_reason_zscore'] += f'{col} high z-score; '
    
    return result_df

def detect_outliers_isolation_forest(df: pd.DataFrame, columns: List[str],
                                   contamination: float = 0.1,
                                   random_state: int = 42) -> pd.DataFrame:
    """
    Isolation Forest 방법을 사용하여 이상치를 탐지하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 입력 데이터프레임
    - columns (List[str]): 이상치 탐지할 컬럼들
    - contamination (float): 이상치 비율
    - random_state (int): 랜덤 시드
    
    Returns:
    - pd.DataFrame: 이상치 정보가 추가된 데이터프레임
    """
    result_df = df.copy()
    
    # 결측값이 없는 데이터만 사용
    clean_data = df[columns].dropna()
    
    if len(clean_data) > 0:
        # Isolation Forest 모델 학습
        iso_forest = IsolationForest(
            contamination=contamination,
            random_state=random_state
        )
        
        # 데이터 정규화
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(clean_data)
        
        # 이상치 예측
        outlier_predictions = iso_forest.fit_predict(scaled_data)
        
        # 결과를 원본 데이터프레임에 매핑
        result_df['is_outlier_isolation'] = False
        result_df['outlier_score_isolation'] = 0.0
        
        # 이상치 점수 계산
        outlier_scores = iso_forest.decision_function(scaled_data)
        
        for i, idx in enumerate(clean_data.index):
            result_df.loc[idx, 'is_outlier_isolation'] = outlier_predictions[i] == -1
            result_df.loc[idx, 'outlier_score_isolation'] = outlier_scores[i]
        
        result_df['outlier_reason_isolation'] = result_df['is_outlier_isolation'].map(
            {True: 'Isolation Forest anomaly', False: ''}
        )
    else:
        result_df['is_outlier_isolation'] = False
        result_df['outlier_score_isolation'] = 0.0
        result_df['outlier_reason_isolation'] = ''
    
    return result_df

def detect_outliers_dbscan(df: pd.DataFrame, columns: List[str],
                          eps: float = 0.5, min_samples: int = 5) -> pd.DataFrame:
    """
    DBSCAN 방법을 사용하여 이상치를 탐지하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 입력 데이터프레임
    - columns (List[str]): 이상치 탐지할 컬럼들
    - eps (float): DBSCAN eps 파라미터
    - min_samples (int): DBSCAN min_samples 파라미터
    
    Returns:
    - pd.DataFrame: 이상치 정보가 추가된 데이터프레임
    """
    result_df = df.copy()
    
    # 결측값이 없는 데이터만 사용
    clean_data = df[columns].dropna()
    
    if len(clean_data) > 0:
        # 데이터 정규화
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(clean_data)
        
        # DBSCAN 클러스터링
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        cluster_labels = dbscan.fit_predict(scaled_data)
        
        # 결과를 원본 데이터프레임에 매핑
        result_df['is_outlier_dbscan'] = False
        result_df['cluster_id_dbscan'] = -1
        
        for i, idx in enumerate(clean_data.index):
            result_df.loc[idx, 'is_outlier_dbscan'] = cluster_labels[i] == -1
            result_df.loc[idx, 'cluster_id_dbscan'] = cluster_labels[i]
        
        result_df['outlier_reason_dbscan'] = result_df['is_outlier_dbscan'].map(
            {True: 'DBSCAN noise point', False: ''}
        )
    else:
        result_df['is_outlier_dbscan'] = False
        result_df['cluster_id_dbscan'] = -1
        result_df['outlier_reason_dbscan'] = ''
    
    return result_df

def generate_report(
    df: pd.DataFrame,
    target_columns: List[str],
    output_file_name: str,
    settings: Dict[str, Any],
    elapsed_time: float
) -> str:
    """
    이상치 탐지 작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - target_columns (List[str]): 대상 컬럼들
    - output_file_name (str): 저장된 파일 경로
    - settings (Dict[str, Any]): 사용된 설정
    - elapsed_time (float): 소요 시간 (초)
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    # 기본 통계
    total_records = len(df)
    
    # 이상치 탐지 결과 요약
    outlier_summary = f"- **총 레코드 수**: {total_records:,}개\n"
    
    # 각 방법별 이상치 통계
    methods = ['iqr', 'zscore', 'isolation', 'dbscan']
    method_names = ['IQR', 'Z-Score', 'Isolation Forest', 'DBSCAN']
    
    for method, method_name in zip(methods, method_names):
        outlier_col = f'is_outlier_{method}'
        if outlier_col in df.columns:
            outlier_count = df[outlier_col].sum()
            outlier_percentage = (outlier_count / total_records) * 100
            outlier_summary += f"- **{method_name} 이상치**: {outlier_count:,}개 ({outlier_percentage:.1f}%)\n"
    
    # 통합 이상치 통계
    outlier_columns = [col for col in df.columns if col.startswith('is_outlier_')]
    if outlier_columns:
        # 모든 방법에서 이상치로 탐지된 경우
        all_outliers = df[outlier_columns].any(axis=1)
        all_outlier_count = all_outliers.sum()
        all_outlier_percentage = (all_outlier_count / total_records) * 100
        outlier_summary += f"- **통합 이상치**: {all_outlier_count:,}개 ({all_outlier_percentage:.1f}%)\n"
    
    # 컬럼별 통계
    column_stats = ""
    for col in target_columns:
        if col in df.columns:
            col_stats = df[col].describe()
            column_stats += f"\n### {col}\n"
            column_stats += f"- **평균**: {col_stats['mean']:.2f}\n"
            column_stats += f"- **표준편차**: {col_stats['std']:.2f}\n"
            column_stats += f"- **최솟값**: {col_stats['min']:.2f}\n"
            column_stats += f"- **최댓값**: {col_stats['max']:.2f}\n"
    
    report = f"""# 이상치 탐지 작업 보고서

## 1. 작업 개요
- **작업 유형**: 이상치 탐지
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **행 수**: {total_records:,}행
- **컬럼 수**: {len(df.columns)}개
- **대상 컬럼**: {', '.join(target_columns)}

## 3. 탐지 설정
- **IQR 방법**: {settings.get('use_iqr', True)}
- **Z-Score 방법**: {settings.get('use_zscore', True)}
- **Isolation Forest**: {settings.get('use_isolation_forest', False)}
- **DBSCAN**: {settings.get('use_dbscan', False)}

## 4. 탐지 결과
{outlier_summary}

## 5. 컬럼별 통계
{column_stats}

## 6. 성능 지표
- **처리 속도**: {total_records / elapsed_time:.2f} 행/초
- **메모리 사용량**: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB

## 7. 작업 상태
- **상태**: 성공
- **처리 결과**: 이상치 탐지가 성공적으로 완료됨
- **출력 파일**: {output_file_name}
"""
    return report

def solution(
    data: object,
    target_columns: List[str],
    output_file_name: str,
    settings: Optional[Dict[str, Any]] = None
) -> Tuple[str, str]:
    """
    CSV 파일에서 이상치를 탐지하는 함수.
    
    Parameters:
    - data: CSV 파일 경로 또는 StringIO 객체
    - target_columns: 이상치 탐지할 컬럼들
    - output_file_name: 저장할 파일 이름
    - settings: 탐지 설정 (선택사항)
    
    Returns:
    - tuple: (출력 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    
    # 기본 설정
    if settings is None:
        settings = {}
    
    # CSV 데이터 로드
    df = pd.read_csv(data)
    
    # 컬럼 존재 확인
    missing_columns = [col for col in target_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"다음 컬럼들이 데이터에 존재하지 않습니다: {missing_columns}")
    
    print(f"- 총 데이터 포인트: {len(df):,}개")
    print(f"- 대상 컬럼: {', '.join(target_columns)}")
    
    # 이상치 탐지 수행
    if settings.get('use_iqr', True):
        print("\n[1/4] IQR 방법으로 이상치를 탐지합니다...")
        df = detect_outliers_iqr(
            df, target_columns,
            settings.get('iqr_multiplier', 1.5)
        )
    
    if settings.get('use_zscore', True):
        print("\n[2/4] Z-Score 방법으로 이상치를 탐지합니다...")
        df = detect_outliers_zscore(
            df, target_columns,
            settings.get('z_threshold', 3.0)
        )
    
    if settings.get('use_isolation_forest', False):
        print("\n[3/4] Isolation Forest 방법으로 이상치를 탐지합니다...")
        df = detect_outliers_isolation_forest(
            df, target_columns,
            settings.get('contamination', 0.1),
            settings.get('random_state', 42)
        )
    
    if settings.get('use_dbscan', False):
        print("\n[4/4] DBSCAN 방법으로 이상치를 탐지합니다...")
        df = detect_outliers_dbscan(
            df, target_columns,
            settings.get('eps', 0.5),
            settings.get('min_samples', 5)
        )
    
    # 통합 이상치 플래그 생성
    outlier_columns = [col for col in df.columns if col.startswith('is_outlier_')]
    if outlier_columns:
        df['is_outlier_any'] = df[outlier_columns].any(axis=1)
        df['outlier_methods'] = df[outlier_columns].apply(
            lambda row: '; '.join([col.replace('is_outlier_', '') for col in outlier_columns if row[col]]), 
            axis=1
        )
    
    # 결과 저장
    print(f"\n[저장] 결과를 저장합니다...")
    df.to_csv(output_file_name, index=False, encoding='utf-8')
    
    # 소요 시간 계산
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 보고서 생성
    report = generate_report(
        df=df,
        target_columns=target_columns,
        output_file_name=output_file_name,
        settings=settings,
        elapsed_time=elapsed_time
    )
    
    return output_file_name, report