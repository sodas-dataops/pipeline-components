import pandas as pd
import numpy as np
from geopy.distance import geodesic
from sklearn.cluster import DBSCAN, KMeans
from sklearn.neighbors import NearestNeighbors
from scipy.spatial.distance import pdist, squareform
from scipy.stats import gaussian_kde
import time
import os
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List
from io import StringIO

def calculate_distances(df: pd.DataFrame, lat_col: str, lon_col: str, 
                       distance_method: str = 'haversine') -> pd.DataFrame:
    """
    지리적 거리를 계산하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 입력 데이터프레임
    - lat_col (str): 위도 컬럼명
    - lon_col (str): 경도 컬럼명
    - distance_method (str): 거리 계산 방법 ('haversine', 'euclidean')
    
    Returns:
    - pd.DataFrame: 거리 정보가 추가된 데이터프레임
    """
    result_df = df.copy()
    
    if distance_method == 'haversine':
        # 중심점 계산
        center_lat = df[lat_col].mean()
        center_lon = df[lon_col].mean()
        
        # 각 점에서 중심점까지의 거리 계산
        distances = []
        for _, row in df.iterrows():
            dist = geodesic(
                (row[lat_col], row[lon_col]), 
                (center_lat, center_lon)
            ).kilometers
            distances.append(dist)
        
        result_df['distance_from_center_km'] = distances
        
        # 최근접 이웃까지의 거리 계산
        if len(df) > 1:
            coords = df[[lat_col, lon_col]].values
            nbrs = NearestNeighbors(n_neighbors=2, algorithm='ball_tree').fit(coords)
            distances_nn, _ = nbrs.kneighbors(coords)
            result_df['distance_to_nearest_neighbor_km'] = distances_nn[:, 1] * 111  # 대략적인 km 변환
    
    elif distance_method == 'euclidean':
        # 유클리드 거리 계산 (위도/경도를 그대로 사용)
        coords = df[[lat_col, lon_col]].values
        center = coords.mean(axis=0)
        distances = np.sqrt(np.sum((coords - center)**2, axis=1))
        result_df['distance_from_center_euclidean'] = distances
    
    return result_df

def perform_clustering(df: pd.DataFrame, lat_col: str, lon_col: str,
                      clustering_method: str = 'dbscan', 
                      n_clusters: int = 5, eps: float = 0.1,
                      min_samples: int = 5) -> pd.DataFrame:
    """
    지리적 클러스터링을 수행하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 입력 데이터프레임
    - lat_col (str): 위도 컬럼명
    - lon_col (str): 경도 컬럼명
    - clustering_method (str): 클러스터링 방법 ('dbscan', 'kmeans')
    - n_clusters (int): K-means 클러스터 수
    - eps (float): DBSCAN eps 파라미터
    - min_samples (int): DBSCAN min_samples 파라미터
    
    Returns:
    - pd.DataFrame: 클러스터 정보가 추가된 데이터프레임
    """
    result_df = df.copy()
    coords = df[[lat_col, lon_col]].values
    
    if clustering_method == 'dbscan':
        # DBSCAN 클러스터링
        clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(coords)
        result_df['cluster_id'] = clustering.labels_
        result_df['is_noise'] = clustering.labels_ == -1
        
    elif clustering_method == 'kmeans':
        # K-means 클러스터링
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        result_df['cluster_id'] = kmeans.fit_predict(coords)
        result_df['is_noise'] = False
    
    # 클러스터별 통계
    cluster_stats = result_df.groupby('cluster_id').agg({
        lat_col: ['count', 'mean', 'std'],
        lon_col: ['mean', 'std']
    }).round(6)
    
    return result_df

