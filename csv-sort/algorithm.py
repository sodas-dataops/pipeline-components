import pandas as pd
import time
from datetime import datetime

def generate_report(
    df: pd.DataFrame,
    input_cols: list,
    is_asc: bool,
    input_filename: str,
    output_filename: str,
    elapsed_time: float
) -> str:
    """
    CSV 정렬 작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - input_cols (list): 정렬 기준 컬럼 목록
    - is_asc (bool): 오름차순 정렬 여부
    - input_filename (str): 입력 파일 경로
    - output_filename (str): 출력 파일 경로
    - elapsed_time (float): 소요 시간 (초)
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    report = f"""# CSV 정렬 작업 보고서

## 1. 작업 개요
- **작업 유형**: CSV 파일 정렬
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **입력 파일**: {input_filename}
- **행 수**: {len(df):,}행
- **컬럼 수**: {len(df.columns)}개
- **컬럼 목록**: {', '.join(df.columns)}

## 3. 정렬 설정
- **정렬 기준 컬럼**: {', '.join(input_cols)}
- **정렬 방식**: {'오름차순' if is_asc else '내림차순'}

## 4. 처리 결과
- **출력 파일**: {output_filename}
- **정렬된 행 수**: {len(df):,}행
- **정렬된 컬럼 수**: {len(input_cols)}개

## 5. 성능 지표
- **처리 속도**: {len(df) / elapsed_time:.2f} 행/초
- **메모리 사용량**: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB

## 6. 작업 상태
- **상태**: 성공
- **처리 결과**: CSV 파일이 성공적으로 정렬됨
"""
    return report

def solution(data: object, output_filename: str, input_cols: list, is_asc=True) -> tuple:
    """
    CSV 파일을 정렬하는 함수

    Parameters:
        data (str): 정렬할 CSV 파일 경로
        output_filename (str): 정렬된 결과를 저장할 파일 경로
        input_cols (list): 정렬 기준이 되는 컬럼 목록
        is_asc (bool): 오름차순 정렬 여부 (True: 오름차순, False: 내림차순)

    Returns:
        tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] CSV 파일 정렬 작업을 시작합니다.")
    print(f"- 정렬 기준 컬럼: {', '.join(input_cols)}")
    print(f"- 정렬 방식: {'오름차순' if is_asc else '내림차순'}")
    
    # CSV 파일 로드
    print("\n[1/3] CSV 파일을 로드합니다...")
    df = pd.read_csv(data)
    print(f"- 총 행 수: {len(df):,}행")
    print(f"- 컬럼 수: {len(df.columns)}개")
    print(f"- 컬럼 목록: {', '.join(df.columns)}")
    
    # 정렬 컬럼 검증
    print("\n[2/3] 정렬 컬럼을 검증합니다...")
    missing_cols = [col for col in input_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"다음 정렬 컬럼이 존재하지 않습니다: {missing_cols}")
    print("- 모든 정렬 컬럼이 존재합니다.")
    
    # 데이터 정렬
    print("\n[3/3] 데이터를 정렬합니다...")
    print(f"- {', '.join(input_cols)} 기준으로 정렬을 시작합니다...")
    df = df.sort_values(by=input_cols, ascending=is_asc)
    print("- 정렬이 완료되었습니다.")
    
    # 결과 저장
    print(f"\n[저장] 정렬된 결과를 저장합니다...")
    df.to_csv(output_filename, index=False, mode='w')
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\n[요약]")
    print(f"- 처리된 행 수: {len(df):,}행")
    print(f"- 정렬된 컬럼 수: {len(input_cols)}개")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    print(f"- 저장 경로: {output_filename}")
    
    # 보고서 생성
    report = generate_report(
        df=df,
        input_cols=input_cols,
        is_asc=is_asc,
        input_filename=data.name if hasattr(data, 'name') else str(data),
        output_filename=output_filename,
        elapsed_time=elapsed_time
    )
    
    return output_filename, report