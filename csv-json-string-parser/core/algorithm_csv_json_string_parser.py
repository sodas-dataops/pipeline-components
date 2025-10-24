import pandas as pd
import numpy as np
import json
import time
import os
from datetime import datetime
from io import StringIO
from typing import Dict, Any, Optional, Tuple

def generate_report(input_data: pd.DataFrame, output_data: pd.DataFrame, 
                   output_filename: str, 
                   input_size: int, output_size: int, elapsed_time: float, 
                   settings: dict = None, conversion_stats: dict = None) -> str:
    """
    JSON 문자열 파싱 작업 보고서를 생성하는 함수.
    
    Parameters:
    - input_data (pd.DataFrame): 입력 데이터
    - output_data (pd.DataFrame): 출력 데이터
    - output_filename (str): 출력 파일 경로
    - input_size (int): 입력 데이터 크기 (bytes)
    - output_size (int): 출력 데이터 크기 (bytes)
    - elapsed_time (float): 소요 시간 (초)
    - settings (dict): 설정
    - conversion_stats (dict): 변환 통계 정보
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    target_column = settings.get('target_column', '') if settings else ''
    column_mapping = settings.get('column_mapping', {}) if settings else {}
    keep_original = settings.get('keep_unknown', False) if settings else False
    error_handling = settings.get('error_handling', 'skip') if settings else 'skip'
    
    # 변환 통계
    stats_info = ""
    if conversion_stats:
        stats_info = f"""
### 변환 통계
- **성공적으로 파싱된 행**: {conversion_stats.get('success_count', 0):,}
- **파싱 실패한 행**: {conversion_stats.get('error_count', 0):,}
- **생성된 새 컬럼**: {len(column_mapping):,}개"""
    
    report = f"""# JSON 문자열 파싱 작업 보고서

## 1. 작업 개요
- **작업 유형**: JSON 문자열 파싱
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초
- **대상 컬럼**: {target_column}
- **컬럼 매핑**: {len(column_mapping):,}개
- **원본 보존**: {'예' if keep_original else '아니오'}
- **오류 처리**: {error_handling}

## 2. 입력 데이터
- **데이터 크기**: {input_size / 1024:.2f} KB
- **행 수**: {len(input_data):,}
- **열 수**: {len(input_data.columns)}
- **열 이름**: {', '.join(input_data.columns)}

## 3. 파싱 결과
- **출력 파일**: {output_filename}
- **파일 크기**: {output_size / 1024:.2f} KB
- **행 수**: {len(output_data):,}
- **열 수**: {len(output_data.columns)}
- **새로 생성된 컬럼**: {', '.join(set(output_data.columns) - set(input_data.columns))}

## 4. 성능 지표
- **처리 속도**: {len(input_data) / elapsed_time:.2f} 행/초
- **오버헤드율**: {((output_size / input_size) - 1) * 100:.2f}%
- **데이터 보존률**: {len(output_data) / len(input_data) * 100:.2f}%{stats_info}

