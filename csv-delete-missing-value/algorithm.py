import os
import time
from datetime import datetime
'''
import library which you need
'''
import pandas as pd

def generate_report(df: pd.DataFrame, subset: list, input_filename: str, output_filename: str,
                  input_size: int, output_size: int, elapsed_time: float,
                  missing_counts: dict, removed_rows: int) -> str:
    """
    작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - subset (list): 처리된 컬럼 목록
    - input_filename (str): 입력 파일 경로
    - output_filename (str): 출력 파일 경로
    - input_size (int): 입력 파일 크기 (bytes)
    - output_size (int): 출력 파일 크기 (bytes)
    - elapsed_time (float): 소요 시간 (초)
    - missing_counts (dict): 각 컬럼별 결측값 수
    - removed_rows (int): 제거된 행 수
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    report = f"""# CSV 결측값 제거 작업 보고서

## 1. 작업 개요
- **작업 유형**: CSV 결측값 제거
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **입력 파일**: {input_filename}
- **파일 크기**: {input_size / 1024:.2f} KB
- **행 수**: {len(df) + removed_rows:,}행
- **컬럼 수**: {len(df.columns)}개
- **컬럼 목록**: {', '.join(df.columns)}

## 3. 결측값 분석
- **처리 모드**: {'전체 컬럼' if not subset else '선택 컬럼'}
- **처리된 컬럼**: {', '.join(subset) if subset else '모든 컬럼'}
- **결측값 현황**:
{chr(10).join([f"- {col}: {count:,}개 ({count/(len(df) + removed_rows)*100:.1f}%)" for col, count in missing_counts.items() if count > 0])}

## 4. 처리 결과
- **출력 파일**: {output_filename}
- **파일 크기**: {output_size / 1024:.2f} KB
- **제거된 행 수**: {removed_rows:,}행
- **남은 행 수**: {len(df):,}행
- **제거 비율**: {removed_rows/(len(df) + removed_rows)*100:.1f}%

## 5. 성능 지표
- **처리 속도**: {input_size / elapsed_time / 1024:.2f} KB/s
- **압축률**: {(1 - output_size / input_size) * 100:.2f}%
- **처리 효율**: {(len(df) + removed_rows) / elapsed_time:.2f} 행/초

## 6. 작업 상태
- **상태**: 성공
- **처리 결과**: 결측값이 성공적으로 제거됨
"""
    return report

def solution(data: object, output_filename: str, subset):
    """
    CSV 파일에서 결측값을 제거하는 함수

    Args:
        data (object): 처리할 CSV 파일 객체
        output_filename (str): 결과를 저장할 파일 경로
        subset (list of str): 결측값 제거를 적용할 컬럼명 목록
        
    Returns:
        tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] 결측값 제거 작업을 시작합니다.")
    if subset:
        print(f"- 대상 컬럼: {', '.join(subset)}")
    else:
        print("- 모든 컬럼의 결측값을 제거합니다.")
    
    # CSV 파일 로드
    print("\n[1/3] CSV 파일을 로드합니다...")
    df = pd.read_csv(data)
    print(f"- 총 행 수: {len(df):,}행")
    print(f"- 컬럼 수: {len(df.columns)}개")
    print(f"- 컬럼 목록: {', '.join(df.columns)}")
    
    # 입력 파일 크기 확인
    input_size = len(data.getvalue().encode('utf-8'))
    print(f"- 입력 파일 크기: {input_size / 1024:.2f} KB")
    
    # 결측값 분석
    print("\n[2/3] 결측값을 분석합니다...")
    if subset:
        missing_counts = df[subset].isnull().sum()
        print("- 각 컬럼별 결측값 수:")
        for col, count in missing_counts.items():
            print(f"  - {col}: {count:,}개 ({count/len(df)*100:.1f}%)")
    else:
        missing_counts = df.isnull().sum()
        print("- 각 컬럼별 결측값 수:")
        for col, count in missing_counts.items():
            if count > 0:
                print(f"  - {col}: {count:,}개 ({count/len(df)*100:.1f}%)")
    
    # 결측값 제거
    print("\n[3/3] 결측값을 제거합니다...")
    if not subset:
        print("- 모든 컬럼의 결측값을 제거합니다...")
        df = df.dropna()
    else:
        print(f"- 지정된 컬럼({', '.join(subset)})의 결측값을 제거합니다...")
        df = df.dropna(subset=subset)
    
    removed_rows = len(df) - len(df)
    print(f"- 제거된 행 수: {removed_rows:,}행")
    print(f"- 남은 행 수: {len(df):,}행")
    
    # 결과 저장
    print(f"\n[저장] 결과를 저장합니다...")
    df.to_csv(output_filename, index=False, mode='w')
    
    # 출력 파일 크기 확인
    output_size = os.path.getsize(output_filename)
    print(f"- 출력 파일 크기: {output_size / 1024:.2f} KB")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\n[요약]")
    print(f"- 처리 전 행 수: {len(df) + removed_rows:,}행")
    print(f"- 처리 후 행 수: {len(df):,}행")
    print(f"- 제거된 행 비율: {removed_rows/(len(df) + removed_rows)*100:.1f}%")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    print(f"- 저장 경로: {output_filename}")
    
    # 보고서 생성
    report = generate_report(df, subset,
                           data.name if hasattr(data, 'name') else data,
                           output_filename, input_size, output_size,
                           elapsed_time, missing_counts, removed_rows)
    
    return output_filename, report