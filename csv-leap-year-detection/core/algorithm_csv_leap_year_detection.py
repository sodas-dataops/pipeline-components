import pandas as pd
import numpy as np
import json
import time
import os
from datetime import datetime
from io import StringIO
import calendar

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
    date_column = settings.get('date_column', '') if settings else ''
    output_column = settings.get('output_column', 'is_leap_year') if settings else 'is_leap_year'
    date_format = settings.get('date_format', 'auto') if settings else 'auto'

    # 날짜 컬럼 정보
    date_info = f"- **날짜 컬럼**: {date_column}" if date_column else ""
    output_info = f"- **출력 컬럼**: {output_column}"
    format_info = f"- **날짜 형식**: {date_format}"
    
    # 윤년 통계
    leap_year_count = output_data[output_column].sum() if output_column in output_data.columns else 0
    total_years = len(output_data)
    leap_year_ratio = (leap_year_count / total_years * 100) if total_years > 0 else 0
    
    report = f"""# 윤년 탐지 작업 보고서

## 1. 작업 개요
- **작업 유형**: 윤년 탐지
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초
- **윤년 개수**: {leap_year_count:,}개
- **윤년 비율**: {leap_year_ratio:.2f}%
{date_info}
{output_info}
{format_info}

## 2. 입력 데이터
- **데이터 크기**: {input_size / 1024:.2f} KB
- **행 수**: {len(input_data):,}
- **열 수**: {len(input_data.columns)}
- **열 이름**: {', '.join(input_data.columns)}

## 3. 윤년 탐지 결과
- **출력 파일**: {output_filename}
- **파일 크기**: {output_size / 1024:.2f} KB
- **행 수**: {len(output_data):,}
- **열 수**: {len(output_data.columns)}
- **윤년 개수**: {leap_year_count:,}개
- **윤년 비율**: {leap_year_ratio:.2f}%

## 4. 성능 지표
- **처리 속도**: {len(input_data) / elapsed_time:.2f} 행/초
- **압축률**: {(1 - output_size / input_size) * 100:.2f}%
- **데이터 보존률**: {len(output_data) / len(input_data) * 100:.2f}%

## 5. 작업 상태
- **상태**: 성공
- **윤년 탐지**: 윤년 탐지가 성공적으로 완료됨
- **데이터 무결성**: 원본 데이터의 구조 유지
"""
    return report

def is_leap_year(year):
    """
    윤년인지 확인하는 함수.
    
    Parameters:
    - year (int): 연도
    
    Returns:
    - bool: 윤년이면 True, 아니면 False
    """
    return calendar.isleap(year)

def solution(input_data: StringIO, output_filename: str, settings: dict = None):
    """
    날짜 데이터에서 윤년을 탐지하는 함수.
    
    Parameters:
    - input_data (StringIO): 입력 CSV 데이터
    - output_filename (str): 출력 CSV 파일 경로
    - settings (dict): 윤년 탐지 설정
        - date_column (str): 날짜 컬럼 이름
        - output_column (str): 윤년 결과를 저장할 컬럼 이름
        - date_format (str): 날짜 형식 ('auto', 'YYYY', 'YYYY-MM-DD' 등)
    
    Returns:
    - tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] 윤년 탐지 작업을 시작합니다.")
    
    # 설정 기본값 설정
    if settings is None:
        settings = {}
    
    date_column = settings.get('date_column', '')
    output_column = settings.get('output_column', 'is_leap_year')
    date_format = settings.get('date_format', 'auto')
    
    print(f"- 날짜 컬럼: {date_column}")
    print(f"- 출력 컬럼: {output_column}")
    print(f"- 날짜 형식: {date_format}")
    
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
    
    # 날짜 컬럼 검증
    if not date_column:
        # 자동으로 날짜 컬럼 찾기
        date_columns = []
        for col in df.columns:
            if df[col].dtype == 'object':
                # 문자열 컬럼에서 날짜 패턴 확인
                sample_values = df[col].dropna().head(10)
                if len(sample_values) > 0:
                    # 간단한 날짜 패턴 확인
                    if any(str(val).count('-') >= 2 or str(val).count('/') >= 2 for val in sample_values):
                        date_columns.append(col)
        
        if date_columns:
            date_column = date_columns[0]
            print(f"- 자동 선택된 날짜 컬럼: {date_column}")
        else:
            raise ValueError("날짜 컬럼을 찾을 수 없습니다. date_column을 명시적으로 지정해주세요.")
    
    if date_column not in df.columns:
        raise ValueError(f"지정된 날짜 컬럼 '{date_column}'이 데이터에 존재하지 않습니다.")
    
    print(f"\n[2/4] 윤년 탐지를 수행합니다...")
    print(f"- 대상 컬럼: {date_column}")
    
    try:
        # 결과 데이터프레임 생성
        result_df = df.copy()
        
        # 날짜 컬럼을 datetime으로 변환
        if date_format == 'auto':
            # 자동 형식 감지
            date_series = pd.to_datetime(df[date_column], errors='coerce', infer_datetime_format=True)
        else:
            # 지정된 형식 사용
            date_series = pd.to_datetime(df[date_column], format=date_format, errors='coerce')
        
        # 변환 실패한 값 확인
        failed_count = date_series.isna().sum()
        if failed_count > 0:
            print(f"- 경고: {failed_count:,}개의 날짜 값이 변환에 실패했습니다.")
        
        # 연도 추출
        years = date_series.dt.year
        
        # 윤년 탐지
        leap_years = years.apply(is_leap_year)
        
        # 결과 컬럼 추가
        result_df[output_column] = leap_years
        
        print(f"- 윤년 탐지 완료: {leap_years.sum():,}개 윤년 발견")
        
    except Exception as e:
        raise ValueError(f"윤년 탐지 실패: {str(e)}")
    
    # 결과 검증
    print(f"\n[3/4] 결과를 검증합니다...")
    print(f"- 원본 컬럼 수: {len(df.columns)}")
    print(f"- 결과 컬럼 수: {len(result_df.columns)}")
    print(f"- 행 수 변화: {len(df):,} → {len(result_df):,}")
    print(f"- 윤년 개수: {result_df[output_column].sum():,}개")
    print(f"- 윤년 비율: {result_df[output_column].mean() * 100:.2f}%")
    
    # CSV로 저장
    print(f"\n[4/4] 결과를 저장합니다...")
    try:
        result_df.to_csv(output_filename, index=False, encoding='utf-8')
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
    print(f"- 결과 데이터: {len(result_df):,}행 x {len(result_df.columns)}열")
    print(f"- 윤년 개수: {result_df[output_column].sum():,}개")
    print(f"- 윤년 비율: {result_df[output_column].mean() * 100:.2f}%")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    
    # 보고서 생성
    report = generate_report(df, result_df, output_filename, 
                           input_size, output_size, elapsed_time, settings)
    
    return output_filename, report