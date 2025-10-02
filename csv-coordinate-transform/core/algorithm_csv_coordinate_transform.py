import pandas as pd
import numpy as np
import pyproj
from pyproj import Transformer, CRS
import time
import os
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List
from io import StringIO

def transform_coordinates(df: pd.DataFrame, x_col: str, y_col: str,
                         source_crs: str, target_crs: str,
                         x_output_col: str = None, y_output_col: str = None) -> pd.DataFrame:
    """
    좌표계를 변환하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 입력 데이터프레임
    - x_col (str): X좌표 컬럼명
    - y_col (str): Y좌표 컬럼명
    - source_crs (str): 소스 좌표계
    - target_crs (str): 타겟 좌표계
    - x_output_col (str): 출력 X좌표 컬럼명
    - y_output_col (str): 출력 Y좌표 컬럼명
    
    Returns:
    - pd.DataFrame: 변환된 좌표가 추가된 데이터프레임
    """
    result_df = df.copy()
    
    # 출력 컬럼명 설정
    if x_output_col is None:
        x_output_col = f"{x_col}_{target_crs.replace(':', '_')}_x"
    if y_output_col is None:
        y_output_col = f"{y_col}_{target_crs.replace(':', '_')}_y"
    
    try:
        # Transformer 생성
        transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)
        
        # 좌표 변환
        x_transformed, y_transformed = transformer.transform(
            df[x_col].values, df[y_col].values
        )
        
        result_df[x_output_col] = x_transformed
        result_df[y_output_col] = y_transformed
        
        # 변환 정보 추가
        result_df['source_crs'] = source_crs
        result_df['target_crs'] = target_crs
        
    except Exception as e:
        raise ValueError(f"좌표 변환 실패: {str(e)}")
    
    return result_df

def wgs84_to_utm(df: pd.DataFrame, lat_col: str, lon_col: str,
                utm_zone: Optional[int] = None, utm_hemisphere: str = 'N') -> pd.DataFrame:
    """
    WGS84 좌표를 UTM 좌표로 변환하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 입력 데이터프레임
    - lat_col (str): 위도 컬럼명
    - lon_col (str): 경도 컬럼명
    - utm_zone (int): UTM 존 번호 (None이면 자동 계산)
    - utm_hemisphere (str): UTM 반구 ('N' 또는 'S')
    
    Returns:
    - pd.DataFrame: UTM 좌표가 추가된 데이터프레임
    """
    result_df = df.copy()
    
    # UTM 존 자동 계산
    if utm_zone is None:
        utm_zone = int((df[lon_col].mean() + 180) / 6) + 1
    
    # UTM 좌표계 정의
    utm_crs = f"EPSG:{32600 + utm_zone}" if utm_hemisphere == 'N' else f"EPSG:{32700 + utm_zone}"
    
    try:
        # WGS84 to UTM 변환
        transformer = Transformer.from_crs("EPSG:4326", utm_crs, always_xy=True)
        utm_x, utm_y = transformer.transform(df[lon_col].values, df[lat_col].values)
        
        result_df['utm_x'] = utm_x
        result_df['utm_y'] = utm_y
        result_df['utm_zone'] = utm_zone
        result_df['utm_hemisphere'] = utm_hemisphere
        
    except Exception as e:
        raise ValueError(f"WGS84 to UTM 변환 실패: {str(e)}")
    
    return result_df

def utm_to_wgs84(df: pd.DataFrame, utm_x_col: str, utm_y_col: str,
                utm_zone: int, utm_hemisphere: str = 'N') -> pd.DataFrame:
    """
    UTM 좌표를 WGS84 좌표로 변환하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 입력 데이터프레임
    - utm_x_col (str): UTM X좌표 컬럼명
    - utm_y_col (str): UTM Y좌표 컬럼명
    - utm_zone (int): UTM 존 번호
    - utm_hemisphere (str): UTM 반구 ('N' 또는 'S')
    
    Returns:
    - pd.DataFrame: WGS84 좌표가 추가된 데이터프레임
    """
    result_df = df.copy()
    
    # UTM 좌표계 정의
    utm_crs = f"EPSG:{32600 + utm_zone}" if utm_hemisphere == 'N' else f"EPSG:{32700 + utm_zone}"
    
    try:
        # UTM to WGS84 변환
        transformer = Transformer.from_crs(utm_crs, "EPSG:4326", always_xy=True)
        lon, lat = transformer.transform(df[utm_x_col].values, df[utm_y_col].values)
        
        result_df['wgs84_lon'] = lon
        result_df['wgs84_lat'] = lat
        
    except Exception as e:
        raise ValueError(f"UTM to WGS84 변환 실패: {str(e)}")
    
    return result_df