def calculate_density(df: pd.DataFrame, lat_col: str, lon_col: str,
                     density_method: str = 'kde', bandwidth: float = 0.01) -> pd.DataFrame:
    """
    지리적 밀도를 계산하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 입력 데이터프레임
    - lat_col (str): 위도 컬럼명
    - lon_col (str): 경도 컬럼명
    - density_method (str): 밀도 계산 방법 ('kde', 'grid')
    - bandwidth (float): KDE 대역폭
    
    Returns:
    - pd.DataFrame: 밀도 정보가 추가된 데이터프레임
    """
    result_df = df.copy()
    
    if density_method == 'kde':
        # KDE를 사용한 밀도 계산
        coords = df[[lat_col, lon_col]].values
        kde = gaussian_kde(coords.T, bw_method=bandwidth)
        densities = kde(coords.T)
        result_df['density_score'] = densities
        
    elif density_method == 'grid':
        # 그리드 기반 밀도 계산
        lat_bins = 20
        lon_bins = 20
        
        lat_edges = np.linspace(df[lat_col].min(), df[lat_col].max(), lat_bins + 1)
        lon_edges = np.linspace(df[lon_col].min(), df[lon_col].max(), lon_bins + 1)
        
        # 각 점이 속한 그리드 셀의 밀도 계산
        densities = []
        for _, row in df.iterrows():
            lat_bin = np.digitize(row[lat_col], lat_edges) - 1
            lon_bin = np.digitize(row[lon_col], lon_edges) - 1
            
            # 해당 그리드 셀 내의 점 개수
            in_cell = ((df[lat_col] >= lat_edges[lat_bin]) & 
                      (df[lat_col] < lat_edges[lat_bin + 1]) &
                      (df[lon_col] >= lon_edges[lon_bin]) & 
                      (df[lon_col] < lon_edges[lon_bin + 1]))
            
            densities.append(in_cell.sum())
        
        result_df['density_score'] = densities
    
    return result_df

def generate_report(
    df: pd.DataFrame,
    lat_column: str,
    lon_column: str,
    analysis_type: str,
    output_file_name: str,
    settings: Dict[str, Any],
    elapsed_time: float
) -> str:
    """
    지리공간 분석 작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - lat_column (str): 위도 컬럼명
    - lon_column (str): 경도 컬럼명
    - analysis_type (str): 분석 유형
    - output_file_name (str): 저장된 파일 경로
    - settings (Dict[str, Any]): 사용된 설정
    - elapsed_time (float): 소요 시간 (초)
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    # 기본 통계
    lat_stats = df[lat_column].describe()
    lon_stats = df[lon_column].describe()
    
    # 분석 결과 요약
    analysis_summary = ""
    if 'distance_from_center_km' in df.columns:
        analysis_summary += f"- **중심점까지 평균 거리**: {df['distance_from_center_km'].mean():.2f} km\n"
        analysis_summary += f"- **최대 거리**: {df['distance_from_center_km'].max():.2f} km\n"
    
    if 'cluster_id' in df.columns:
        n_clusters = df['cluster_id'].nunique()
        noise_points = df['is_noise'].sum() if 'is_noise' in df.columns else 0
        analysis_summary += f"- **클러스터 수**: {n_clusters}개\n"
        analysis_summary += f"- **노이즈 점**: {noise_points}개\n"
    
    if 'density_score' in df.columns:
        analysis_summary += f"- **평균 밀도 점수**: {df['density_score'].mean():.4f}\n"
        analysis_summary += f"- **최대 밀도 점수**: {df['density_score'].max():.4f}\n"
    
    report = f"""# 지리공간 분석 작업 보고서

## 1. 작업 개요
- **작업 유형**: {analysis_type}
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **행 수**: {len(df):,}행
- **컬럼 수**: {len(df.columns)}개
- **위도 컬럼**: {lat_column}
- **경도 컬럼**: {lon_column}

## 3. 분석 설정
- **분석 유형**: {analysis_type}
- **거리 계산 방법**: {settings.get('distance_method', 'haversine')}
- **클러스터링 방법**: {settings.get('clustering_method', 'dbscan')}
- **밀도 계산 방법**: {settings.get('density_method', 'kde')}

