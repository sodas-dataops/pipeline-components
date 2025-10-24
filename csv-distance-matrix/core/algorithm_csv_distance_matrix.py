import pandas as pd
import numpy as np
from scipy.spatial.distance import pdist, squareform
from geopy.distance import geodesic
import time
import os
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List
from io import StringIO

def calculate_euclidean_distance_matrix(df: pd.DataFrame, feature_columns: List[str]) -> np.ndarray:
    """
    유클리드 거리 행렬을 계산하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 입력 데이터프레임
    - feature_columns (List[str]): 거리 계산에 사용할 특성 컬럼들
    
    Returns:
    - np.ndarray: 거리 행렬
    """
    # 결측값이 없는 데이터만 사용
    clean_data = df[feature_columns].dropna()
    
    if len(clean_data) == 0:
        return np.array([])
    
    # 유클리드 거리 계산
    distances = pdist(clean_data.values, metric='euclidean')
    distance_matrix = squareform(distances)
    
    return distance_matrix

def calculate_manhattan_distance_matrix(df: pd.DataFrame, feature_columns: List[str]) -> np.ndarray:
    """
    맨하탄 거리 행렬을 계산하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 입력 데이터프레임
    - feature_columns (List[str]): 거리 계산에 사용할 특성 컬럼들
    
    Returns:
    - np.ndarray: 거리 행렬
    """
    # 결측값이 없는 데이터만 사용
    clean_data = df[feature_columns].dropna()
    
    if len(clean_data) == 0:
        return np.array([])
    
    # 맨하탄 거리 계산
    distances = pdist(clean_data.values, metric='cityblock')
    distance_matrix = squareform(distances)
    
    return distance_matrix

def calculate_geodesic_distance_matrix(df: pd.DataFrame, lat_column: str, lon_column: str) -> np.ndarray:
    """
    지구 표면 거리 행렬을 계산하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 입력 데이터프레임
    - lat_column (str): 위도 컬럼명
    - lon_column (str): 경도 컬럼명
    
    Returns:
    - np.ndarray: 거리 행렬 (킬로미터 단위)
    """
    # 결측값이 없는 데이터만 사용
    clean_data = df[[lat_column, lon_column]].dropna()
    
    if len(clean_data) == 0:
        return np.array([])
    
    n = len(clean_data)
    distance_matrix = np.zeros((n, n))
    
    # 각 점 쌍에 대해 지구 표면 거리 계산
    for i in range(n):
        for j in range(i + 1, n):
            point1 = (clean_data.iloc[i][lat_column], clean_data.iloc[i][lon_column])
            point2 = (clean_data.iloc[j][lat_column], clean_data.iloc[j][lon_column])
            
            distance = geodesic(point1, point2).kilometers
            distance_matrix[i, j] = distance
            distance_matrix[j, i] = distance
    
    return distance_matrix

def calculate_cosine_distance_matrix(df: pd.DataFrame, feature_columns: List[str]) -> np.ndarray:
    """
    코사인 거리 행렬을 계산하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 입력 데이터프레임
    - feature_columns (List[str]): 거리 계산에 사용할 특성 컬럼들
    
    Returns:
    - np.ndarray: 거리 행렬
    """
    # 결측값이 없는 데이터만 사용
    clean_data = df[feature_columns].dropna()
    
    if len(clean_data) == 0:
        return np.array([])
    
    # 코사인 거리 계산
    distances = pdist(clean_data.values, metric='cosine')
    distance_matrix = squareform(distances)
    
    return distance_matrix

def generate_report(
    df: pd.DataFrame,
    feature_columns: List[str],
    distance_method: str,
    output_file_name: str,
    settings: Dict[str, Any],
    elapsed_time: float,
    distance_matrix: np.ndarray
) -> str:
    """
    거리 행렬 작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - feature_columns (List[str]): 특성 컬럼들
    - distance_method (str): 거리 계산 방법
    - output_file_name (str): 저장된 파일 경로
    - settings (Dict[str, Any]): 사용된 설정
    - elapsed_time (float): 소요 시간 (초)
    - distance_matrix (np.ndarray): 계산된 거리 행렬
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    # 기본 통계
    total_records = len(df)
    matrix_size = distance_matrix.shape[0] if distance_matrix.size > 0 else 0
    
    # 거리 행렬 통계
    distance_stats = ""
    if distance_matrix.size > 0:
        # 대각선을 제외한 거리 값들
        mask = ~np.eye(distance_matrix.shape[0], dtype=bool)
        distances = distance_matrix[mask]
        
        distance_stats = f"""
### 거리 행렬 통계
- **행렬 크기**: {matrix_size} x {matrix_size}
- **총 거리 쌍 수**: {len(distances):,}개
- **최소 거리**: {distances.min():.4f}
- **최대 거리**: {distances.max():.4f}
- **평균 거리**: {distances.mean():.4f}
- **표준편차**: {distances.std():.4f}
- **중앙값**: {np.median(distances):.4f}
"""
    
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
    
    report = f"""# 거리 행렬 계산 작업 보고서