def generate_report(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    transform_type: str,
    output_file_name: str,
    settings: Dict[str, Any],
    elapsed_time: float
) -> str:
    """
    좌표 변환 작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - x_column (str): X좌표 컬럼명
    - y_column (str): Y좌표 컬럼명
    - transform_type (str): 변환 유형
    - output_file_name (str): 저장된 파일 경로
    - settings (Dict[str, Any]): 사용된 설정
    - elapsed_time (float): 소요 시간 (초)
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    # 기본 통계
    x_stats = df[x_column].describe()
    y_stats = df[y_column].describe()
    
    # 변환 결과 요약
    transform_summary = ""
    if 'utm_x' in df.columns:
        transform_summary += f"- **UTM X 좌표 범위**: {df['utm_x'].min():.2f} ~ {df['utm_x'].max():.2f}\n"
        transform_summary += f"- **UTM Y 좌표 범위**: {df['utm_y'].min():.2f} ~ {df['utm_y'].max():.2f}\n"
        transform_summary += f"- **UTM 존**: {df['utm_zone'].iloc[0] if 'utm_zone' in df.columns else 'N/A'}\n"
    
    if 'wgs84_lon' in df.columns:
        transform_summary += f"- **WGS84 경도 범위**: {df['wgs84_lon'].min():.6f}° ~ {df['wgs84_lon'].max():.6f}°\n"
        transform_summary += f"- **WGS84 위도 범위**: {df['wgs84_lat'].min():.6f}° ~ {df['wgs84_lat'].max():.6f}°\n"
    
    report = f"""# 좌표 변환 작업 보고서

## 1. 작업 개요
- **작업 유형**: {transform_type}
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **행 수**: {len(df):,}행
- **컬럼 수**: {len(df.columns)}개
- **X좌표 컬럼**: {x_column}
- **Y좌표 컬럼**: {y_column}

## 3. 변환 설정
- **변환 유형**: {transform_type}
- **소스 좌표계**: {settings.get('source_crs', 'EPSG:4326')}
- **타겟 좌표계**: {settings.get('target_crs', 'EPSG:3857')}

## 4. 입력 좌표 범위
### X좌표 ({x_column})
- **최솟값**: {x_stats['min']:.6f}
- **최댓값**: {x_stats['max']:.6f}
- **평균**: {x_stats['mean']:.6f}
- **표준편차**: {x_stats['std']:.6f}

### Y좌표 ({y_column})
- **최솟값**: {y_stats['min']:.6f}
- **최댓값**: {y_stats['max']:.6f}
- **평균**: {y_stats['mean']:.6f}
- **표준편차**: {y_stats['std']:.6f}

## 5. 변환 결과
{transform_summary}

## 6. 성능 지표
- **처리 속도**: {len(df) / elapsed_time:.2f} 행/초
- **메모리 사용량**: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB

## 7. 작업 상태
- **상태**: 성공
- **처리 결과**: {transform_type} 변환이 성공적으로 완료됨
- **출력 파일**: {output_file_name}
"""
    return report

def solution(
    data: object,
    x_column: str,
    y_column: str,
    output_file_name: str,
    transform_type: str = 'custom',
    settings: Optional[Dict[str, Any]] = None
) -> Tuple[str, str]:
    """
    CSV 파일에서 좌표 변환을 수행하는 함수.
    
    Parameters:
    - data: CSV 파일 경로 또는 StringIO 객체
    - x_column: X좌표 컬럼명
    - y_column: Y좌표 컬럼명
    - output_file_name: 저장할 파일 이름
    - transform_type: 변환 유형 ('wgs84_to_utm', 'utm_to_wgs84', 'custom')
    - settings: 변환 설정 (선택사항)
    
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
    if x_column not in df.columns:
        raise ValueError(f"X좌표 컬럼 '{x_column}'이 데이터에 존재하지 않습니다.")
    if y_column not in df.columns:
        raise ValueError(f"Y좌표 컬럼 '{y_column}'이 데이터에 존재하지 않습니다.")
    
    # 결측값 제거
    initial_count = len(df)
    df = df.dropna(subset=[x_column, y_column])
    if len(df) < initial_count:
        print(f"- 경고: {initial_count - len(df)}개의 결측값이 있는 행이 제거되었습니다.")
    
    print(f"- 유효한 데이터 포인트: {len(df):,}개")
    
    # 좌표 변환 수행
    if transform_type == 'wgs84_to_utm':
        print("\n[변환] WGS84 to UTM 변환을 수행합니다...")
        df = wgs84_to_utm(
            df, y_column, x_column,  # lat, lon 순서
            settings.get('utm_zone'),
            settings.get('utm_hemisphere', 'N')
        )
        
    elif transform_type == 'utm_to_wgs84':
        print("\n[변환] UTM to WGS84 변환을 수행합니다...")
        df = utm_to_wgs84(
            df, x_column, y_column,
            settings.get('utm_zone', 52),
            settings.get('utm_hemisphere', 'N')
        )
        
    elif transform_type == 'custom':
        print("\n[변환] 사용자 정의 좌표 변환을 수행합니다...")
        df = transform_coordinates(
            df, x_column, y_column,
            settings.get('source_crs', 'EPSG:4326'),
            settings.get('target_crs', 'EPSG:3857'),
            settings.get('x_output_col'),
            settings.get('y_output_col')
        )
    
    else:
        raise ValueError(f"지원하지 않는 변환 유형입니다: {transform_type}")
    
    # 결과 저장
    print(f"\n[저장] 결과를 저장합니다...")
    df.to_csv(output_file_name, index=False, encoding='utf-8')
    
    # 소요 시간 계산
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 보고서 생성
    report = generate_report(
        df=df,
        x_column=x_column,
        y_column=y_column,
        transform_type=transform_type,
        output_file_name=output_file_name,
        settings=settings,
        elapsed_time=elapsed_time
    )
    
    return output_file_name, report