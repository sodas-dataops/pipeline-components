import pandas as pd
import numpy as np
import json
import time
import os
from datetime import datetime
from io import StringIO
from scipy import stats
from scipy.special import boxcox1p
from sklearn.preprocessing import PowerTransformer

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
    transform_method = settings.get('transform_method', 'log') if settings else 'log'
    target_columns = settings.get('target_columns', []) if settings else []
    lambda_param = settings.get('lambda_param', None) if settings else None
    add_constant = settings.get('add_constant', 1) if settings else 1

    # 변환 컬럼 정보
    target_info = f"- **대상 컬럼**: {', '.join(target_columns)}" if target_columns else "- **대상 컬럼**: 모든 수치형 컬럼"
    lambda_info = f"- **Lambda 파라미터**: {lambda_param}" if lambda_param is not None else ""
    
    report = f"""# 분포 변환 작업 보고서

## 1. 작업 개요
- **작업 유형**: 분포 변환
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초
- **변환 방법**: {transform_method}
- **대상 컬럼 수**: {len(target_columns) if target_columns else '모든 수치형'}
- **상수 추가**: {add_constant}
{target_info}
{lambda_info}

## 2. 입력 데이터
- **데이터 크기**: {input_size / 1024:.2f} KB
- **행 수**: {len(input_data):,}
- **열 수**: {len(input_data.columns)}
- **열 이름**: {', '.join(input_data.columns)}

## 3. 변환 결과
- **출력 파일**: {output_filename}
- **파일 크기**: {output_size / 1024:.2f} KB
- **행 수**: {len(output_data):,}
- **열 수**: {len(output_data.columns)}
- **데이터 보존률**: {len(output_data) / len(input_data) * 100:.2f}%

## 4. 성능 지표
- **처리 속도**: {len(input_data) / elapsed_time:.2f} 행/초
- **압축률**: {(1 - output_size / input_size) * 100:.2f}%
- **데이터 보존률**: {len(output_data) / len(input_data) * 100:.2f}%

## 5. 작업 상태
- **상태**: 성공
- **변환**: 분포 변환이 성공적으로 완료됨
- **데이터 무결성**: 원본 데이터의 구조 유지
"""
    return report

