import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import time
import os
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List
from io import StringIO

def perform_kmeans_clustering(df: pd.DataFrame, feature_columns: List[str],
                             n_clusters: int, random_state: int = 42) -> pd.DataFrame:
    """
    K-means 클러스터링을 수행하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 입력 데이터프레임
    - feature_columns (List[str]): 클러스터링에 사용할 특성 컬럼들
    - n_clusters (int): 클러스터 수
    - random_state (int): 랜덤 시드
    
    Returns:
    - pd.DataFrame: 클러스터 정보가 추가된 데이터프레임
    """
    result_df = df.copy()
    
    # 결측값이 없는 데이터만 사용
    clean_data = df[feature_columns].dropna()
    
    if len(clean_data) > 0:
        # 데이터 정규화
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(clean_data)
        
        # K-means 클러스터링
        kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
        cluster_labels = kmeans.fit_predict(scaled_data)
        
        # 결과를 원본 데이터프레임에 매핑
        result_df['cluster_id'] = -1
        result_df['cluster_center_distance'] = 0.0
        
        for i, idx in enumerate(clean_data.index):
            result_df.loc[idx, 'cluster_id'] = cluster_labels[i]
            # 클러스터 중심까지의 거리 계산
            center = kmeans.cluster_centers_[cluster_labels[i]]
            distance = np.linalg.norm(scaled_data[i] - center)
            result_df.loc[idx, 'cluster_center_distance'] = distance
        
        # 실루엣 점수 계산
        if len(np.unique(cluster_labels)) > 1:
            silhouette_avg = silhouette_score(scaled_data, cluster_labels)
            result_df['silhouette_score'] = silhouette_avg
        else:
            result_df['silhouette_score'] = 0.0
    else:
        result_df['cluster_id'] = -1
        result_df['cluster_center_distance'] = 0.0
        result_df['silhouette_score'] = 0.0
    
    return result_df

def perform_dbscan_clustering(df: pd.DataFrame, feature_columns: List[str],
                             eps: float = 0.5, min_samples: int = 5) -> pd.DataFrame:
    """
    DBSCAN 클러스터링을 수행하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 입력 데이터프레임
    - feature_columns (List[str]): 클러스터링에 사용할 특성 컬럼들
    - eps (float): DBSCAN eps 파라미터
    - min_samples (int): DBSCAN min_samples 파라미터
    
    Returns:
    - pd.DataFrame: 클러스터 정보가 추가된 데이터프레임
    """
    result_df = df.copy()
    
    # 결측값이 없는 데이터만 사용
    clean_data = df[feature_columns].dropna()
    
    if len(clean_data) > 0:
        # 데이터 정규화
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(clean_data)
        
        # DBSCAN 클러스터링
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        cluster_labels = dbscan.fit_predict(scaled_data)
        
        # 결과를 원본 데이터프레임에 매핑
        result_df['cluster_id'] = -1
        result_df['is_noise'] = False
        
        for i, idx in enumerate(clean_data.index):
            result_df.loc[idx, 'cluster_id'] = cluster_labels[i]
            result_df.loc[idx, 'is_noise'] = cluster_labels[i] == -1
        
        # 실루엣 점수 계산 (노이즈가 아닌 클러스터가 2개 이상인 경우)
        non_noise_labels = cluster_labels[cluster_labels != -1]
        if len(np.unique(non_noise_labels)) > 1:
            non_noise_data = scaled_data[cluster_labels != -1]
            silhouette_avg = silhouette_score(non_noise_data, non_noise_labels)
            result_df['silhouette_score'] = silhouette_avg
        else:
            result_df['silhouette_score'] = 0.0
    else:
        result_df['cluster_id'] = -1
        result_df['is_noise'] = False
        result_df['silhouette_score'] = 0.0
    
    return result_df

def perform_hierarchical_clustering(df: pd.DataFrame, feature_columns: List[str],
                                   n_clusters: int, linkage: str = 'ward') -> pd.DataFrame:
    """
    계층적 클러스터링을 수행하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 입력 데이터프레임
    - feature_columns (List[str]): 클러스터링에 사용할 특성 컬럼들
    - n_clusters (int): 클러스터 수
    - linkage (str): 연결 방법 ('ward', 'complete', 'average', 'single')
    
    Returns:
    - pd.DataFrame: 클러스터 정보가 추가된 데이터프레임
    """
    result_df = df.copy()
    
    # 결측값이 없는 데이터만 사용
    clean_data = df[feature_columns].dropna()
    
    if len(clean_data) > 0:
        # 데이터 정규화
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(clean_data)
        
        # 계층적 클러스터링
        hierarchical = AgglomerativeClustering(
            n_clusters=n_clusters, 
            linkage=linkage
        )
        cluster_labels = hierarchical.fit_predict(scaled_data)
        
        # 결과를 원본 데이터프레임에 매핑
        result_df['cluster_id'] = -1
        
        for i, idx in enumerate(clean_data.index):
            result_df.loc[idx, 'cluster_id'] = cluster_labels[i]
        
        # 실루엣 점수 계산
        if len(np.unique(cluster_labels)) > 1:
            silhouette_avg = silhouette_score(scaled_data, cluster_labels)
            result_df['silhouette_score'] = silhouette_avg
        else:
            result_df['silhouette_score'] = 0.0
    else:
        result_df['cluster_id'] = -1
        result_df['silhouette_score'] = 0.0
    
    return result_df

