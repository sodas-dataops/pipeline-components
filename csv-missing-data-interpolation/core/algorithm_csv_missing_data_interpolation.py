import pandas as pd
import numpy as np
import json
import time
import os
from datetime import datetime
from io import StringIO
from sklearn.impute import SimpleImputer, KNNImputer
from scipy import interpolate

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
    interpolation_method = settings.get('interpolation_method', 'mean') if settings else 'mean'
    target_columns = settings.get('target_columns', []) if settings else []
    fill_direction = settings.get('fill_direction', 'forward') if settings else 'forward'
    custom_value = settings.get('custom_value', 0) if settings else 0

    # 결측값 보간 설정 정보
    columns_info = f"- **대상 컬럼**: {', '.join(target_columns)}" if target_columns else "- **대상 컬럼**: 전체 컬럼"
    method_info = f"- **보간 방법**: {interpolation_method}"
    direction_info = f"- **채움 방향**: {fill_direction}" if interpolation_method in ['forward', 'backward'] else ""
    custom_info = f"- **사용자 정의 값**: {custom_value}" if interpolation_method == 'custom' else ""
    
    # 결측값 통계
    missing_before = input_data.isnull().sum().sum()
    missing_after = output_data.isnull().sum().sum()
    filled_count = missing_before - missing_after
    
    report = f"""# CSV 결측값 보간 작업 보고서

## 1. 작업 개요
- **작업 유형**: CSV 결측값 보간
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초
- **보간된 결측값**: {filled_count:,}개
- **보간 성공률**: {(filled_count / missing_before * 100) if missing_before > 0 else 0:.2f}%
{columns_info}
{method_info}
{direction_info}
{custom_info}

## 2. 입력 데이터
- **데이터 크기**: {input_size / 1024:.2f} KB
- **행 수**: {len(input_data):,}
- **열 수**: {len(input_data.columns)}
- **열 이름**: {', '.join(input_data.columns)}
- **결측값 수**: {missing_before:,}개

## 3. 보간 결과
- **출력 파일**: {output_filename}
- **파일 크기**: {output_size / 1024:.2f} KB
- **행 수**: {len(output_data):,}
- **열 수**: {len(output_data.columns)}
- **남은 결측값**: {missing_after:,}개
- **데이터 보존률**: {len(output_data) / len(input_data) * 100:.2f}%

## 4. 성능 지표
- **처리 속도**: {len(input_data) / elapsed_time:.2f} 행/초
- **압축률**: {(1 - output_size / input_size) * 100:.2f}%
- **보간 효율**: {filled_count / elapsed_time:.2f} 값/초

## 5. 작업 상태
- **상태**: 성공
- **결측값 보간**: 결측값 보간이 성공적으로 완료됨
- **데이터 무결성**: 원본 데이터의 구조와 타입 유지
"""
    return report