def solution(input_data: StringIO, output_filename: str, settings: dict = None):
    """
    수치형 데이터에 분포 변환을 적용하는 함수.
    
    Parameters:
    - input_data (StringIO): 입력 CSV 데이터
    - output_filename (str): 출력 CSV 파일 경로
    - settings (dict): 변환 설정
        - transform_method (str): 변환 방법 ('log', 'sqrt', 'box_cox', 'power', 'yeo_johnson')
        - target_columns (list): 대상 컬럼 목록
        - lambda_param (float): Box-Cox 변환의 lambda 파라미터
        - add_constant (float): 로그/제곱근 변환 시 추가할 상수
    
    Returns:
    - tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] 분포 변환 작업을 시작합니다.")
    
    # 설정 기본값 설정
    if settings is None:
        settings = {}
    
    transform_method = settings.get('transform_method', 'log')
    target_columns = settings.get('target_columns', [])
    lambda_param = settings.get('lambda_param', None)
    add_constant = settings.get('add_constant', 1)
    
    print(f"- 변환 방법: {transform_method}")
    print(f"- 대상 컬럼: {target_columns if target_columns else '모든 수치형 컬럼'}")
    if lambda_param is not None:
        print(f"- Lambda 파라미터: {lambda_param}")
    print(f"- 상수 추가: {add_constant}")
    
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
    
    # 대상 컬럼 결정
    if not target_columns:
        # 모든 수치형 컬럼 선택
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        target_columns = numeric_columns
        print(f"- 자동 선택된 수치형 컬럼: {target_columns}")
    else:
        # 지정된 컬럼 검증
        missing_columns = [col for col in target_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"지정된 컬럼이 데이터에 존재하지 않습니다: {missing_columns}")
        
        # 수치형이 아닌 컬럼 경고
        non_numeric = [col for col in target_columns if not pd.api.types.is_numeric_dtype(df[col])]
        if non_numeric:
            print(f"- 경고: 다음 컬럼은 수치형이 아닙니다: {non_numeric}")
    
    if not target_columns:
        print("- 경고: 변환할 수치형 컬럼이 없습니다.")
        # 원본 데이터를 그대로 저장
        df.to_csv(output_filename, index=False, encoding='utf-8')
        output_size = os.path.getsize(output_filename)
        elapsed_time = time.time() - start_time
        report = generate_report(df, df, output_filename, input_size, output_size, elapsed_time, settings)
        return output_filename, report
    
    print(f"\n[2/4] 분포 변환을 수행합니다...")
    print(f"- 대상 컬럼: {target_columns}")
    
    try:
        # 변환된 데이터프레임 생성
        transformed_df = df.copy()
        
        for col in target_columns:
            print(f"- {col} 변환 중...")
            
            # 결측값이 있는 경우 경고
            if df[col].isna().any():
                print(f"  경고: {col} 컬럼에 결측값이 있습니다.")
            
            # 변환 방법에 따른 처리
            if transform_method == 'log':
                # 로그 변환
                if (df[col] + add_constant <= 0).any():
                    print(f"  경고: {col} 컬럼에 0 이하의 값이 있어 변환할 수 없습니다.")
                    continue
                transformed_df[col] = np.log(df[col] + add_constant)
                
            elif transform_method == 'sqrt':
                # 제곱근 변환
                if (df[col] + add_constant < 0).any():
                    print(f"  경고: {col} 컬럼에 음수 값이 있어 변환할 수 없습니다.")
                    continue
                transformed_df[col] = np.sqrt(df[col] + add_constant)
                
            elif transform_method == 'box_cox':
                # Box-Cox 변환
                if (df[col] <= 0).any():
                    print(f"  경고: {col} 컬럼에 0 이하의 값이 있어 Box-Cox 변환할 수 없습니다.")
                    continue
                
                if lambda_param is not None:
                    # 고정된 lambda 사용
                    transformed_df[col] = stats.boxcox(df[col], lmbda=lambda_param)
                else:
                    # 최적 lambda 자동 계산
                    transformed_data, fitted_lambda = stats.boxcox(df[col])
                    transformed_df[col] = transformed_data
                    print(f"  최적 lambda: {fitted_lambda:.4f}")
                
            elif transform_method == 'power':
                # 거듭제곱 변환
                if lambda_param is None:
                    lambda_param = 0.5  # 기본값
                transformed_df[col] = np.power(df[col] + add_constant, lambda_param)
                
            elif transform_method == 'yeo_johnson':
                # Yeo-Johnson 변환
                pt = PowerTransformer(method='yeo-johnson', standardize=False)
                transformed_df[col] = pt.fit_transform(df[[col]]).flatten()
                
            else:
                raise ValueError(f"지원하지 않는 변환 방법: {transform_method}")
            
            print(f"  {col} 변환 완료")
        
    except Exception as e:
        raise ValueError(f"변환 실패: {str(e)}")
    
    # 변환 결과 검증
    print(f"\n[3/4] 변환 결과를 검증합니다...")
    print(f"- 원본 컬럼 수: {len(df.columns)}")
    print(f"- 변환 후 컬럼 수: {len(transformed_df.columns)}")
    print(f"- 행 수 변화: {len(df):,} → {len(transformed_df):,}")
    
    # CSV로 저장
    print(f"\n[4/4] 결과를 저장합니다...")
    try:
        transformed_df.to_csv(output_filename, index=False, encoding='utf-8')
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
    print(f"- 변환된 데이터: {len(transformed_df):,}행 x {len(transformed_df.columns)}열")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    
    # 보고서 생성
    report = generate_report(df, transformed_df, output_filename, 
                           input_size, output_size, elapsed_time, settings)
    
    return output_filename, report