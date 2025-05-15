import pandas as pd
import time
import os
from datetime import datetime

def generate_report(df: pd.DataFrame, input_cols: list, display_mode: str, suffix: str,
                  in_format: str, out_format: str, input_filename: str, output_filename: str,
                  input_size: int, output_size: int, elapsed_time: float,
                  success_counts: dict, fail_counts: dict) -> str:
    """
    작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - input_cols (list): 처리된 컬럼 목록
    - display_mode (str): 표시 모드 ('append' 또는 'replace')
    - suffix (str): 새 컬럼 접미사
    - in_format (str): 입력 포맷
    - out_format (str): 출력 포맷
    - input_filename (str): 입력 파일 경로
    - output_filename (str): 출력 파일 경로
    - input_size (int): 입력 파일 크기 (bytes)
    - output_size (int): 출력 파일 크기 (bytes)
    - elapsed_time (float): 소요 시간 (초)
    - success_counts (dict): 각 컬럼별 성공 건수
    - fail_counts (dict): 각 컬럼별 실패 건수
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    report = f"""# CSV 날짜/시간 포맷 변경 작업 보고서

## 1. 작업 개요
- **작업 유형**: CSV 날짜/시간 포맷 변경
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **입력 파일**: {input_filename}
- **파일 크기**: {input_size / 1024:.2f} KB
- **행 수**: {len(df)}
- **기존 컬럼 수**: {len(df.columns)}
- **기존 컬럼**: {', '.join(df.columns)}

## 3. 포맷 변경 설정
- **표시 모드**: {display_mode}
- **입력 포맷**: {in_format}
- **출력 포맷**: {out_format}
- **처리된 컬럼 수**: {len(input_cols)}
- **처리된 컬럼**: {', '.join(input_cols)}
{f"- 새 컬럼 접미사: {suffix}" if display_mode == 'append' else ""}

## 4. 처리 결과
- **출력 파일**: {output_filename}
- **파일 크기**: {output_size / 1024:.2f} KB
- **새 컬럼 수**: {len(df.columns)}
- **새 컬럼**: {', '.join(df.columns)}
- **변환 결과**:
{chr(10).join([f"- {col}: {success_counts[col]}개 성공, {fail_counts[col]}개 실패" for col in input_cols])}

## 5. 성능 지표
- **처리 속도**: {input_size / elapsed_time / 1024:.2f} KB/s
- **압축률**: {(1 - output_size / input_size) * 100:.2f}%
- **처리 효율**: {len(df) / elapsed_time:.2f} 행/초

## 6. 작업 상태
- **상태**: 성공
- **처리 결과**: 날짜/시간 포맷이 성공적으로 변경됨
"""
    return report

def solution(data: object, output_filename: str, input_cols, display_mode='replace', suffix='_new', 
                        in_format='%Y-%m-%d %H:%M:%S', out_format='%Y/%m/%d'):
    """
    주어진 csv 데이터셋에서 DateTime의 포맷을 변경하는 알고리즘

    Parameters:
        data (str): CSV 파일 경로. 알고리즘 내에서 pandas의 read_csv로 읽어와야 합니다.
        input_cols (list of str): 포맷을 변경할 DateTime 컬럼들의 리스트.
        display_mode (str, optional): 결과를 테이블에 어떻게 표시할지 설정합니다. 'append' 또는 'replace' 가능합니다. 기본값은 'replace'입니다.
        suffix (str, optional): display_mode가 'append'일 때 새로운 필드의 접미사입니다. 기본값은 "_new"입니다.
        in_format (str, optional): in-table에서의 DateTime 포맷입니다. 기본값은 '%Y-%m-%d %H:%M:%S'입니다.
        out_format (str, optional): out-table에서의 DateTime 포맷입니다. 기본값은 '%Y/%m/%d'입니다.
        output_filename (str): 결과를 저장할 CSV 파일의 이름.

    Returns:
        tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] 날짜/시간 포맷 변경 작업을 시작합니다.")
    print(f"- 입력 포맷: {in_format}")
    print(f"- 출력 포맷: {out_format}")
    print(f"- 표시 모드: {display_mode}")
    if display_mode == 'append':
        print(f"- 새 컬럼 접미사: {suffix}")
    
    # CSV 파일 읽기
    print("\n[1/4] CSV 파일을 로드합니다...")
    df = pd.read_csv(data)
    print(f"- 총 {len(df)}개의 행이 로드되었습니다.")
    print(f"- 기존 컬럼: {', '.join(df.columns)}")
    
    # 입력 파일 크기 확인
    input_size = os.path.getsize(data.name if hasattr(data, 'name') else data)
    print(f"- 입력 파일 크기: {input_size / 1024:.2f} KB")
    
    # 입력 컬럼 검증
    print("\n[2/4] 입력 컬럼을 검증합니다...")
    missing_cols = [col for col in input_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"다음 컬럼이 존재하지 않습니다: {missing_cols}")
    print(f"- 처리할 컬럼: {', '.join(input_cols)}")
    
    # 날짜/시간 포맷 변경
    print("\n[3/4] 날짜/시간 포맷을 변경합니다...")
    total_cols = len(input_cols)
    success_counts = {}
    fail_counts = {}
    
    if display_mode == 'append':
        for i, col in enumerate(input_cols, 1):
            new_col_name = col + suffix
            print(f"- {i}/{total_cols}번째 컬럼 처리: {col} -> {new_col_name}")
            df[new_col_name] = df[col]
            df[new_col_name] = pd.to_datetime(df[new_col_name], format=in_format, errors='coerce')
            df[new_col_name] = df[new_col_name].dt.strftime(out_format)
            success_count = len(df[new_col_name].dropna())
            fail_count = df[new_col_name].isna().sum()
            success_counts[col] = success_count
            fail_counts[col] = fail_count
            print(f"  - 변환 완료: {success_count}개 행 성공, {fail_count}개 행 실패")
    elif display_mode == 'replace':
        for i, col in enumerate(input_cols, 1):
            print(f"- {i}/{total_cols}번째 컬럼 처리: {col}")
            df[col] = pd.to_datetime(df[col], format=in_format, errors='coerce')
            df[col] = df[col].dt.strftime(out_format)
            success_count = len(df[col].dropna())
            fail_count = df[col].isna().sum()
            success_counts[col] = success_count
            fail_counts[col] = fail_count
            print(f"  - 변환 완료: {success_count}개 행 성공, {fail_count}개 행 실패")
    else:
        raise ValueError("잘못된 display_mode입니다. 'append' 또는 'replace'를 사용하세요.")
    
    # 결과 저장
    print(f"\n[4/4] 결과를 저장합니다...")
    df.to_csv(output_filename, index=False)
    
    # 출력 파일 크기 확인
    output_size = os.path.getsize(output_filename)
    print(f"- 출력 파일 크기: {output_size / 1024:.2f} KB")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\n[요약]")
    print(f"- 처리된 행 수: {len(df)}")
    print(f"- 처리된 컬럼 수: {total_cols}")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    print(f"- 저장 경로: {output_filename}")
    
    # 보고서 생성
    report = generate_report(df, input_cols, display_mode, suffix,
                           in_format, out_format,
                           data.name if hasattr(data, 'name') else data,
                           output_filename, input_size, output_size,
                           elapsed_time, success_counts, fail_counts)
    
    return output_filename, report