import pandas as pd
import time
import numpy as np
from datetime import datetime
from collections import defaultdict
# from scipy.stats import trim_mean  # SciPy 쓰는 버전 원하면 주석 해제

# MultiIndex 컬럼을 평탄화 하는 함수
def flat_cols(df):
    df.columns = ['_'.join(x) for x in df.columns.to_flat_index()]
    return df

def _trimmed_mean_numpy(x, proportion):
    """
    Numpy를 사용한 trimmed mean 계산 함수
    
    Parameters:
    - x: pandas Series
    - proportion: 절사할 비율 (0.0 <= proportion < 0.5)
    
    Returns:
    - float: trimmed mean 값
    """
    # NaN 제거, 정렬 후 양쪽 proportion 비율 절사
    arr = np.sort(np.asarray(x.dropna()))
    if len(arr) == 0:
        return np.nan
    k = int(len(arr) * proportion)
    if k*2 >= len(arr):
        return np.nan
    return arr[k:len(arr)-k].mean()

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
        output_filename (str): 결과를 저장할 CSV 파일의 이름.
        input_cols (list of str): 통계를 계산할 컬럼들의 리스트.
        group_by (list of str): 그룹화할 컬럼들의 리스트.
        statistics (list of str): 계산할 통계량들의 리스트.
        - sum: 합계
        - mean: 평균
        - median: 중앙값
        - min: 최소값
        - max: 최대값
        - std: 표준편차
        - var: 분산
        - count: 개수
        - nunique: 고유값 개수
        - size: 크기
        - first: 첫번째 값
        - last: 마지막 값
        - prod: 곱
        - sem: 표준 오차
        - skew: 왜도
        - kurt: 첨도
        - percentile: 백분위수
        - trimmed-mean: 트리밍된 평균
        percentile_amounts (list of float, optional): 백분위수를 계산할 때 사용할 백분율의 리스트.
        trimmed_mean_amounts (float, optional): 트리밍된 평균을 계산할 때 사용할 값. (0.0 <= trimmed_mean_amounts < 0.5)

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
    
    # 통계량 계산
    print("\n[3/4] 통계량을 계산합니다...")
    print("- 그룹화를 수행합니다...")
    
    # 중복 컬럼 제거 (groupby를 위해)
    unique_input_cols = list(dict.fromkeys(input_cols))  # 순서 유지하면서 중복 제거
    if len(unique_input_cols) != len(input_cols):
        print(f"- 중복 컬럼 제거: {len(input_cols)} -> {len(unique_input_cols)}")
        print(f"- 원본: {input_cols}")
        print(f"- 정리됨: {unique_input_cols}")
    
    grouped = df.groupby(group_by)[unique_input_cols]
    print(f"- 생성된 그룹 수: {len(grouped.groups)}")
    
    # --- (중요) 위치 페어링으로 컬럼별 집계 목록 만들기 ---
    pairs = list(zip(input_cols, statistics))
    basic_agg_map = defaultdict(list)         # pandas 내장/문자열 통계만 넣음
    pct_targets = defaultdict(list)           # percentile을 요청한 (col -> p 리스트)
    tmean_targets = set()                     # trimmed-mean을 요청한 컬럼 집합

    # 숫자/비숫자에 맞지 않는 통계는 걸러주면 안전
    numeric_only = {"mean","sum","median","std","var","sem","skew","kurt","min","max","prod"}
    any_dtype   = {"count","size","nunique","first","last"}

    # dtype 파악(방어적): 숫자 컬럼엔 수치 통계 허용, 비수치엔 안전 통계만
    numeric_cols = df[unique_input_cols].select_dtypes(include="number").columns.tolist()
    non_numeric_cols = [c for c in unique_input_cols if c not in numeric_cols]

    print("- 통계량 페어링을 분석합니다...")
    for col, stat in pairs:
        if stat == "percentile":
            if percentile_amounts is not None:
                # 이 컬럼에 대해서만 해당 p들을 계산
                pct_targets[col].extend(percentile_amounts)
                print(f"  - {col}: percentile {percentile_amounts}")
            continue
        if stat == "trimmed-mean":
            if trimmed_mean_amounts is not None:
                tmean_targets.add(col)
                print(f"  - {col}: trimmed-mean {trimmed_mean_amounts}")
            continue

        # 나머지는 pandas가 아는 키워드/함수여야 함 → 문자열 키워드만 받는다고 가정
        if col in numeric_cols and stat in numeric_only | any_dtype:
            basic_agg_map[col].append(stat)
            print(f"  - {col}: {stat}")
        elif col in non_numeric_cols and stat in any_dtype:
            basic_agg_map[col].append(stat)
            print(f"  - {col}: {stat}")
        else:
            # 부적합 통계는 무시(원하면 경고 로그 출력)
            print(f"  - {col}: {stat} (부적합 통계로 무시됨)")

    # 1) 기본 집계 (내장 키워드들만)
    print("- 기본 통계량을 계산합니다...")
    if basic_agg_map:
        # 중복 통계량 제거 (같은 컬럼에 같은 통계량이 여러 번 요청된 경우)
        for col in basic_agg_map:
            basic_agg_map[col] = list(set(basic_agg_map[col]))  # 중복 제거
        
        summary_df = (
            grouped.agg(dict(basic_agg_map))  # 예: {"_id":["count"], "imdb_rating":["mean"], "imdb_votes":["mean","sum"]}
            .pipe(flat_cols)
        )
        print(f"- 계산된 기본 통계량: {', '.join(summary_df.columns)}")
    else:
        # 기본 통계량이 없으면 빈 DataFrame 생성
        summary_df = pd.DataFrame(index=grouped.groups.keys())

    # 2) percentile: 요청된 컬럼에 대해서만, 요청된 p들만
    if pct_targets:
        print("- 백분위수를 계산합니다...")
        # 각 (col, p)마다 named aggregation 람다로 한 번에 붙이기
        pct_aggs = {}
        for col, ps in pct_targets.items():
            for p in ps:
                name = f"{col}_q{int(p*100)}"
                pct_aggs[name] = (col, lambda s, p=p: s.quantile(p))
        if pct_aggs:
            pct_df = df.groupby(group_by).agg(**pct_aggs)
            summary_df = pd.concat([summary_df, pct_df], axis=1)
            print(f"- 추가된 백분위수: {', '.join(pct_df.columns)}")

    # 3) trimmed-mean: 요청된 컬럼에 대해서만
    if tmean_targets:
        print("- 트리밍된 평균을 계산합니다...")
        tmean_aggs = {}
        for col in tmean_targets:
            name = f"{col}_trimmed_mean_{trimmed_mean_amounts}"
            # SciPy 버전:
            # tmean_aggs[name] = (col, lambda s: trim_mean(s.dropna(), proportiontocut=trimmed_mean_amounts))
            # Numpy만으로 구현한 버전:
            tmean_aggs[name] = (col, lambda s: _trimmed_mean_numpy(s, trimmed_mean_amounts))
        if tmean_aggs:
            tmean_df = df.groupby(group_by).agg(**tmean_aggs)
            summary_df = pd.concat([summary_df, tmean_df], axis=1)
            print(f"- 추가된 트리밍된 평균: {', '.join(tmean_df.columns)}")
    
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