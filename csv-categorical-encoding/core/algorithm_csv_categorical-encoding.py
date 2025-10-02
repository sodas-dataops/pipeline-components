import pandas as pd
import numpy as np
import json
import time
import os
from datetime import datetime
from io import StringIO
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, OrdinalEncoder
from sklearn.compose import ColumnTransformer

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
    encoding_method = settings.get('encoding_method', 'label') if settings else 'label'
    target_columns = settings.get('target_columns', []) if settings else []
    handle_unknown = settings.get('handle_unknown', 'error') if settings else 'error'
    drop_first = settings.get('drop_first', False) if settings else False

    # 인코딩 컬럼 정보
    target_info = f"- **대상 컬럼**: {', '.join(target_columns)}" if target_columns else "- **대상 컬럼**: 모든 범주형 컬럼"
    
    report = f"""# 범주형 데이터 인코딩 작업 보고서

## 1. 작업 개요
- **작업 유형**: 범주형 데이터 인코딩
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초
- **인코딩 방법**: {encoding_method}
- **대상 컬럼 수**: {len(target_columns) if target_columns else '모든 범주형'}
- **알 수 없는 값 처리**: {handle_unknown}
- **첫 번째 더미 변수 제거**: {drop_first if encoding_method == 'one_hot' else 'N/A'}
{target_info}

## 2. 입력 데이터
- **데이터 크기**: {input_size / 1024:.2f} KB
- **행 수**: {len(input_data):,}
- **열 수**: {len(input_data.columns)}
- **열 이름**: {', '.join(input_data.columns)}

## 3. 인코딩 결과
- **출력 파일**: {output_filename}
- **파일 크기**: {output_size / 1024:.2f} KB
- **행 수**: {len(output_data):,}
- **열 수**: {len(output_data.columns)}
- **열 증가율**: {((len(output_data.columns) - len(input_data.columns)) / len(input_data.columns) * 100):.2f}%

## 4. 성능 지표
- **처리 속도**: {len(input_data) / elapsed_time:.2f} 행/초
- **압축률**: {(1 - output_size / input_size) * 100:.2f}%
- **데이터 보존률**: {len(output_data) / len(input_data) * 100:.2f}%

## 5. 작업 상태
- **상태**: 성공
- **인코딩**: 범주형 데이터가 성공적으로 인코딩됨
- **데이터 무결성**: 원본 데이터의 구조 유지
"""
    return report

def solution(input_data: StringIO, output_filename: str, settings: dict = None):
    """
    범주형 데이터에 인코딩을 적용하는 함수.
    
    Parameters:
    - input_data (StringIO): 입력 CSV 데이터
    - output_filename (str): 출력 CSV 파일 경로
    - settings (dict): 인코딩 설정
        - encoding_method (str): 인코딩 방법 ('label', 'one_hot', 'ordinal')
        - target_columns (list): 대상 컬럼 목록
        - handle_unknown (str): 알 수 없는 값 처리 방법
        - drop_first (bool): 첫 번째 더미 변수 제거 여부
    
    Returns:
    - tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] 범주형 데이터 인코딩 작업을 시작합니다.")
    
    # 설정 기본값 설정
    if settings is None:
        settings = {}
    
    encoding_method = settings.get('encoding_method', 'label')
    target_columns = settings.get('target_columns', [])
    handle_unknown = settings.get('handle_unknown', 'error')
    drop_first = settings.get('drop_first', False)
    
    print(f"- 인코딩 방법: {encoding_method}")
    print(f"- 대상 컬럼: {target_columns if target_columns else '모든 범주형 컬럼'}")
    print(f"- 알 수 없는 값 처리: {handle_unknown}")
    if encoding_method == 'one_hot':
        print(f"- 첫 번째 더미 변수 제거: {drop_first}")
    
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
        # 모든 범주형 컬럼 선택
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
        target_columns = categorical_columns
        print(f"- 자동 선택된 범주형 컬럼: {target_columns}")
    else:
        # 지정된 컬럼 검증
        missing_columns = [col for col in target_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"지정된 컬럼이 데이터에 존재하지 않습니다: {missing_columns}")
        
        # 범주형이 아닌 컬럼 경고
        non_categorical = [col for col in target_columns if df[col].dtype not in ['object', 'category']]
        if non_categorical:
            print(f"- 경고: 다음 컬럼은 범주형이 아닙니다: {non_categorical}")
    
    if not target_columns:
        print("- 경고: 인코딩할 범주형 컬럼이 없습니다.")
        # 원본 데이터를 그대로 저장
        df.to_csv(output_filename, index=False, encoding='utf-8')
        output_size = os.path.getsize(output_filename)
        elapsed_time = time.time() - start_time
        report = generate_report(df, df, output_filename, input_size, output_size, elapsed_time, settings)
        return output_filename, report
    
    print(f"\n[2/4] 범주형 데이터 인코딩을 수행합니다...")
    print(f"- 대상 컬럼: {target_columns}")
    
    try:
        # 인코딩 방법에 따른 처리
        if encoding_method == 'label':
            # Label Encoding
            encoded_df = df.copy()
            for col in target_columns:
                le = LabelEncoder()
                encoded_df[col] = le.fit_transform(encoded_df[col].astype(str))
                print(f"- {col}: {len(le.classes_)}개 클래스 인코딩 완료")
        
        elif encoding_method == 'one_hot':
            # One-Hot Encoding
            encoded_df = df.copy()
            for col in target_columns:
                # 원본 컬럼 제거
                encoded_df = encoded_df.drop(columns=[col])
                
                # One-Hot 인코딩
                dummies = pd.get_dummies(df[col], prefix=col, drop_first=drop_first)
                encoded_df = pd.concat([encoded_df, dummies], axis=1)
                print(f"- {col}: {dummies.shape[1]}개 더미 변수 생성")
        
        elif encoding_method == 'ordinal':
            # Ordinal Encoding
            encoded_df = df.copy()
            for col in target_columns:
                # 고유값을 정렬하여 순서 결정
                unique_values = sorted(df[col].dropna().unique())
                oe = OrdinalEncoder(categories=[unique_values], handle_unknown=handle_unknown)
                encoded_df[col] = oe.fit_transform(encoded_df[[col]]).flatten()
                print(f"- {col}: {len(unique_values)}개 클래스 순서 인코딩 완료")
        
        else:
            raise ValueError(f"지원하지 않는 인코딩 방법: {encoding_method}")
        
    except Exception as e:
        raise ValueError(f"인코딩 실패: {str(e)}")
    
    # 인코딩 결과 검증
    print(f"\n[3/4] 인코딩 결과를 검증합니다...")
    print(f"- 원본 컬럼 수: {len(df.columns)}")
    print(f"- 인코딩 후 컬럼 수: {len(encoded_df.columns)}")
    print(f"- 행 수 변화: {len(df):,} → {len(encoded_df):,}")
    
    # CSV로 저장
    print(f"\n[4/4] 결과를 저장합니다...")
    try:
        encoded_df.to_csv(output_filename, index=False, encoding='utf-8')
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
    print(f"- 인코딩된 데이터: {len(encoded_df):,}행 x {len(encoded_df.columns)}열")
    print(f"- 컬럼 증가율: {((len(encoded_df.columns) - len(df.columns)) / len(df.columns) * 100):.2f}%")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    
    # 보고서 생성
    report = generate_report(df, encoded_df, output_filename, 
                           input_size, output_size, elapsed_time, settings)
    
    return output_filename, report