## 1. 작업 개요
- **작업 유형**: 거리 행렬 계산
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **행 수**: {total_records:,}행
- **컬럼 수**: {len(df.columns)}개
- **특성 컬럼**: {', '.join(feature_columns)}

## 3. 거리 계산 설정
- **거리 계산 방법**: {distance_method}
- **특성 컬럼 수**: {len(feature_columns)}개

## 4. 거리 행렬 결과
{distance_stats}

## 5. 특성별 통계
{feature_stats}

## 6. 성능 지표
- **처리 속도**: {total_records / elapsed_time:.2f} 행/초
- **메모리 사용량**: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB
- **거리 행렬 메모리**: {distance_matrix.nbytes / 1024 / 1024:.2f} MB

## 7. 작업 상태
- **상태**: 성공
- **처리 결과**: {distance_method} 거리 행렬이 성공적으로 계산됨
- **출력 파일**: {output_file_name}
"""
    return report

def solution(
    data: object,
    feature_columns: List[str],
    output_file_name: str,
    distance_method: str = 'euclidean',
    settings: Optional[Dict[str, Any]] = None
) -> Tuple[str, str]:
    """
    CSV 파일에서 거리 행렬을 계산하는 함수.
    
    Parameters:
    - data: CSV 파일 경로 또는 StringIO 객체
    - feature_columns: 거리 계산에 사용할 특성 컬럼들 (settings에서 덮어쓸 수 있음)
    - output_file_name: 저장할 파일 이름
    - distance_method: 거리 계산 방법 ('euclidean', 'manhattan', 'geodesic', 'cosine') (settings에서 덮어쓸 수 있음)
    - settings: 거리 계산 설정 (선택사항)
        - feature_columns: 특성 컬럼 리스트
        - distance_method: 거리 계산 방법
    
    Returns:
    - tuple: (출력 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    
    # 기본 설정
    if settings is None:
        settings = {}
    
    # settings에서 파라미터 읽어오기 (기본값으로 덮어쓰기 방지)
    if 'feature_columns' in settings and settings['feature_columns']:
        feature_columns = settings['feature_columns']
    if 'distance_method' in settings and settings['distance_method']:
        distance_method = settings['distance_method']
    
    # CSV 데이터 로드
    df = pd.read_csv(data)
    
    # 컬럼 존재 확인
    missing_columns = [col for col in feature_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"다음 컬럼들이 데이터에 존재하지 않습니다: {missing_columns}")
    
    print(f"- 총 데이터 포인트: {len(df):,}개")
    print(f"- 특성 컬럼: {', '.join(feature_columns)}")
    print(f"- 거리 계산 방법: {distance_method}")
    
    # 거리 행렬 계산
    if distance_method == 'euclidean':
        print("\n[거리 계산] 유클리드 거리 행렬을 계산합니다...")
        distance_matrix = calculate_euclidean_distance_matrix(df, feature_columns)
        
    elif distance_method == 'manhattan':
        print("\n[거리 계산] 맨하탄 거리 행렬을 계산합니다...")
        distance_matrix = calculate_manhattan_distance_matrix(df, feature_columns)
        
    elif distance_method == 'geodesic':
        if len(feature_columns) != 2:
            raise ValueError("지구 표면 거리 계산을 위해서는 정확히 2개의 컬럼(위도, 경도)이 필요합니다.")
        print("\n[거리 계산] 지구 표면 거리 행렬을 계산합니다...")
        distance_matrix = calculate_geodesic_distance_matrix(df, feature_columns[0], feature_columns[1])
        
    elif distance_method == 'cosine':
        print("\n[거리 계산] 코사인 거리 행렬을 계산합니다...")
        distance_matrix = calculate_cosine_distance_matrix(df, feature_columns)
    
    else:
        raise ValueError(f"지원하지 않는 거리 계산 방법입니다: {distance_method}")
    
    # 거리 행렬 결과 요약
    if distance_matrix.size > 0:
        matrix_size = distance_matrix.shape[0]
        print(f"- 거리 행렬 크기: {matrix_size} x {matrix_size}")
        
        # 대각선을 제외한 거리 값들
        mask = ~np.eye(matrix_size, dtype=bool)
        distances = distance_matrix[mask]
        print(f"- 거리 범위: {distances.min():.4f} ~ {distances.max():.4f}")
        print(f"- 평균 거리: {distances.mean():.4f}")
    
    # 거리 행렬을 DataFrame으로 변환
    if distance_matrix.size > 0:
        # 인덱스와 컬럼명 설정
        index_names = [f"point_{i}" for i in range(distance_matrix.shape[0])]
        distance_df = pd.DataFrame(
            distance_matrix,
            index=index_names,
            columns=index_names
        )
    else:
        distance_df = pd.DataFrame()
    
    # 결과 저장
    print(f"\n[저장] 결과를 저장합니다...")
    distance_df.to_csv(output_file_name, index=True, encoding='utf-8')
    
    # 소요 시간 계산
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 보고서 생성
    report = generate_report(
        df=df,
        feature_columns=feature_columns,
        distance_method=distance_method,
        output_file_name=output_file_name,
        settings=settings,
        elapsed_time=elapsed_time,
        distance_matrix=distance_matrix
    )
    
    return output_file_name, report