## 5. 작업 상태
- **상태**: 성공
- **결과**: JSON 파싱이 성공적으로 완료됨
- **데이터 무결성**: 원본 데이터의 행 순서 유지
"""
    return report

def solution(input_data: StringIO, output_filename: str, settings: dict = None) -> Tuple[str, str]:
    """
    CSV 데이터에서 JSON 문자열을 파싱하여 개별 컬럼으로 변환하는 함수.
    
    Parameters:
    - input_data (StringIO): 입력 CSV 데이터
    - output_filename (str): 출력 CSV 파일 경로
    - settings (dict): 파싱 설정
        - target_column (str): JSON 문자열이 포함된 컬럼명
        - column_mapping (dict): JSON 키 -> 새 컬럼명 매핑
        - keep_original (bool): 원본 컬럼 보존 여부
        - error_handling (str): 오류 처리 방식 ('skip', 'default', 'fail')
    
    Returns:
    - tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] JSON 문자열 파싱 작업을 시작합니다.")
    
    # 설정 기본값 설정
    if settings is None:
        settings = {}
    
    target_column = settings.get('target_column', '')
    column_mapping = settings.get('column_mapping', {})
    keep_original = settings.get('keep_original', False)
    error_handling = settings.get('error_handling', 'skip')
    
    print(f"- 대상 컬럼: {target_column}")
    print(f"- 컬럼 매핑: {len(column_mapping):,}개")
    print(f"- 원본 보존: {'예' if keep_original else '아니오'}")
    print(f"- 오류 처리: {error_handling}")
    
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
    
    # 대상 컬럼 검증
    if not target_column:
        raise ValueError("target_column이 명시되지 않았습니다.")
    
    if target_column not in df.columns:
        raise ValueError(f"대상 컬럼 '{target_column}'이 데이터에 존재하지 않습니다.")
    
    print(f"\n[2/4] JSON 문자열을 파싱합니다...")
    
    # JSON 파싱 실행
    try:
        parsed_df = df.copy()
        conversion_stats = {'success_count': 0, 'error_count': 0}
        
        # 새 컬럼들 초기화
        for new_col in column_mapping.values():
            parsed_df[new_col] = None
            
        # 각 행 처리
        for idx, row in df.iterrows():
            json_str = row[target_column]
            
            try:
                # JSON 파싱
                parsed_obj = json.loads(json_str) if pd.notna(json_str) else {}
                
                # 매핑된 컬럼들 처리
                for json_key, csv_col_name in column_mapping.items():
                    value = parsed_obj.get(json_key)
                    
                    # 데이터 타입 변환
                    converted_value = _convert_value(json_key, value)
                    parsed_df.loc[idx, csv_col_name] = converted_value
                    
                conversion_stats['success_count'] += 1
                    
            except json.JSONDecodeError as e:
                conversion_stats['error_count'] += 1
                print(f"- 경고: 행 {idx} JSON 파싱 오류 - {str(e)}")
                
                if error_handling == 'fail':
                    raise ValueError(f"행 {idx}에서 JSON 파싱 실패: {str(e)}")
                elif error_handling == 'default':
                    for csv_col_name in column_mapping.values():
                        parsed_df.loc[idx, csv_col_name] = None
        
        # 원본 컬럼 제거 (선택적)
        if not keep_original:
            parsed_df = parsed_df.drop(columns=[target_column])
                    
    except Exception as e:
        raise ValueError(f"JSON 파싱 실패: {str(e)}")
    
    # 파싱 결과 검증
    print(f"\n[3/4] 파싱 결과를 검증합니다...")
    print(f"- 성공적으로 파싱된 행: {conversion_stats['success_count']:,}")
    print(f"- 파싱 실패한 행: {conversion_stats['error_count']:,}")
    print(f"- 새로 생성된 컬럼: {', '.join(set(parsed_df.columns) - set(df.columns))}")
    
    # CSV로 저장
    print(f"\n[4/4] 결과를 저장합니다...")
    try:
        parsed_df.to_csv(output_filename, index=False, encoding='utf-8')
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
    print(f"- 원본 행 수: {len(df):,}")
    print(f"- 파싱된 행 수: {len(parsed_df):,}")
    print(f"- 새 컬럼 수: {len(set(parsed_df.columns) - set(df.columns))}")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    
    # 보고서 생성
    report = generate_report(df, parsed_df, output_filename, 
                           input_size, output_size, elapsed_time, settings, conversion_stats)
    
    return output_filename, report

def _convert_value(key: str, value: Any) -> Any:
    """
    JSON 값을 적절한 타입으로 변환하는 헬퍼 함수
    """
    if value is None:
        return None
        
    # 숫자 필드들 자동 변환
    if key.startswith('field') and len(key) > 5 and key[5:].isdigit():  # field1, field2, etc.
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
            
    # timestamp 필드들
    if key in ['created_at', 'timestamp']:
        try:
            return pd.to_datetime(value)
        except:
            return value
            
    # channel_id는 정수로
    if key == 'channel_id':
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
            
    # entry_id는 정수로
    if key == 'entry_id':
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
            
    # status 필드는 문자열 그대로
    if key == 'status':
        return str(value)
        
    # 위도/경도/고도는 float으로
    if key in ['latitude', 'longitude', 'elevation']:
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
            
    # 기본적으로 원본 유지
    return value
