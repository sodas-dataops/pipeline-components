import pandas as pd
import numpy as np
import time
import os
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List
from io import StringIO

def validate_coordinates(df: pd.DataFrame, lat_col: str, lon_col: str,
                        validation_rules: Dict[str, Any]) -> pd.DataFrame:
    """
    좌표 유효성을 검증하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 입력 데이터프레임
    - lat_col (str): 위도 컬럼명
    - lon_col (str): 경도 컬럼명
    - validation_rules (Dict[str, Any]): 검증 규칙
    
    Returns:
    - pd.DataFrame: 검증 결과가 추가된 데이터프레임
    """
    result_df = df.copy()
    
    # 기본 검증 플래그 초기화
    result_df['is_valid_coordinate'] = True
    result_df['validation_errors'] = ''
    
    # 1. 결측값 검증
    if validation_rules.get('check_missing', True):
        missing_lat = result_df[lat_col].isna()
        missing_lon = result_df[lon_col].isna()
        missing_coords = missing_lat | missing_lon
        
        result_df.loc[missing_coords, 'is_valid_coordinate'] = False
        result_df.loc[missing_lat, 'validation_errors'] += 'Missing latitude; '
        result_df.loc[missing_lon, 'validation_errors'] += 'Missing longitude; '
    
    # 2. 범위 검증
    if validation_rules.get('check_range', True):
        # 위도 범위 (-90 ~ 90)
        invalid_lat = (result_df[lat_col] < -90) | (result_df[lat_col] > 90)
        # 경도 범위 (-180 ~ 180)
        invalid_lon = (result_df[lon_col] < -180) | (result_df[lon_col] > 180)
        
        result_df.loc[invalid_lat, 'is_valid_coordinate'] = False
        result_df.loc[invalid_lon, 'is_valid_coordinate'] = False
        result_df.loc[invalid_lat, 'validation_errors'] += 'Invalid latitude range; '
        result_df.loc[invalid_lon, 'validation_errors'] += 'Invalid longitude range; '
    
    # 3. 중복 좌표 검증
    if validation_rules.get('check_duplicates', False):
        coord_duplicates = result_df.duplicated(subset=[lat_col, lon_col], keep=False)
        result_df.loc[coord_duplicates, 'is_duplicate'] = True
        result_df.loc[coord_duplicates, 'validation_errors'] += 'Duplicate coordinates; '
    
    # 4. 극값 검증 (0,0 좌표 등)
    if validation_rules.get('check_extreme_values', True):
        extreme_coords = ((result_df[lat_col] == 0) & (result_df[lon_col] == 0)) | \
                        ((result_df[lat_col] == 90) & (result_df[lon_col] == 180)) | \
                        ((result_df[lat_col] == -90) & (result_df[lon_col] == -180))
        
        result_df.loc[extreme_coords, 'is_extreme_value'] = True
        result_df.loc[extreme_coords, 'validation_errors'] += 'Extreme coordinate values; '
    
    # 5. 정밀도 검증
    if validation_rules.get('check_precision', False):
        precision_threshold = validation_rules.get('precision_threshold', 6)
        
        # 소수점 자릿수 확인
        lat_precision = result_df[lat_col].astype(str).str.split('.').str[1].str.len().fillna(0)
        lon_precision = result_df[lon_col].astype(str).str.split('.').str[1].str.len().fillna(0)
        
        low_precision = (lat_precision < precision_threshold) | (lon_precision < precision_threshold)
        result_df.loc[low_precision, 'is_low_precision'] = True
        result_df.loc[low_precision, 'validation_errors'] += 'Low precision coordinates; '
    
    # 6. 지리적 일관성 검증
    if validation_rules.get('check_geographic_consistency', False):
        # 같은 지역 내 좌표들의 분산이 너무 큰 경우
        region_col = validation_rules.get('region_column', '')
        if region_col and region_col in df.columns:
            for region in df[region_col].unique():
                region_mask = df[region_col] == region
                region_coords = df[region_mask]
                
                if len(region_coords) > 1:
                    lat_std = region_coords[lat_col].std()
                    lon_std = region_coords[lon_col].std()
                    
                    # 표준편차가 임계값을 초과하는 경우
                    if lat_std > validation_rules.get('max_lat_std', 1.0) or \
                       lon_std > validation_rules.get('max_lon_std', 1.0):
                        result_df.loc[region_mask, 'is_inconsistent_region'] = True
                        result_df.loc[region_mask, 'validation_errors'] += 'Inconsistent region coordinates; '
    
    # 검증 에러 메시지 정리
    result_df['validation_errors'] = result_df['validation_errors'].str.rstrip('; ')
    
    return result_df