## 4. 지리적 범위
### 위도 ({lat_column})
- **최솟값**: {lat_stats['min']:.6f}°
- **최댓값**: {lat_stats['max']:.6f}°
- **평균**: {lat_stats['mean']:.6f}°
- **표준편차**: {lat_stats['std']:.6f}°

### 경도 ({lon_column})
- **최솟값**: {lon_stats['min']:.6f}°
- **최댓값**: {lon_stats['max']:.6f}°
- **평균**: {lon_stats['mean']:.6f}°
- **표준편차**: {lon_stats['std']:.6f}°

## 5. 분석 결과
{analysis_summary}

## 6. 성능 지표
- **처리 속도**: {len(df) / elapsed_time:.2f} 행/초
- **메모리 사용량**: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB

## 7. 작업 상태
- **상태**: 성공
- **처리 결과**: {analysis_type} 분석이 성공적으로 완료됨
- **출력 파일**: {output_file_name}
"""
    return report

def solution(
    data: object,
    lat_column: str,
    lon_column: str,
    output_file_name: str,
    analysis_type: str = 'comprehensive',
    settings: Optional[Dict[str, Any]] = None
) -> Tuple[str, str]:
    """
    CSV 파일에서 지리공간 분석을 수행하는 함수.
    
    Parameters:
    - data: CSV 파일 경로 또는 StringIO 객체
    - lat_column: 위도 컬럼명
    - lon_column: 경도 컬럼명
    - output_file_name: 저장할 파일 이름
    - analysis_type: 분석 유형 ('distance', 'clustering', 'density', 'comprehensive')
    - settings: 분석 설정 (선택사항)
    
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
    if lat_column not in df.columns:
        raise ValueError(f"위도 컬럼 '{lat_column}'이 데이터에 존재하지 않습니다.")
    if lon_column not in df.columns:
        raise ValueError(f"경도 컬럼 '{lon_column}'이 데이터에 존재하지 않습니다.")
    
    # 결측값 제거
    initial_count = len(df)
    df = df.dropna(subset=[lat_column, lon_column])
    if len(df) < initial_count:
        print(f"- 경고: {initial_count - len(df)}개의 결측값이 있는 행이 제거되었습니다.")
    
    # 좌표 유효성 검증
    invalid_coords = ((df[lat_column] < -90) | (df[lat_column] > 90) |
                     (df[lon_column] < -180) | (df[lon_column] > 180))
    if invalid_coords.any():
        print(f"- 경고: {invalid_coords.sum()}개의 유효하지 않은 좌표가 발견되었습니다.")
        df = df[~invalid_coords]
    
    print(f"- 유효한 데이터 포인트: {len(df):,}개")
    
    # 분석 수행
    if analysis_type in ['distance', 'comprehensive']:
        print("\n[1/3] 거리 계산을 수행합니다...")
        df = calculate_distances(
            df, lat_column, lon_column,
            settings.get('distance_method', 'haversine')
        )
    
    if analysis_type in ['clustering', 'comprehensive']:
        print("\n[2/3] 클러스터링을 수행합니다...")
        df = perform_clustering(
            df, lat_column, lon_column,
            settings.get('clustering_method', 'dbscan'),
            settings.get('n_clusters', 5),
            settings.get('eps', 0.1),
            settings.get('min_samples', 5)
        )
    
    if analysis_type in ['density', 'comprehensive']:
        print("\n[3/3] 밀도 분석을 수행합니다...")
        df = calculate_density(
            df, lat_column, lon_column,
            settings.get('density_method', 'kde'),
            settings.get('bandwidth', 0.01)
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
        lat_column=lat_column,
        lon_column=lon_column,
        analysis_type=analysis_type,
        output_file_name=output_file_name,
        settings=settings,
        elapsed_time=elapsed_time
    )
    
    return output_file_name, report