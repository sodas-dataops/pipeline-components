import os
import time
from datetime import datetime
from config.config import args
import pandas as pd

env = 'development' if not 'APP_ENV' in os.environ else os.environ['APP_ENV']
args = args[env]

def generate_report(df: pd.DataFrame, input_cols: list, output_cols: list,
                  input_filename: str, output_filename: str, input_size: int, output_size: int,
                  elapsed_time: float) -> str:
    """
    작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - input_cols (list): 변경 전 컬럼 목록
    - output_cols (list): 변경 후 컬럼 목록
    - input_filename (str): 입력 파일 경로
    - output_filename (str): 출력 파일 경로
    - input_size (int): 입력 파일 크기 (bytes)
    - output_size (int): 출력 파일 크기 (bytes)
    - elapsed_time (float): 소요 시간 (초)
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    report = f"""# CSV 컬럼 이름 변경 작업 보고서

## 1. 작업 개요
- **작업 유형**: CSV 컬럼 이름 변경
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **입력 파일**: {input_filename}
- **파일 크기**: {input_size / 1024:.2f} KB
- **행 수**: {len(df)}
- **기존 컬럼 수**: {len(df.columns)}
- **기존 컬럼**: {', '.join(df.columns)}

## 3. 변경 설정
- **변경된 컬럼 수**: {len(input_cols)}
- **변경 내용**:
{chr(10).join([f"- {input_cols[i]} → {output_cols[i]}" for i in range(len(input_cols))])}

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
- **처리 결과**: 컬럼 이름이 성공적으로 변경됨
"""
    return report

def solution(data, input_cols, output_cols, output_filename):
    """
    Samsung Brightics ML v3.9의 Change Column Name 함수를 파이썬으로 구현한 알고리즘

    Parameters:
        data (str): CSV 파일 경로. 알고리즘 내에서 pandas의 read_csv로 읽어와야 합니다.
        input_cols (list of str): 변경할 기존 컬럼 이름들의 리스트.
        output_cols (list of str): 변경할 새로운 컬럼 이름들의 리스트. 'input_cols' 파라미터와 순서가 일치해야 합니다.
        output_filename (str): 변경된 데이터프레임을 저장할 CSV 파일의 이름.

    Returns:
        tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] CSV 컬럼 이름 변경 작업을 시작합니다.")
    
    # CSV 파일 읽기
    print("\n[1/3] CSV 파일을 로드합니다...")
    df = pd.read_csv(data)
    print(f"- 총 {len(df)}개의 행이 로드되었습니다.")
    print(f"- 기존 컬럼: {', '.join(df.columns)}")
    
    # 입력 파일 크기 확인
    input_size = len(data.getvalue().encode('utf-8'))
    print(f"- 입력 파일 크기: {input_size / 1024:.2f} KB")
    
    # 컬럼 이름 변경
    print("\n[2/3] 컬럼 이름을 변경합니다...")
    for input_col, output_col in zip(input_cols, output_cols):
        df.rename(columns={input_col: output_col}, inplace=True)
        print(f"- {input_col} → {output_col}")
    
    # 변경된 데이터프레임을 CSV 파일로 저장
    print("\n[3/3] 결과를 CSV로 저장합니다...")
    df.to_csv(output_filename, index=False)
    print(f"- CSV 저장 완료: {output_filename}")
    
    # 출력 파일 크기 확인
    output_size = os.path.getsize(output_filename)
    print(f"- 출력 파일 크기: {output_size / 1024:.2f} KB")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\n[요약]")
    print(f"- 처리된 행 수: {len(df)}")
    print(f"- 변경된 컬럼 수: {len(input_cols)}")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    print(f"- 저장 경로: {output_filename}")
    
    # 보고서 생성
    report = generate_report(df, input_cols, output_cols,
                           data.name if hasattr(data, 'name') else data,
                           output_filename, input_size, output_size,
                           elapsed_time)
    
    return output_filename, report
