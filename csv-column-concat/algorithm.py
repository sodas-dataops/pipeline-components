import pandas as pd
import time
import os
from datetime import datetime

def generate_report(df: pd.DataFrame, target_cols: list, optional_cols: list, delimiter: str, 
                  new_col_name: str, input_filename: str, output_filename: str, 
                  input_size: int, output_size: int, elapsed_time: float) -> str:
    """
    작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - target_cols (list): 연결 대상 컬럼 목록
    - optional_cols (list): 선택적 컬럼 목록
    - delimiter (str): 구분자
    - new_col_name (str): 새 컬럼 이름
    - input_filename (str): 입력 파일 경로
    - output_filename (str): 출력 파일 경로
    - input_size (int): 입력 파일 크기 (bytes)
    - output_size (int): 출력 파일 크기 (bytes)
    - elapsed_time (float): 소요 시간 (초)
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    report = f"""# CSV 컬럼 연결 작업 보고서

## 1. 작업 개요
- **작업 유형**: CSV 컬럼 연결
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **입력 파일**: {input_filename}
- **파일 크기**: {input_size / 1024:.2f} KB
- **행 수**: {len(df)}
- **기존 컬럼 수**: {len(df.columns)}
- **기존 컬럼**: {', '.join(df.columns)}

## 3. 연결 설정
- **대상 컬럼**: {', '.join(target_cols)}
- **선택적 컬럼**: {', '.join(optional_cols)}
- **구분자**: '{delimiter}'
- **새 컬럼 이름**: '{new_col_name}'

## 4. 처리 결과
- **출력 파일**: {output_filename}
- **파일 크기**: {output_size / 1024:.2f} KB
- **새 컬럼 수**: {len(df.columns)}
- **새 컬럼**: {', '.join(df.columns)}

## 5. 성능 지표
- **처리 속도**: {input_size / elapsed_time / 1024:.2f} KB/s
- **압축률**: {(1 - output_size / input_size) * 100:.2f}%
- **처리 효율**: {len(df) / elapsed_time:.2f} 행/초

## 6. 작업 상태
- **상태**: 성공
- **처리 결과**: 컬럼이 성공적으로 연결됨
"""
    return report

def solution(input_filename: str, output_filename: str, target_cols: list, optional_cols: list = None, 
            delimiter: str = ',', new_col_name: str = 'concatenated'):
    """
    CSV 파일의 지정된 컬럼들을 연결하여 새로운 컬럼을 만드는 함수.
    
    Parameters:
    - input_filename (str): 입력 CSV 파일 경로
    - output_filename (str): 출력 CSV 파일 경로
    - target_cols (list): 연결할 필수 컬럼 목록
    - optional_cols (list): 연결할 선택적 컬럼 목록 (기본값: None)
    - delimiter (str): 컬럼 연결 시 사용할 구분자 (기본값: ',')
    - new_col_name (str): 새로 생성할 컬럼의 이름 (기본값: 'concatenated')
    
    Returns:
    - tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] CSV 컬럼 연결 작업을 시작합니다.")
    
    # CSV 파일 로드
    print("\n[1/3] CSV 파일을 로드합니다...")
    try:
        df = pd.read_csv(input_filename)
        print(f"- CSV 데이터 로드 완료: {len(df)}행 x {len(df.columns)}열")
    except Exception as e:
        raise ValueError(f"CSV 파일 로드 실패: {str(e)}")
    
    # 입력 파일 크기 확인
    input_size = os.path.getsize(input_filename)
    print(f"- 입력 파일 크기: {input_size / 1024:.2f} KB")
    
    # 컬럼 검증
    print("\n[2/3] 컬럼을 검증하고 연결합니다...")
    missing_cols = [col for col in target_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"필수 컬럼이 누락되었습니다: {', '.join(missing_cols)}")
    
    # 선택적 컬럼 처리
    if optional_cols:
        available_optional_cols = [col for col in optional_cols if col in df.columns]
        print(f"- 사용 가능한 선택적 컬럼: {', '.join(available_optional_cols)}")
        target_cols.extend(available_optional_cols)
    
    # 컬럼 연결
    print(f"- 연결할 컬럼: {', '.join(target_cols)}")
    df[new_col_name] = df[target_cols].astype(str).agg(delimiter.join, axis=1)
    print(f"- 새 컬럼 '{new_col_name}' 생성 완료")
    
    # CSV로 저장
    print("\n[3/3] 결과를 CSV로 저장합니다...")
    try:
        df.to_csv(output_filename, index=False)
        print(f"- CSV 저장 완료: {output_filename}")
    except Exception as e:
        raise IOError(f"CSV 저장 실패: {str(e)}")
    
    # 출력 파일 크기 확인
    output_size = os.path.getsize(output_filename)
    print(f"- 출력 파일 크기: {output_size / 1024:.2f} KB")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\n[요약]")
    print(f"- 입력 파일: {input_filename}")
    print(f"- 출력 파일: {output_filename}")
    print(f"- 처리된 행 수: {len(df)}")
    print(f"- 연결된 컬럼 수: {len(target_cols)}")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    
    # 보고서 생성
    report = generate_report(df, target_cols, optional_cols or [], delimiter, new_col_name,
                           input_filename, output_filename, input_size, output_size, elapsed_time)
    
    return output_filename, report