def generate_report(
    df: pd.DataFrame,
    feature_columns: List[str],
    clustering_method: str,
    output_file_name: str,
    settings: Dict[str, Any],
    elapsed_time: float
) -> str:
    """
    지역 클러스터링 작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - feature_columns (List[str]): 특성 컬럼들
    - clustering_method (str): 클러스터링 방법
    - output_file_name (str): 저장된 파일 경로
    - settings (Dict[str, Any]): 사용된 설정
    - elapsed_time (float): 소요 시간 (초)
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    # 기본 통계
    total_records = len(df)
    
    # 클러스터링 결과 요약
    clustering_summary = f"- **총 레코드 수**: {total_records:,}개\n"
    
    if 'cluster_id' in df.columns:
        n_clusters = df['cluster_id'].nunique()
        clustering_summary += f"- **클러스터 수**: {n_clusters}개\n"
        
        # 클러스터별 통계
        cluster_stats = df['cluster_id'].value_counts().sort_index()
        clustering_summary += "\n### 클러스터별 레코드 수\n"
        for cluster_id, count in cluster_stats.items():
            percentage = (count / total_records) * 100
            clustering_summary += f"- **클러스터 {cluster_id}**: {count:,}개 ({percentage:.1f}%)\n"
        
        # 노이즈 점 통계 (DBSCAN인 경우)
        if 'is_noise' in df.columns:
            noise_count = df['is_noise'].sum()
            noise_percentage = (noise_count / total_records) * 100
            clustering_summary += f"- **노이즈 점**: {noise_count:,}개 ({noise_percentage:.1f}%)\n"
        
        # 실루엣 점수
        if 'silhouette_score' in df.columns:
            avg_silhouette = df['silhouette_score'].mean()
            clustering_summary += f"- **평균 실루엣 점수**: {avg_silhouette:.3f}\n"
    
    # 특성별 통계
    feature_stats = ""
    for col in feature_columns:
        if col in df.columns:
            col_stats = df[col].describe()
            feature_stats += f"\n### {col}\n"
            feature_stats += f"- **평균**: {col_stats['mean']:.2f}\n"
            feature_stats += f"- **표준편차**: {col_stats['std']:.2f}\n"
            feature_stats += f"- **최솟값**: {col_stats['min']:.2f}\n"
            feature_stats += f"- **최댓값**: {col_stats['max']:.2f}\n"
    
    report = f"""# 지역 클러스터링 작업 보고서

## 1. 작업 개요
- **작업 유형**: 지역 클러스터링
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **행 수**: {total_records:,}행
- **컬럼 수**: {len(df.columns)}개
- **특성 컬럼**: {', '.join(feature_columns)}

## 3. 클러스터링 설정
- **클러스터링 방법**: {clustering_method}
- **특성 컬럼 수**: {len(feature_columns)}개

## 4. 클러스터링 결과
{clustering_summary}

## 5. 특성별 통계
{feature_stats}

## 6. 성능 지표
- **처리 속도**: {total_records / elapsed_time:.2f} 행/초
- **메모리 사용량**: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB

## 7. 작업 상태
- **상태**: 성공
- **처리 결과**: {clustering_method} 클러스터링이 성공적으로 완료됨
- **출력 파일**: {output_file_name}
"""
    return report

def solution(
    data: object,
    feature_columns: List[str],
    output_file_name: str,
    clustering_method: str = 'kmeans',
    settings: Optional[Dict[str, Any]] = None
) -> Tuple[str, str]:
    """
    CSV 파일에서 지역 클러스터링을 수행하는 함수.
    
    Parameters:
    - data: CSV 파일 경로 또는 StringIO 객체
    - feature_columns: 클러스터링에 사용할 특성 컬럼들
    - output_file_name: 저장할 파일 이름
    - clustering_method: 클러스터링 방법 ('kmeans', 'dbscan', 'hierarchical')
    - settings: 클러스터링 설정 (선택사항)
    
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
    missing_columns = [col for col in feature_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"다음 컬럼들이 데이터에 존재하지 않습니다: {missing_columns}")
    
    print(f"- 총 데이터 포인트: {len(df):,}개")
    print(f"- 특성 컬럼: {', '.join(feature_columns)}")
    print(f"- 클러스터링 방법: {clustering_method}")
    
    # 클러스터링 수행
    if clustering_method == 'kmeans':
        print("\n[클러스터링] K-means 클러스터링을 수행합니다...")
        df = perform_kmeans_clustering(
            df, feature_columns,
            settings.get('n_clusters', 5),
            settings.get('random_state', 42)
        )
        
    elif clustering_method == 'dbscan':
        print("\n[클러스터링] DBSCAN 클러스터링을 수행합니다...")
        df = perform_dbscan_clustering(
            df, feature_columns,
            settings.get('eps', 0.5),
            settings.get('min_samples', 5)
        )
        
    elif clustering_method == 'hierarchical':
        print("\n[클러스터링] 계층적 클러스터링을 수행합니다...")
        df = perform_hierarchical_clustering(
            df, feature_columns,
            settings.get('n_clusters', 5),
            settings.get('linkage', 'ward')
        )
    
    else:
        raise ValueError(f"지원하지 않는 클러스터링 방법입니다: {clustering_method}")
    
    # 클러스터링 결과 요약
    if 'cluster_id' in df.columns:
        n_clusters = df['cluster_id'].nunique()
        print(f"- 생성된 클러스터 수: {n_clusters}개")
        
        if 'silhouette_score' in df.columns:
            avg_silhouette = df['silhouette_score'].mean()
            print(f"- 평균 실루엣 점수: {avg_silhouette:.3f}")
    
    # 결과 저장
    print(f"\n[저장] 결과를 저장합니다...")
    df.to_csv(output_file_name, index=False, encoding='utf-8')
    
    # 소요 시간 계산
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 보고서 생성
    report = generate_report(
        df=df,
        feature_columns=feature_columns,
        clustering_method=clustering_method,
        output_file_name=output_file_name,
        settings=settings,
        elapsed_time=elapsed_time
    )
    
    return output_file_name, report