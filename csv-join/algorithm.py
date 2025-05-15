import os
import time
from config.config import args
from datetime import datetime
'''
import library which you need
'''
import pandas as pd

env = 'development' if not 'APP_ENV' in os.environ else os.environ['APP_ENV']
args = args[env]

def generate_report(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    result_df: pd.DataFrame,
    left_on: str,
    right_on: str,
    how: str,
    lsuffix: str,
    rsuffix: str,
    sort: bool,
    input_left_filename: str,
    input_right_filename: str,
    output_filename: str,
    elapsed_time: float
) -> str:
    """
    CSV 조인 작업 보고서를 생성하는 함수.
    
    Parameters:
    - left_df (pd.DataFrame): 왼쪽 테이블
    - right_df (pd.DataFrame): 오른쪽 테이블
    - result_df (pd.DataFrame): 조인 결과 테이블
    - left_on (str): 왼쪽 테이블 조인 키
    - right_on (str): 오른쪽 테이블 조인 키
    - how (str): 조인 방식
    - lsuffix (str): 왼쪽 테이블 접미사
    - rsuffix (str): 오른쪽 테이블 접미사
    - sort (bool): 정렬 여부
    - input_left_filename (str): 왼쪽 입력 파일 경로
    - input_right_filename (str): 오른쪽 입력 파일 경로
    - output_filename (str): 출력 파일 경로
    - elapsed_time (float): 소요 시간 (초)
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    report = f"""# CSV 조인 작업 보고서

## 1. 작업 개요
- **작업 유형**: CSV 테이블 조인
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
### 왼쪽 테이블
- **입력 파일**: {input_left_filename}
- **행 수**: {len(left_df):,}행
- **컬럼 수**: {len(left_df.columns)}개
- **컬럼 목록**: {', '.join(left_df.columns)}

### 오른쪽 테이블
- **입력 파일**: {input_right_filename}
- **행 수**: {len(right_df):,}행
- **컬럼 수**: {len(right_df.columns)}개
- **컬럼 목록**: {', '.join(right_df.columns)}

## 3. 조인 설정
- **조인 방식**: {how}
- **왼쪽 테이블 조인 키**: {left_on}
- **오른쪽 테이블 조인 키**: {right_on}
- **컬럼 접미사**: 왼쪽='{lsuffix}', 오른쪽='{rsuffix}'
- **정렬 여부**: {'예' if sort else '아니오'}

## 4. 처리 결과
- **출력 파일**: {output_filename}
- **결과 행 수**: {len(result_df):,}행
- **결과 컬럼 수**: {len(result_df.columns)}개
- **조인 효율**: {len(result_df)/max(len(left_df), len(right_df))*100:.1f}%

## 5. 성능 지표
- **처리 속도**: {len(result_df) / elapsed_time:.2f} 행/초
- **메모리 사용량**: {result_df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB

## 6. 작업 상태
- **상태**: 성공
- **처리 결과**: 테이블이 성공적으로 조인됨
"""
    return report

def solution(left_table: object, right_table: object, output_filename: str, left_on, right_on, how='inner', lsuffix='', rsuffix='', sort=False) -> tuple:
    """
    조인 함수를 구현한 알고리즘

    Parameters:
        left_table (str): 왼쪽(첫 번째) 테이블.
        right_table (str): 오른쪽(두 번째) 테이블.
        left_on (str or list of str): 왼쪽 테이블의 조인 키(s).
        right_on (str or list of str): 오른쪽 테이블의 조인 키(s).
        how (str, optional): 조인 방법 ('inner', 'outer', 'left', 'right' 중 하나). 기본값은 'inner'.
        lsuffix (str, optional): 왼쪽 테이블 칼럼 이름과 중복되는 경우에 추가할 접미사. 기본값은 ''.
        rsuffix (str, optional): 오른쪽 테이블 칼럼 이름과 중복되는 경우에 추가할 접미사. 기본값은 ''.
        sort (bool, optional): 조인 결과를 조인 키에 따라 정렬할지 여부. 기본값은 False.
        output_filename (str): 결과를 저장할 CSV 파일의 이름.

    Returns:
        tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] 테이블 조인 작업을 시작합니다.")
    print(f"- 조인 방식: {how}")
    print(f"- 왼쪽 테이블 조인 키: {left_on}")
    print(f"- 오른쪽 테이블 조인 키: {right_on}")
    if lsuffix or rsuffix:
        print(f"- 컬럼 접미사: 왼쪽='{lsuffix}', 오른쪽='{rsuffix}'")
    if sort:
        print("- 조인 결과를 조인 키로 정렬합니다.")
    
    # 테이블 로드
    print("\n[1/4] 테이블을 로드합니다...")
    print("- 왼쪽 테이블을 로드합니다...")
    left_df = pd.read_csv(left_table)
    print(f"  - 행 수: {len(left_df)}")
    print(f"  - 컬럼: {', '.join(left_df.columns)}")
    
    print("- 오른쪽 테이블을 로드합니다...")
    right_df = pd.read_csv(right_table)
    print(f"  - 행 수: {len(right_df)}")
    print(f"  - 컬럼: {', '.join(right_df.columns)}")

    # 조인 키 검증
    print("\n[2/4] 조인 키를 검증합니다...")
    left_missing = [col for col in (left_on if isinstance(left_on, list) else [left_on]) if col not in left_df.columns]
    right_missing = [col for col in (right_on if isinstance(right_on, list) else [right_on]) if col not in right_df.columns]
    
    if left_missing:
        raise ValueError(f"왼쪽 테이블에서 다음 조인 키가 존재하지 않습니다: {left_missing}")
    if right_missing:
        raise ValueError(f"오른쪽 테이블에서 다음 조인 키가 존재하지 않습니다: {right_missing}")
    print("- 모든 조인 키가 존재합니다.")
    
    # 조인 방법 검증
    print("\n[3/4] 조인을 수행합니다...")
    valid_how_values = ['inner', 'outer', 'left', 'right']
    if how not in valid_how_values:
        raise ValueError(f"유효한 'how' 파라미터 값을 입력하세요. 가능한 값: {', '.join(valid_how_values)}")
    
    print(f"- {how} 조인을 수행합니다...")
    result_table = pd.merge(left_df, right_df, left_on=left_on, right_on=right_on, how=how, suffixes=(lsuffix, rsuffix))
    print(f"- 조인 결과: {len(result_table)} 행")
    
    if sort:
        print("- 조인 결과를 정렬합니다...")
        result_table.sort_values(by=left_on, inplace=True)
    
    # 결과 저장
    print(f"\n[4/4] 결과를 저장합니다...")
    result_table.to_csv(output_filename, index=False, mode='w')
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\n[요약]")
    print(f"- 왼쪽 테이블 행 수: {len(left_df)}")
    print(f"- 오른쪽 테이블 행 수: {len(right_df)}")
    print(f"- 조인 결과 행 수: {len(result_table)}")
    print(f"- 조인 효율: {len(result_table)/max(len(left_df), len(right_df))*100:.1f}%")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    print(f"- 저장 경로: {output_filename}")
    
    # 보고서 생성
    report = generate_report(
        left_df=left_df,
        right_df=right_df,
        result_df=result_table,
        left_on=left_on,
        right_on=right_on,
        how=how,
        lsuffix=lsuffix,
        rsuffix=rsuffix,
        sort=sort,
        input_left_filename=left_table.name if hasattr(left_table, 'name') else str(left_table),
        input_right_filename=right_table.name if hasattr(right_table, 'name') else str(right_table),
        output_filename=output_filename,
        elapsed_time=elapsed_time
    )
    
    return output_filename, report