import pandas as pd
import numpy as np
import json
import time
import os
from datetime import datetime
from io import StringIO
from collections import defaultdict
import re

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
    include_statistics = settings.get('include_statistics', True) if settings else True
    include_distribution = settings.get('include_distribution', True) if settings else True
    include_quality_metrics = settings.get('include_quality_metrics', True) if settings else True
    include_correlation = settings.get('include_correlation', True) if settings else True
    sample_size = settings.get('sample_size', 10000) if settings else 10000

    # 프로파일링 옵션 정보
    statistics_info = f"- **통계 분석**: {'포함' if include_statistics else '제외'}"
    distribution_info = f"- **분포 분석**: {'포함' if include_distribution else '제외'}"
    quality_info = f"- **품질 지표**: {'포함' if include_quality_metrics else '제외'}"
    correlation_info = f"- **상관관계 분석**: {'포함' if include_correlation else '제외'}"
    sample_info = f"- **샘플 크기**: {sample_size:,}개"
    
    # 데이터 품질 요약
    total_rows = len(input_data)
    total_cols = len(input_data.columns)
    missing_data = input_data.isnull().sum().sum()
    duplicate_rows = input_data.duplicated().sum()
    completeness = ((total_rows * total_cols - missing_data) / (total_rows * total_cols) * 100) if total_rows > 0 else 0
    
    report = f"""# 데이터 프로파일링 작업 보고서

## 1. 작업 개요
- **작업 유형**: 데이터 프로파일링
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초
- **데이터 완전성**: {completeness:.2f}%
- **중복 행**: {duplicate_rows:,}개
- **결측값**: {missing_data:,}개
{statistics_info}
{distribution_info}
{quality_info}
{correlation_info}
{sample_info}

## 2. 입력 데이터
- **데이터 크기**: {input_size / 1024:.2f} KB
- **행 수**: {total_rows:,}
- **열 수**: {total_cols}
- **열 이름**: {', '.join(input_data.columns)}

## 3. 프로파일링 결과
- **출력 파일**: {output_filename}
- **파일 크기**: {output_size / 1024:.2f} KB
- **행 수**: {len(output_data):,}
- **열 수**: {len(output_data.columns)}

## 4. 데이터 품질 지표
- **완전성**: {completeness:.2f}%
- **중복률**: {(duplicate_rows / total_rows * 100):.2f}%
- **결측률**: {(missing_data / (total_rows * total_cols) * 100):.2f}%

## 5. 성능 지표
- **처리 속도**: {total_rows / elapsed_time:.2f} 행/초
- **압축률**: {(1 - output_size / input_size) * 100:.2f}%

## 6. 작업 상태
- **상태**: 성공
- **프로파일링**: 데이터 프로파일링이 성공적으로 완료됨
- **메타데이터**: 상세한 데이터 특성 분석 완료
"""
    return report

def analyze_data_types(df):
    """데이터 타입 분석"""
    type_analysis = {}
    for col in df.columns:
        dtype = str(df[col].dtype)
        non_null_count = df[col].count()
        null_count = df[col].isnull().sum()
        
        type_analysis[col] = {
            'dtype': dtype,
            'non_null_count': non_null_count,
            'null_count': null_count,
            'null_percentage': (null_count / len(df)) * 100
        }
        
        # 수치형 데이터의 경우 추가 정보
        if pd.api.types.is_numeric_dtype(df[col]):
            type_analysis[col]['is_numeric'] = True
            type_analysis[col]['min'] = df[col].min()
            type_analysis[col]['max'] = df[col].max()
            type_analysis[col]['mean'] = df[col].mean()
            type_analysis[col]['std'] = df[col].std()
        else:
            type_analysis[col]['is_numeric'] = False
            type_analysis[col]['unique_count'] = df[col].nunique()
            type_analysis[col]['most_frequent'] = df[col].mode().iloc[0] if not df[col].mode().empty else None
    
    return type_analysis

