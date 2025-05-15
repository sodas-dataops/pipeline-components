from io import StringIO
import pandas as pd
import time
from datetime import datetime

def generate_report(
    input_dfs: list,
    result_df: pd.DataFrame,
    input_filenames: list,
    output_filename: str,
    elapsed_time: float
) -> str:
    """
    CSV 병합 작업 보고서를 생성하는 함수.
    
    Parameters:
    - input_dfs (list): 입력 DataFrame 리스트
    - result_df (pd.DataFrame): 병합 결과 DataFrame
    - input_filenames (list): 입력 파일 경로 리스트
    - output_filename (str): 출력 파일 경로
    - elapsed_time (float): 소요 시간 (초)
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    # 입력 데이터 통계 계산
    total_input_rows = sum(len(df) for df in input_dfs)
    total_input_columns = max(len(df.columns) for df in input_dfs)
    common_columns = set.intersection(*[set(df.columns) for df in input_dfs])
    
    report = f"""# CSV 병합 작업 보고서

## 1. 작업 개요
- **작업 유형**: CSV 파일 병합
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **입력 파일 수**: {len(input_dfs)}개
- **총 입력 행 수**: {total_input_rows:,}행
- **최대 컬럼 수**: {total_input_columns}개
- **공통 컬럼 수**: {len(common_columns)}개
- **공통 컬럼 목록**: {', '.join(common_columns)}

### 입력 파일 상세 정보
{chr(10).join([f"#### 파일 {i+1}: {input_filenames[i]}\n- 행 수: {len(df):,}행\n- 컬럼 수: {len(df.columns)}개\n- 컬럼 목록: {', '.join(df.columns)}" for i, df in enumerate(input_dfs)])}

## 3. 처리 결과
- **출력 파일**: {output_filename}
- **결과 행 수**: {len(result_df):,}행
- **결과 컬럼 수**: {len(result_df.columns)}개
- **컬럼 목록**: {', '.join(result_df.columns)}

## 4. 성능 지표
- **처리 속도**: {total_input_rows / elapsed_time:.2f} 행/초
- **메모리 사용량**: {result_df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB

## 5. 작업 상태
- **상태**: 성공
- **처리 결과**: CSV 파일이 성공적으로 병합됨
"""
    return report

def solution(input_data: list, output_csv_path: str) -> tuple:
    """
    여러 개의 DataFrame을 합쳐서 저장
    공통되지 않는 컬럼은 NaN으로 채워집니다.

    Parameters:
    - input_data: 합칠 입력 데이터의 리스트
    - output_csv_path: 결과를 저장할 파일 경로
    
    Returns:
    - tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    
    # CSV 데이터 로드
    data_frames = []
    for data in input_data:
        data_frames.append(pd.read_csv(data))
    if not data_frames:
        raise ValueError("No data frames provided for merging.")

    df = pd.concat(data_frames, ignore_index=True, sort=False)

    # 결과 저장
    df.to_csv(output_csv_path, index=False)
    print(f"Data saved to {output_csv_path}")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 보고서 생성
    report = generate_report(
        input_dfs=data_frames,
        result_df=df,
        input_filenames=[data.name if hasattr(data, 'name') else str(data) for data in input_data],
        output_filename=output_csv_path,
        elapsed_time=elapsed_time
    )
    
    return output_csv_path, report