import pandas as pd
import time
from datetime import datetime

# MultiIndex 컬럼을 평탄화 하는 함수
def flat_cols(df):
    df.columns = ['_'.join(x) for x in df.columns.to_flat_index()]
    return df

def generate_report(
    df: pd.DataFrame,
    summary_df: pd.DataFrame,
    input_cols: list,
    group_by: list,
    statistics: list,
    percentile_amounts: list,
    trimmed_mean_amounts: float,
    input_filename: str,
    output_filename: str,
    elapsed_time: float
) -> str:
    """
    통계 요약 작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 입력 DataFrame
    - summary_df (pd.DataFrame): 통계 요약 결과 DataFrame
    - input_cols (list): 통계 대상 컬럼 목록
    - group_by (list): 그룹화 컬럼 목록
    - statistics (list): 계산된 통계량 목록
    - percentile_amounts (list): 백분위수 계산 값 목록
    - trimmed_mean_amounts (float): 트리밍된 평균 계산 값
    - input_filename (str): 입력 파일 경로
    - output_filename (str): 출력 파일 경로
    - elapsed_time (float): 소요 시간 (초)
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    report = f"""# CSV 통계 요약 작업 보고서

## 1. 작업 개요
- **작업 유형**: CSV 통계 요약
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **입력 파일**: {input_filename}
- **행 수**: {len(df):,}행
- **컬럼 수**: {len(df.columns)}개
- **컬럼 목록**: {', '.join(df.columns)}

## 3. 통계 설정
- **통계 대상 컬럼**: {', '.join(input_cols)}
- **그룹화 컬럼**: {', '.join(group_by)}
- **계산된 통계량**: {', '.join(statistics)}
- **백분위수 계산**: {', '.join(map(str, percentile_amounts)) if percentile_amounts else '없음'}
- **트리밍된 평균 계산**: {trimmed_mean_amounts if trimmed_mean_amounts else '없음'}

## 4. 처리 결과
- **출력 파일**: {output_filename}
- **그룹 수**: {len(summary_df):,}개
- **계산된 통계량 수**: {len(summary_df.columns)}개
- **통계량 목록**: {', '.join(summary_df.columns)}

## 5. 성능 지표
- **처리 속도**: {len(df) / elapsed_time:.2f} 행/초
- **메모리 사용량**: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB

## 6. 작업 상태
- **상태**: 성공
- **처리 결과**: 통계 요약이 성공적으로 생성됨
"""
    return report

def solution(data: object, output_filename: str, input_cols, group_by, statistics, 
                    percentile_amounts=None, trimmed_mean_amounts=None) -> tuple:
    """
    Samsung Brightics ML v3.9의 Statistic Summary 함수를 파이썬으로 구현한 알고리즘

    Parameters:
        data (str): CSV 파일 경로. 알고리즘 내에서 pandas의 read_csv로 읽어와야 합니다.
        input_cols (list of str): 통계를 계산할 컬럼들의 리스트.
        group_by (list of str): 그룹화할 컬럼들의 리스트.
        statistics (list of str): 계산할 통계량들의 리스트.
        percentile_amounts (list of float, optional): 백분위수를 계산할 때 사용할 백분율의 리스트.
        trimmed_mean_amounts (float, optional): 트리밍된 평균을 계산할 때 사용할 값. (0.0 <= trimmed_mean_amounts < 0.5)
        output_filename (str): 결과를 저장할 CSV 파일의 이름.

    Returns:
        tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] 통계 요약 작업을 시작합니다.")
    print(f"- 통계 대상 컬럼: {', '.join(input_cols)}")
    print(f"- 그룹화 컬럼: {', '.join(group_by)}")
    print(f"- 계산할 통계량: {', '.join(statistics)}")
    if percentile_amounts:
        print(f"- 백분위수 계산: {', '.join(map(str, percentile_amounts))}")
    if trimmed_mean_amounts:
        print(f"- 트리밍된 평균 계산: {trimmed_mean_amounts}")
    
    # CSV 파일 읽기
    print("\n[1/4] CSV 파일을 로드합니다...")
    df = pd.read_csv(data)
    print(f"- 총 {len(df)}개의 행이 로드되었습니다.")
    print(f"- 기존 컬럼: {', '.join(df.columns)}")
    
    # 입력 컬럼 검증
    print("\n[2/4] 입력 컬럼을 검증합니다...")
    missing_cols = [col for col in input_cols + group_by if col not in df.columns]
    if missing_cols:
        raise ValueError(f"다음 컬럼이 존재하지 않습니다: {missing_cols}")
    print("- 모든 컬럼이 존재합니다.")
    
    # 기본 통계량 계산
    print("\n[3/4] 통계량을 계산합니다...")
    print("- 그룹화를 수행합니다...")
    grouped = df.groupby(group_by)[input_cols]
    print(f"- 생성된 그룹 수: {len(grouped.groups)}")
    
    print("- 기본 통계량을 계산합니다...")
    cols = {col: statistics for col in input_cols}
    summary_df = grouped.agg(cols).pipe(flat_cols)
    print(f"- 계산된 통계량: {', '.join(summary_df.columns)}")
    
    # 백분위수 계산
    if 'percentile' in statistics and percentile_amounts is not None:
        print("- 백분위수를 계산합니다...")
        percentiles = grouped.quantile(percentile_amounts)
        summary_df = pd.concat([summary_df, percentiles], axis=1)
        print(f"- 추가된 백분위수: {', '.join(percentiles.columns)}")
    
    # 트리밍된 평균 계산
    if 'trimmed-mean' in statistics and trimmed_mean_amounts is not None:
        print("- 트리밍된 평균을 계산합니다...")
        trimmed_means = grouped.apply(lambda group: group.iloc[int(trimmed_mean_amounts * len(group)):int((1 - trimmed_mean_amounts) * len(group))].mean())
        summary_df = pd.concat([summary_df, trimmed_means.rename('trimmed-mean')], axis=1)
        print("- 트리밍된 평균이 추가되었습니다.")
    
    # 결과 저장
    print(f"\n[4/4] 결과를 저장합니다...")
    summary_df.reset_index().to_csv(output_filename, index=False)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\n[요약]")
    print(f"- 처리된 행 수: {len(df)}")
    print(f"- 그룹 수: {len(grouped.groups)}")
    print(f"- 계산된 통계량 수: {len(summary_df.columns)}")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    print(f"- 저장 경로: {output_filename}")
    
    # 보고서 생성
    report = generate_report(
        df=df,
        summary_df=summary_df,
        input_cols=input_cols,
        group_by=group_by,
        statistics=statistics,
        percentile_amounts=percentile_amounts,
        trimmed_mean_amounts=trimmed_mean_amounts,
        input_filename=data.name if hasattr(data, 'name') else str(data),
        output_filename=output_filename,
        elapsed_time=elapsed_time
    )
    
    return output_filename, report