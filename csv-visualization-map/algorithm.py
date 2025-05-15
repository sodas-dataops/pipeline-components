import pandas as pd
import folium
from folium.plugins import MarkerCluster
import time
from datetime import datetime

def generate_report(
    df: pd.DataFrame,
    label_column: str,
    lat_column: str,
    lon_column: str,
    output_html: str,
    elapsed_time: float
) -> str:
    """
    지도 시각화 작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - label_column (str): 레이블 컬럼명
    - lat_column (str): 위도 컬럼명
    - lon_column (str): 경도 컬럼명
    - output_html (str): 저장된 HTML 파일 경로
    - elapsed_time (float): 소요 시간 (초)
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    # 위치 데이터 통계 계산
    valid_locations = df.dropna(subset=[lat_column, lon_column])
    total_locations = len(valid_locations)
    unique_labels = valid_locations[label_column].nunique()
    
    report = f"""# 지도 시각화 작업 보고서

## 1. 작업 개요
- **작업 유형**: 지도 시각화
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **행 수**: {len(df):,}행
- **컬럼 수**: {len(df.columns)}개
- **컬럼 목록**: {', '.join(df.columns)}

## 3. 시각화 설정
- **레이블 컬럼**: {label_column}
- **위도 컬럼**: {lat_column}
- **경도 컬럼**: {lon_column}

## 4. 처리 결과
- **출력 파일**: {output_html}
- **총 위치 수**: {total_locations:,}개
- **고유 레이블 수**: {unique_labels:,}개
- **위도 범위**: {valid_locations[lat_column].min():.4f} ~ {valid_locations[lat_column].max():.4f}
- **경도 범위**: {valid_locations[lon_column].min():.4f} ~ {valid_locations[lon_column].max():.4f}
- **중심 좌표**: ({valid_locations[lat_column].mean():.4f}, {valid_locations[lon_column].mean():.4f})

## 5. 성능 지표
- **처리 속도**: {total_locations / elapsed_time:.2f} 위치/초
- **메모리 사용량**: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB

## 6. 작업 상태
- **상태**: 성공
- **처리 결과**: 지도가 성공적으로 생성됨
"""
    return report

def solution(data: str, label_column: str, lat_column: str, lon_column: str, output_html: str) -> tuple:
    """
    CSV 파일에서 위치 데이터를 지도에 시각화하여 이미지로 저장하는 함수.
    
    Parameters:
    - data: CSV 파일 경로
    - label_column: 마커에 표시할 레이블 컬럼명
    - lat_column: 위도 컬럼명
    - lon_column: 경도 컬럼명
    - output_html: 저장할 HTML 파일 경로
    
    Returns:
    - tuple: (HTML 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    
    # CSV 파일 로드
    df = pd.read_csv(data)
    
    # 지도의 중심을 평균 위도와 경도로 설정
    center_lat = df[lat_column].mean()
    center_lon = df[lon_column].mean()
    map_ = folium.Map(location=[center_lat, center_lon], tiles='openstreetmap', zoom_start=8)

    # MarkerCluster 객체 생성
    marker_cluster = MarkerCluster()

    # CSV의 각 위치에 마커 추가
    for _, row in df.iterrows():
        # if pd.isna(row[lat_column]) or pd.isna(row[lon_column]):
        #     continue
        # folium.Marker(
        #     location=[row[lat_column], row[lon_column]],
        #     popup=folium.Popup(row[label_column], max_width=300)
        # ).add_to(marker_cluster)

        if pd.isna(row[lat_column]) or pd.isna(row[lon_column]):
            continue

        # 장애인 포털 데모를 위해 임시로 하이퍼링크 추가
        # 링크 주소와 텍스트를 구성
        label_text = str(row[label_column])
        link_url = f"http://dataops-barrier-free-job-portal.221.154.134.31.traefik.me:10019/search/job?company_name={label_text}"
        popup_html = f'<a href="{link_url}" target="_top">{label_text}</a>'

        folium.Marker(
            location=[row[lat_column], row[lon_column]],
            popup=folium.Popup(popup_html, max_width=300)
        ).add_to(marker_cluster)

    # MarkerCluster를 지도에 추가
    map_.add_child(marker_cluster)
    
    # HTML로 저장
    map_.save(output_html)

    # 소요 시간 계산
    end_time = time.time()
    elapsed_time = end_time - start_time

    # 보고서 생성
    report = generate_report(
        df=df,
        label_column=label_column,
        lat_column=lat_column,
        lon_column=lon_column,
        output_html=output_html,
        elapsed_time=elapsed_time
    )

    return output_html, report


