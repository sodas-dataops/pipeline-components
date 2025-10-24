import pandas as pd
import numpy as np
import json
import time
import os
from datetime import datetime
from io import StringIO
import holidays

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
    weekend_column = settings.get('weekend_column', 'is_weekend') if settings else 'is_weekend'
    holiday_column = settings.get('holiday_column', 'is_holiday') if settings else 'is_holiday'
    country = settings.get('country', 'US') if settings else 'US'
    date_format = settings.get('date_format', 'auto') if settings else 'auto'

    # 날짜 컬럼 정보
    date_info = f"- **날짜 컬럼**: {date_column}" if date_column else ""
    weekend_info = f"- **주말 컬럼**: {weekend_column}"
    holiday_info = f"- **공휴일 컬럼**: {holiday_column}"
    country_info = f"- **국가**: {country}"
    format_info = f"- **날짜 형식**: {date_format}"
    
    # 주말/공휴일 통계
    weekend_count = output_data[weekend_column].sum() if weekend_column in output_data.columns else 0
    holiday_count = output_data[holiday_column].sum() if holiday_column in output_data.columns else 0
    total_days = len(output_data)
    weekend_ratio = (weekend_count / total_days * 100) if total_days > 0 else 0
    holiday_ratio = (holiday_count / total_days * 100) if total_days > 0 else 0
    
    report = f"""# 주말/공휴일 탐지 작업 보고서

## 1. 작업 개요
- **작업 유형**: 주말/공휴일 탐지
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초
- **주말 개수**: {weekend_count:,}개
- **주말 비율**: {weekend_ratio:.2f}%
- **공휴일 개수**: {holiday_count:,}개
- **공휴일 비율**: {holiday_ratio:.2f}%
{date_info}
{weekend_info}
{holiday_info}
{country_info}
{format_info}

## 2. 입력 데이터
- **데이터 크기**: {input_size / 1024:.2f} KB
- **행 수**: {len(input_data):,}
- **열 수**: {len(input_data.columns)}
- **열 이름**: {', '.join(input_data.columns)}

## 3. 주말/공휴일 탐지 결과
- **출력 파일**: {output_filename}
- **파일 크기**: {output_size / 1024:.2f} KB
- **행 수**: {len(output_data):,}
- **열 수**: {len(output_data.columns)}
- **주말 개수**: {weekend_count:,}개
- **주말 비율**: {weekend_ratio:.2f}%
- **공휴일 개수**: {holiday_count:,}개
- **공휴일 비율**: {holiday_ratio:.2f}%

## 4. 성능 지표
- **처리 속도**: {len(input_data) / elapsed_time:.2f} 행/초
- **압축률**: {(1 - output_size / input_size) * 100:.2f}%
- **데이터 보존률**: {len(output_data) / len(input_data) * 100:.2f}%

## 5. 작업 상태
- **상태**: 성공
- **주말/공휴일 탐지**: 주말/공휴일 탐지가 성공적으로 완료됨
- **데이터 무결성**: 원본 데이터의 구조 유지
"""
    return report

def solution(input_data: StringIO, output_filename: str, settings: dict = None):
    """
    날짜 데이터에서 주말과 공휴일을 탐지하는 함수.
    
    Parameters:
    - input_data (StringIO): 입력 CSV 데이터
    - output_filename (str): 출력 CSV 파일 경로
    - settings (dict): 주말/공휴일 탐지 설정
        - date_column (str): 날짜 컬럼 이름
        - weekend_column (str): 주말 결과를 저장할 컬럼 이름
        - holiday_column (str): 공휴일 결과를 저장할 컬럼 이름
        - country (str): 공휴일 기준 국가 코드
        - date_format (str): 날짜 형식 ('auto', 'YYYY-MM-DD' 등)
    
    Returns:
    - tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] 주말/공휴일 탐지 작업을 시작합니다.")
    
    # 설정 기본값 설정
    if settings is None:
        settings = {}
    
    date_column = settings.get('date_column', '')
    weekend_column = settings.get('weekend_column', 'is_weekend')
    holiday_column = settings.get('holiday_column', 'is_holiday')
    country = settings.get('country', 'US')
    date_format = settings.get('date_format', 'auto')
    
    print(f"- 날짜 컬럼: {date_column}")
    print(f"- 주말 컬럼: {weekend_column}")
    print(f"- 공휴일 컬럼: {holiday_column}")
    print(f"- 국가: {country}")
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
    
    print(f"\n[2/4] 주말/공휴일 탐지를 수행합니다...")
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
        
        # 주말 탐지 (토요일=5, 일요일=6)
        weekends = date_series.dt.dayofweek.isin([5, 6])
        
        # 공휴일 탐지
        try:
            # 국가별 공휴일 데이터 로드
            country_holidays = holidays.country_holidays(country)
            holidays_list = [date for date in date_series.dropna() if date in country_holidays]
            holiday_dates = set(holidays_list)
            
            # 공휴일 여부 확인
            is_holiday = date_series.isin(holiday_dates)
            
            print(f"- {country} 공휴일 데이터 로드 완료: {len(holiday_dates)}개 공휴일")
            
        except Exception as e:
            print(f"- 경고: {country} 공휴일 데이터를 로드할 수 없습니다: {str(e)}")
            print("- 공휴일 탐지를 건너뜁니다.")
            is_holiday = pd.Series([False] * len(date_series), index=date_series.index)
        
        # 결과 컬럼 추가
        result_df[weekend_column] = weekends
        result_df[holiday_column] = is_holiday
        
        print(f"- 주말 탐지 완료: {weekends.sum():,}개 주말 발견")
        print(f"- 공휴일 탐지 완료: {is_holiday.sum():,}개 공휴일 발견")
        
    except Exception as e:
        raise ValueError(f"주말/공휴일 탐지 실패: {str(e)}")
    
    # 결과 검증
    print(f"\n[3/4] 결과를 검증합니다...")
    print(f"- 원본 컬럼 수: {len(df.columns)}")
    print(f"- 결과 컬럼 수: {len(result_df.columns)}")
    print(f"- 행 수 변화: {len(df):,} → {len(result_df):,}")
    print(f"- 주말 개수: {result_df[weekend_column].sum():,}개")
    print(f"- 주말 비율: {result_df[weekend_column].mean() * 100:.2f}%")
    print(f"- 공휴일 개수: {result_df[holiday_column].sum():,}개")
    print(f"- 공휴일 비율: {result_df[holiday_column].mean() * 100:.2f}%")
    
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
    print(f"- 주말 개수: {result_df[weekend_column].sum():,}개")
    print(f"- 주말 비율: {result_df[weekend_column].mean() * 100:.2f}%")
    print(f"- 공휴일 개수: {result_df[holiday_column].sum():,}개")
    print(f"- 공휴일 비율: {result_df[holiday_column].mean() * 100:.2f}%")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    
    # 보고서 생성
    report = generate_report(df, result_df, output_filename, 
                           input_size, output_size, elapsed_time, settings)
    
    return output_filename, report