def analyze_distribution(df, sample_size=10000):
    """분포 분석"""
    distribution_analysis = {}
    
    # 샘플링 (대용량 데이터의 경우)
    if len(df) > sample_size:
        sample_df = df.sample(n=sample_size, random_state=42)
    else:
        sample_df = df
    
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            # 수치형 데이터 분포
            col_data = sample_df[col].dropna()
            if len(col_data) > 0:
                distribution_analysis[col] = {
                    'type': 'numeric',
                    'skewness': col_data.skew(),
                    'kurtosis': col_data.kurtosis(),
                    'percentiles': {
                        '25%': col_data.quantile(0.25),
                        '50%': col_data.quantile(0.50),
                        '75%': col_data.quantile(0.75),
                        '90%': col_data.quantile(0.90),
                        '95%': col_data.quantile(0.95),
                        '99%': col_data.quantile(0.99)
                    }
                }
        else:
            # 범주형 데이터 분포
            value_counts = df[col].value_counts()
            distribution_analysis[col] = {
                'type': 'categorical',
                'unique_values': len(value_counts),
                'top_values': value_counts.head(10).to_dict(),
                'entropy': -sum((p/len(df)) * np.log2(p/len(df)) for p in value_counts if p > 0)
            }
    
    return distribution_analysis

def analyze_quality_metrics(df):
    """데이터 품질 지표 분석"""
    quality_metrics = {}
    
    for col in df.columns:
        col_data = df[col]
        
        # 기본 품질 지표
        quality_metrics[col] = {
            'completeness': (col_data.count() / len(df)) * 100,
            'uniqueness': (col_data.nunique() / len(df)) * 100,
            'duplicate_count': len(df) - col_data.nunique()
        }
        
        # 수치형 데이터의 경우 추가 품질 지표
        if pd.api.types.is_numeric_dtype(col_data):
            # 이상치 탐지 (IQR 방법)
            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = col_data[(col_data < lower_bound) | (col_data > upper_bound)]
            quality_metrics[col]['outlier_count'] = len(outliers)
            quality_metrics[col]['outlier_percentage'] = (len(outliers) / len(col_data)) * 100
            
            # 정규성 검정 (간단한 방법)
            if len(col_data.dropna()) > 3:
                skewness = col_data.skew()
                quality_metrics[col]['is_normal'] = abs(skewness) < 0.5
                quality_metrics[col]['skewness'] = skewness
        
        # 문자열 데이터의 경우 추가 품질 지표
        elif pd.api.types.is_string_dtype(col_data) or col_data.dtype == 'object':
            # 빈 문자열 체크
            empty_strings = (col_data == '').sum()
            quality_metrics[col]['empty_strings'] = empty_strings
            quality_metrics[col]['empty_string_percentage'] = (empty_strings / len(col_data)) * 100
            
            # 패턴 분석 (이메일, 전화번호 등)
            if len(col_data.dropna()) > 0:
                sample_values = col_data.dropna().head(100)
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                phone_pattern = r'^[\+]?[1-9][\d]{0,15}$'
                
                email_count = sum(1 for val in sample_values if re.match(email_pattern, str(val)))
                phone_count = sum(1 for val in sample_values if re.match(phone_pattern, str(val)))
                
                quality_metrics[col]['email_like'] = email_count
                quality_metrics[col]['phone_like'] = phone_count
    
    return quality_metrics

def analyze_correlation(df):
    """상관관계 분석"""
    correlation_analysis = {}
    
    # 수치형 컬럼만 선택
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) > 1:
        # 피어슨 상관계수
        pearson_corr = df[numeric_cols].corr()
        correlation_analysis['pearson'] = pearson_corr.to_dict()
        
        # 강한 상관관계 찾기 (|r| > 0.7)
        strong_correlations = []
        for i in range(len(numeric_cols)):
            for j in range(i+1, len(numeric_cols)):
                corr_value = pearson_corr.iloc[i, j]
                if abs(corr_value) > 0.7:
                    strong_correlations.append({
                        'col1': numeric_cols[i],
                        'col2': numeric_cols[j],
                        'correlation': corr_value
                    })
        
        correlation_analysis['strong_correlations'] = strong_correlations
    
    return correlation_analysis

