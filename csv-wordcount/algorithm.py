import pandas as pd
from collections import Counter
import time
from datetime import datetime

def generate_report(
    df: pd.DataFrame,
    columns: list,
    separator: str,
    input_filename: str,
    output_filename: str,
    elapsed_time: float,
    total_words: int,
    unique_words: int
) -> str:
    """
    단어 카운트 작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - columns (list): 처리된 컬럼 목록
    - separator (str): 사용된 구분자
    - input_filename (str): 입력 파일 경로
    - output_filename (str): 출력 파일 경로
    - elapsed_time (float): 소요 시간 (초)
    - total_words (int): 총 단어 수
    - unique_words (int): 고유 단어 수
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    report = f"""# 단어 카운트 작업 보고서

## 1. 작업 개요
- **작업 유형**: 단어 카운트
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **입력 파일**: {input_filename}
- **행 수**: {len(df):,}행
- **컬럼 수**: {len(df.columns)}개
- **컬럼 목록**: {', '.join(df.columns)}

## 3. 처리 설정
- **처리 컬럼**: {', '.join(columns)}
- **구분자**: '{separator}'

## 4. 처리 결과
- **출력 파일**: {output_filename}
- **총 단어 수**: {total_words:,}개
- **고유 단어 수**: {unique_words:,}개
- **평균 단어 수**: {total_words/len(df):.1f}개/행

## 5. 성능 지표
- **처리 속도**: {total_words / elapsed_time:.2f} 단어/초
- **메모리 사용량**: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB

## 6. 작업 상태
- **상태**: 성공
- **처리 결과**: 단어 카운트가 성공적으로 완료됨
"""
    return report

def solution(input_data: object, columns: list, separator: str, output_file: str) -> tuple:
    """
    단어 카운트를 수행하고 결과를 저장하는 함수.

    Parameters:
    - input_data: CSV 데이터 (파일 경로 또는 Pandas DataFrame)
    - columns: 단어 카운트를 수행할 컬럼 목록
    - separator: 단어를 분리할 구분자
    - output_file: 결과를 저장할 CSV 파일 경로
    
    Returns:
    - tuple: (출력 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    
    # CSV 데이터 로드
    data = pd.read_csv(input_data)

    # 단어 카운트를 위한 Counter 객체 초기화
    word_counter = Counter()

    # 지정된 컬럼에서 단어 추출 및 카운트
    for column in columns:
        if column in data.columns:
            for entry in data[column].dropna():
                words = str(entry).split(separator)
                word_counter.update(words)

    # 결과를 데이터프레임으로 변환
    result_df = pd.DataFrame(word_counter.items(), columns=['word', 'count'])

    # 결과 저장
    result_df.to_csv(output_file, index=False)
    print(f'Word count result saved to {output_file}')

    # 소요 시간 계산
    end_time = time.time()
    elapsed_time = end_time - start_time

    # 보고서 생성
    report = generate_report(
        df=data,
        columns=columns,
        separator=separator,
        input_filename=input_data.name if hasattr(input_data, 'name') else 'input_data',
        output_filename=output_file,
        elapsed_time=elapsed_time,
        total_words=sum(word_counter.values()),
        unique_words=len(word_counter)
    )

    return output_file, report