def generate_report(
    df: pd.DataFrame,
    lat_column: str,
    lon_column: str,
    output_file_name: str,
    settings: Dict[str, Any],
    elapsed_time: float
) -> str:
    """
    좌표 검증 작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - lat_column (str): 위도 컬럼명
    - lon_column (str): 경도 컬럼명
    - output_file_name (str): 저장된 파일 경로
    - settings (Dict[str, Any]): 사용된 설정
    - elapsed_time (float): 소요 시간 (초)
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    # 기본 통계
    total_records = len(df)
    valid_records = df['is_valid_coordinate'].sum() if 'is_valid_coordinate' in df.columns else total_records
    invalid_records = total_records - valid_records
    
    # 검증 결과 요약
    validation_summary = f"- **총 레코드 수**: {total_records:,}개\n"
    validation_summary += f"- **유효한 좌표**: {valid_records:,}개 ({valid_records/total_records*100:.1f}%)\n"
    validation_summary += f"- **무효한 좌표**: {invalid_records:,}개 ({invalid_records/total_records*100:.1f}%)\n"
    
    # 에러 유형별 통계
    if 'validation_errors' in df.columns:
        error_types = {}
        for errors in df[df['validation_errors'] != '']['validation_errors']:
            for error in errors.split('; '):
                if error:
                    error_types[error] = error_types.get(error, 0) + 1
        
        if error_types:
            validation_summary += "\n### 에러 유형별 통계\n"
            for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
                validation_summary += f"- **{error_type}**: {count:,}개\n"
    
    # 좌표 범위 통계
    lat_stats = df[lat_column].describe()
    lon_stats = df[lon_column].describe()
    
    report = f"""# 좌표 검증 작업 보고서

## 1. 작업 개요
- **작업 유형**: 좌표 유효성 검증
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **행 수**: {total_records:,}행
- **컬럼 수**: {len(df.columns)}개
- **위도 컬럼**: {lat_column}
- **경도 컬럼**: {lon_column}

## 3. 검증 설정
- **결측값 검증**: {settings.get('check_missing', True)}
- **범위 검증**: {settings.get('check_range', True)}
- **중복 검증**: {settings.get('check_duplicates', False)}
- **극값 검증**: {settings.get('check_extreme_values', True)}
- **정밀도 검증**: {settings.get('check_precision', False)}
- **지리적 일관성 검증**: {settings.get('check_geographic_consistency', False)}

## 4. 좌표 범위
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

## 5. 검증 결과
{validation_summary}

## 6. 성능 지표
- **처리 속도**: {total_records / elapsed_time:.2f} 행/초
- **메모리 사용량**: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB

## 7. 작업 상태
- **상태**: 성공
- **처리 결과**: 좌표 검증이 성공적으로 완료됨
- **출력 파일**: {output_file_name}
"""
    return report

def solution(
    data: object,
    lat_column: str,
    lon_column: str,
    output_file_name: str,
    settings: Optional[Dict[str, Any]] = None
) -> Tuple[str, str]:
    """
    CSV 파일에서 좌표 유효성 검증을 수행하는 함수.
    
    Parameters:
    - data: CSV 파일 경로 또는 StringIO 객체
    - lat_column: 위도 컬럼명
    - lon_column: 경도 컬럼명
    - output_file_name: 저장할 파일 이름
    - settings: 검증 설정 (선택사항)
    
    Returns:
    - tuple: (출력 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    
    # 기본 설정
    if settings is None:
        settings = {}
    
    # 기본 검증 규칙 설정
    validation_rules = {
        'check_missing': settings.get('check_missing', True),
        'check_range': settings.get('check_range', True),
        'check_duplicates': settings.get('check_duplicates', False),
        'check_extreme_values': settings.get('check_extreme_values', True),
        'check_precision': settings.get('check_precision', False),
        'precision_threshold': settings.get('precision_threshold', 6),
        'check_geographic_consistency': settings.get('check_geographic_consistency', False),
        'region_column': settings.get('region_column', ''),
        'max_lat_std': settings.get('max_lat_std', 1.0),
        'max_lon_std': settings.get('max_lon_std', 1.0)
    }
    
    # CSV 데이터 로드
    df = pd.read_csv(data)
    
    # 컬럼 존재 확인
    if lat_column not in df.columns:
        raise ValueError(f"위도 컬럼 '{lat_column}'이 데이터에 존재하지 않습니다.")
    if lon_column not in df.columns:
        raise ValueError(f"경도 컬럼 '{lon_column}'이 데이터에 존재하지 않습니다.")
    
    print(f"- 총 데이터 포인트: {len(df):,}개")
    
    # 좌표 검증 수행
    print("\n[검증] 좌표 유효성을 검증합니다...")
    df = validate_coordinates(df, lat_column, lon_column, validation_rules)
    
    # 검증 결과 요약
    valid_count = df['is_valid_coordinate'].sum()
    invalid_count = len(df) - valid_count
    
    print(f"- 유효한 좌표: {valid_count:,}개 ({valid_count/len(df)*100:.1f}%)")
    print(f"- 무효한 좌표: {invalid_count:,}개 ({invalid_count/len(df)*100:.1f}%)")
    
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
        output_file_name=output_file_name,
        settings=settings,
        elapsed_time=elapsed_time
    )
    
    return output_file_name, report