def solution(input_data: StringIO, output_filename: str, settings: dict = None):
    """
    CSV 데이터의 결측값을 보간하는 함수.
    
    Parameters:
    - input_data (StringIO): 입력 CSV 데이터
    - output_filename (str): 출력 CSV 파일 경로
    - settings (dict): 보간 설정
        - interpolation_method (str): 보간 방법 ('mean', 'median', 'mode', 'forward', 'backward', 'linear', 'knn', 'custom')
        - target_columns (list): 보간할 컬럼 목록
        - fill_direction (str): 채움 방향 ('forward', 'backward')
        - custom_value: 사용자 정의 값
        - knn_neighbors (int): KNN 이웃 수
    
    Returns:
    - tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] 결측값 보간 작업을 시작합니다.")
    
    # 설정 기본값 설정
    if settings is None:
        settings = {}
    
    interpolation_method = settings.get('interpolation_method', 'mean')
    target_columns = settings.get('target_columns', [])
    fill_direction = settings.get('fill_direction', 'forward')
    custom_value = settings.get('custom_value', 0)
    knn_neighbors = settings.get('knn_neighbors', 5)
    
    print(f"- 보간 방법: {interpolation_method}")
    if target_columns:
        print(f"- 대상 컬럼: {', '.join(target_columns)}")
    if interpolation_method in ['forward', 'backward']:
        print(f"- 채움 방향: {fill_direction}")
    if interpolation_method == 'custom':
        print(f"- 사용자 정의 값: {custom_value}")
    if interpolation_method == 'knn':
        print(f"- KNN 이웃 수: {knn_neighbors}")
    
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
    
    # 결측값 통계
    missing_before = df.isnull().sum().sum()
    print(f"- 결측값 수: {missing_before:,}개")
    
    if missing_before == 0:
        print("- 결측값이 없습니다. 원본 데이터를 그대로 반환합니다.")
        interpolated_df = df.copy()
    else:
        # 대상 컬럼 검증
        if target_columns:
            missing_cols = [col for col in target_columns if col not in df.columns]
            if missing_cols:
                raise ValueError(f"대상 컬럼이 존재하지 않습니다: {missing_cols}")
            columns_to_process = target_columns
        else:
            columns_to_process = df.columns.tolist()
        
        print(f"- 보간 대상 컬럼: {', '.join(columns_to_process)}")
        
        # 결측값 보간 수행
        print(f"\n[2/4] 결측값 보간을 수행합니다...")
        
        try:
            interpolated_df = df.copy()
            
            for col in columns_to_process:
                if interpolated_df[col].isnull().any():
                    print(f"- 컬럼 '{col}' 보간 중...")
                    
                    if interpolation_method == 'mean':
                        interpolated_df[col] = interpolated_df[col].fillna(interpolated_df[col].mean())
                    elif interpolation_method == 'median':
                        interpolated_df[col] = interpolated_df[col].fillna(interpolated_df[col].median())
                    elif interpolation_method == 'mode':
                        mode_value = interpolated_df[col].mode()
                        if len(mode_value) > 0:
                            interpolated_df[col] = interpolated_df[col].fillna(mode_value[0])
                        else:
                            print(f"  경고: 컬럼 '{col}'에 모드 값이 없습니다.")
                    elif interpolation_method == 'forward':
                        interpolated_df[col] = interpolated_df[col].fillna(method='ffill')
                    elif interpolation_method == 'backward':
                        interpolated_df[col] = interpolated_df[col].fillna(method='bfill')
                    elif interpolation_method == 'linear':
                        if interpolated_df[col].dtype in ['int64', 'float64']:
                            interpolated_df[col] = interpolated_df[col].interpolate(method='linear')
                        else:
                            print(f"  경고: 컬럼 '{col}'은 숫자형이 아니므로 선형 보간을 적용할 수 없습니다.")
                    elif interpolation_method == 'knn':
                        if interpolated_df[col].dtype in ['int64', 'float64']:
                            # KNN 보간을 위한 임시 데이터프레임 생성
                            temp_df = interpolated_df.select_dtypes(include=[np.number])
                            if len(temp_df.columns) > 0:
                                knn_imputer = KNNImputer(n_neighbors=knn_neighbors)
                                temp_imputed = knn_imputer.fit_transform(temp_df)
                                temp_imputed_df = pd.DataFrame(temp_imputed, columns=temp_df.columns, index=temp_df.index)
                                interpolated_df[col] = temp_imputed_df[col]
                            else:
                                print(f"  경고: KNN 보간을 위한 숫자형 컬럼이 없습니다.")
                        else:
                            print(f"  경고: 컬럼 '{col}'은 숫자형이 아니므로 KNN 보간을 적용할 수 없습니다.")
                    elif interpolation_method == 'custom':
                        interpolated_df[col] = interpolated_df[col].fillna(custom_value)
                    else:
                        raise ValueError(f"지원하지 않는 보간 방법: {interpolation_method}")
            
        except Exception as e:
            raise ValueError(f"결측값 보간 실패: {str(e)}")
    
    # 보간 결과 검증
    print(f"\n[3/4] 보간 결과를 검증합니다...")
    
    missing_after = interpolated_df.isnull().sum().sum()
    filled_count = missing_before - missing_after
    
    print(f"- 보간된 결측값: {filled_count:,}개")
    print(f"- 남은 결측값: {missing_after:,}개")
    print(f"- 보간 성공률: {(filled_count / missing_before * 100) if missing_before > 0 else 0:.2f}%")

    # CSV로 저장
    print(f"\n[4/4] 결과를 저장합니다...")
    try:
        interpolated_df.to_csv(output_filename, index=False, encoding='utf-8')
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
    print(f"- 보간된 데이터: {len(interpolated_df):,}행")
    print(f"- 보간된 결측값: {filled_count:,}개")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    
    # 보고서 생성
    report = generate_report(df, interpolated_df, output_filename, 
                           input_size, output_size, elapsed_time, settings)
    
    return output_filename, report