import pandas as pd
import numpy as np
import json
import time
import os
from datetime import datetime
from io import StringIO
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

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
    cluster_column = settings.get('cluster_column', '') if settings else ''
    n_clusters = settings.get('n_clusters', 5) if settings else 5
    sample_size = settings.get('sample_size', 0) if settings else 0
    sample_ratio = settings.get('sample_ratio', 0.1) if settings else 0.1
    random_state = settings.get('random_state', None) if settings else None

    # 클러스터 컬럼 정보
    cluster_info = f"- **클러스터 컬럼**: {cluster_column}" if cluster_column else ""
    cluster_count_info = f"- **클러스터 수**: {n_clusters}개"
    sample_info = f"- **샘플 크기**: {sample_size:,}개" if sample_size > 0 else f"- **샘플 비율**: {sample_ratio:.2%}"
    random_info = f"- **랜덤 시드**: {random_state}" if random_state else "- **랜덤 시드**: None"
    
    # 클러스터별 샘플 통계
    if 'cluster_id' in output_data.columns:
        cluster_stats = output_data['cluster_id'].value_counts().sort_index()
        cluster_stats_info = "\n".join([f"- **클러스터 {i}**: {count:,}개" for i, count in cluster_stats.items()])
    else:
        cluster_stats_info = "클러스터 정보 없음"
    
    report = f"""# 클러스터 샘플링 작업 보고서

## 1. 작업 개요
- **작업 유형**: 클러스터 샘플링
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초
- **샘플링된 데이터**: {len(output_data):,}개
- **샘플링 비율**: {len(output_data) / len(input_data) * 100:.2f}%
{cluster_info}
{cluster_count_info}
{sample_info}
{random_info}

## 2. 입력 데이터
- **데이터 크기**: {input_size / 1024:.2f} KB
- **행 수**: {len(input_data):,}
- **열 수**: {len(input_data.columns)}
- **열 이름**: {', '.join(input_data.columns)}

## 3. 클러스터 샘플링 결과
- **출력 파일**: {output_filename}
- **파일 크기**: {output_size / 1024:.2f} KB
- **행 수**: {len(output_data):,}
- **열 수**: {len(output_data.columns)}
- **샘플링 비율**: {len(output_data) / len(input_data) * 100:.2f}%

## 4. 클러스터별 샘플 분포
{cluster_stats_info}

## 5. 성능 지표
- **처리 속도**: {len(input_data) / elapsed_time:.2f} 행/초
- **압축률**: {(1 - output_size / input_size) * 100:.2f}%
- **데이터 보존률**: {len(output_data) / len(input_data) * 100:.2f}%

## 6. 작업 상태
- **상태**: 성공
- **클러스터 샘플링**: 클러스터 샘플링이 성공적으로 완료됨
- **데이터 무결성**: 원본 데이터의 클러스터 구조 유지
"""
    return report

def solution(input_data: StringIO, output_filename: str, settings: dict = None):
    """
    데이터에 클러스터 샘플링을 적용하는 함수.
    
    Parameters:
    - input_data (StringIO): 입력 CSV 데이터
    - output_filename (str): 출력 CSV 파일 경로
    - settings (dict): 클러스터 샘플링 설정
        - cluster_column (str): 클러스터링에 사용할 컬럼 이름
        - n_clusters (int): 클러스터 수
        - sample_size (int): 샘플 크기 (0이면 sample_ratio 사용)
        - sample_ratio (float): 샘플 비율 (0.0 ~ 1.0)
        - random_state (int): 랜덤 시드
    
    Returns:
    - tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] 클러스터 샘플링 작업을 시작합니다.")
    
    # 설정 기본값 설정
    if settings is None:
        settings = {}
    
    cluster_column = settings.get('cluster_column', '')
    n_clusters = settings.get('n_clusters', 5)
    sample_size = settings.get('sample_size', 0)
    sample_ratio = settings.get('sample_ratio', 0.1)
    random_state = settings.get('random_state', None)
    
    print(f"- 클러스터 컬럼: {cluster_column}")
    print(f"- 클러스터 수: {n_clusters}개")
    print(f"- 샘플 크기: {sample_size:,}개" if sample_size > 0 else f"- 샘플 비율: {sample_ratio:.2%}")
    print(f"- 랜덤 시드: {random_state}")
    
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
    
    # 클러스터 컬럼 검증
    if not cluster_column:
        # 자동으로 수치형 컬럼 선택
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_columns:
            raise ValueError("클러스터링에 사용할 수치형 컬럼이 없습니다.")
        cluster_column = numeric_columns[0]
        print(f"- 자동 선택된 클러스터 컬럼: {cluster_column}")
    
    if cluster_column not in df.columns:
        raise ValueError(f"지정된 클러스터 컬럼 '{cluster_column}'이 데이터에 존재하지 않습니다.")
    
    # 클러스터링에 사용할 데이터 준비
    cluster_data = df[cluster_column].values.reshape(-1, 1)
    
    # 데이터 정규화
    scaler = StandardScaler()
    cluster_data_scaled = scaler.fit_transform(cluster_data)
    
    print(f"\n[2/4] 클러스터링을 수행합니다...")
    print(f"- 대상 컬럼: {cluster_column}")
    print(f"- 클러스터 수: {n_clusters}개")
    
    try:
        # K-means 클러스터링
        kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
        cluster_labels = kmeans.fit_predict(cluster_data_scaled)
        
        # 클러스터 ID를 데이터프레임에 추가
        df_with_clusters = df.copy()
        df_with_clusters['cluster_id'] = cluster_labels
        
        print(f"- 클러스터링 완료: {n_clusters}개 클러스터 생성")
        
        # 클러스터별 샘플링
        sampled_dfs = []
        for cluster_id in range(n_clusters):
            cluster_data = df_with_clusters[df_with_clusters['cluster_id'] == cluster_id]
            
            if len(cluster_data) == 0:
                continue
            
            # 클러스터별 샘플 크기 결정
            if sample_size > 0:
                cluster_sample_size = min(sample_size, len(cluster_data))
            else:
                cluster_sample_size = max(1, int(len(cluster_data) * sample_ratio))
            
            # 클러스터에서 샘플링
            if cluster_sample_size >= len(cluster_data):
                cluster_sample = cluster_data
            else:
                cluster_sample = cluster_data.sample(n=cluster_sample_size, random_state=random_state)
            
            sampled_dfs.append(cluster_sample)
            print(f"- 클러스터 {cluster_id}: {len(cluster_data):,}개 → {len(cluster_sample):,}개 샘플")
        
        # 샘플링된 데이터 결합
        sampled_df = pd.concat(sampled_dfs, ignore_index=True)
        
    except Exception as e:
        raise ValueError(f"클러스터 샘플링 실패: {str(e)}")
    
    # 결과 검증
    print(f"\n[3/4] 결과를 검증합니다...")
    print(f"- 원본 컬럼 수: {len(df.columns)}")
    print(f"- 결과 컬럼 수: {len(sampled_df.columns)}")
    print(f"- 행 수 변화: {len(df):,} → {len(sampled_df):,}")
    print(f"- 샘플링 비율: {len(sampled_df) / len(df):.2%}")
    
    # 클러스터별 분포 확인
    cluster_distribution = sampled_df['cluster_id'].value_counts().sort_index()
    print(f"- 클러스터별 샘플 분포: {dict(cluster_distribution)}")
    
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
    print(f"- 클러스터 수: {n_clusters}개")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    
    # 보고서 생성
    report = generate_report(df, sampled_df, output_filename, 
                           input_size, output_size, elapsed_time, settings)
    
    return output_filename, report