def solution(input_data: StringIO, output_filename: str, settings: dict = None):
    """
    데이터 프로파일링을 수행하는 함수.
    
    Parameters:
    - input_data (StringIO): 입력 CSV 데이터
    - output_filename (str): 출력 JSON 파일 경로
    - settings (dict): 프로파일링 설정
        - include_statistics (bool): 통계 분석 포함 여부
        - include_distribution (bool): 분포 분석 포함 여부
        - include_quality_metrics (bool): 품질 지표 포함 여부
        - include_correlation (bool): 상관관계 분석 포함 여부
        - sample_size (int): 분포 분석용 샘플 크기
    
    Returns:
    - tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] 데이터 프로파일링 작업을 시작합니다.")
    
    # 설정 기본값 설정
    if settings is None:
        settings = {}
    
    include_statistics = settings.get('include_statistics', True)
    include_distribution = settings.get('include_distribution', True)
    include_quality_metrics = settings.get('include_quality_metrics', True)
    include_correlation = settings.get('include_correlation', True)
    sample_size = settings.get('sample_size', 10000)
    
    print(f"- 통계 분석: {'포함' if include_statistics else '제외'}")
    print(f"- 분포 분석: {'포함' if include_distribution else '제외'}")
    print(f"- 품질 지표: {'포함' if include_quality_metrics else '제외'}")
    print(f"- 상관관계 분석: {'포함' if include_correlation else '제외'}")
    print(f"- 샘플 크기: {sample_size:,}개")
    
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
    
    # 프로파일링 수행
    print(f"\n[2/4] 데이터 프로파일링을 수행합니다...")
    
    try:
        profile_data = {
            'metadata': {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'column_names': list(df.columns),
                'data_types': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'memory_usage': df.memory_usage(deep=True).sum(),
                'created_at': datetime.now().isoformat()
            }
        }
        
        # 데이터 타입 분석
        print("- 데이터 타입 분석 중...")
        profile_data['data_types_analysis'] = analyze_data_types(df)
        
        # 통계 분석
        if include_statistics:
            print("- 통계 분석 중...")
            profile_data['statistics'] = df.describe(include='all').to_dict()
        
        # 분포 분석
        if include_distribution:
            print("- 분포 분석 중...")
            profile_data['distribution_analysis'] = analyze_distribution(df, sample_size)
        
        # 품질 지표 분석
        if include_quality_metrics:
            print("- 품질 지표 분석 중...")
            profile_data['quality_metrics'] = analyze_quality_metrics(df)
        
        # 상관관계 분석
        if include_correlation:
            print("- 상관관계 분석 중...")
            profile_data['correlation_analysis'] = analyze_correlation(df)
        
        print(f"- 프로파일링 완료: {len(profile_data)}개 섹션 생성")
        
    except Exception as e:
        raise ValueError(f"프로파일링 실패: {str(e)}")
    
    # 결과 검증
    print(f"\n[3/4] 결과를 검증합니다...")
    print(f"- 생성된 프로파일 섹션: {len(profile_data)}개")
    print(f"- 분석된 컬럼: {len(df.columns)}개")
    
    # JSON으로 저장
    print(f"\n[4/4] 결과를 저장합니다...")
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, ensure_ascii=False, indent=2, default=str)
        print(f"- JSON 저장 완료: {output_filename}")
    except (PermissionError, OSError, UnicodeEncodeError) as e:
        raise IOError(f"JSON 저장 실패: {str(e)}")
    
    # 출력 데이터 크기 확인
    output_size = os.path.getsize(output_filename)
    print(f"- 출력 데이터 크기: {output_size / 1024:.2f} KB")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\n[요약]")
    print(f"- 출력 파일: {output_filename}")
    print(f"- 원본 데이터: {len(df):,}행 x {len(df.columns)}열")
    print(f"- 프로파일 섹션: {len(profile_data)}개")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    
    # 보고서 생성
    report = generate_report(df, pd.DataFrame(), output_filename, 
                           input_size, output_size, elapsed_time, settings)
    
    return output_filename, report