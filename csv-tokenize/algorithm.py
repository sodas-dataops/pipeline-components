import pandas as pd
from konlpy.tag import Okt
from multiprocessing import Pool, cpu_count
import os
import time
from datetime import datetime


def load_korean_stopwords(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f)


def tokenize_and_clean(text, stopwords, ignore_words, remove_stopwords):
    okt = Okt()
    tokens = okt.nouns(str(text))

    if remove_stopwords and stopwords:
        tokens = [token for token in tokens if token not in stopwords]

    if ignore_words:
        tokens = [token for token in tokens if token not in ignore_words]

    return " ".join(tokens)


def parallel_tokenize(texts, stopwords, ignore_words, remove_stopwords):
    # 멀티프로세싱용 래퍼 함수
    from functools import partial
    with Pool(processes=cpu_count()) as pool:
        func = partial(tokenize_and_clean, stopwords=stopwords, ignore_words=ignore_words, remove_stopwords=remove_stopwords)
        return pool.map(func, texts)


def generate_report(
    df: pd.DataFrame,
    text_column: str,
    new_column: str,
    ignore_words: list,
    remove_stopwords: bool,
    keep_tokenized_column_only: bool,
    input_filename: str,
    output_filename: str,
    elapsed_time: float,
    total_tokens: int,
    unique_tokens: int
) -> str:
    """
    토큰화 작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - text_column (str): 원본 텍스트 컬럼명
    - new_column (str): 토큰화된 텍스트 컬럼명
    - ignore_words (list): 무시할 단어 목록
    - remove_stopwords (bool): 불용어 제거 여부
    - keep_tokenized_column_only (bool): 토큰화된 컬럼만 유지 여부
    - input_filename (str): 입력 파일 경로
    - output_filename (str): 출력 파일 경로
    - elapsed_time (float): 소요 시간 (초)
    - total_tokens (int): 총 토큰 수
    - unique_tokens (int): 고유 토큰 수
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    report = f"""# CSV 토큰화 작업 보고서

## 1. 작업 개요
- **작업 유형**: CSV 텍스트 토큰화
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **입력 파일**: {input_filename}
- **행 수**: {len(df):,}행
- **컬럼 수**: {len(df.columns)}개
- **컬럼 목록**: {', '.join(df.columns)}

## 3. 토큰화 설정
- **원본 텍스트 컬럼**: {text_column}
- **토큰화된 텍스트 컬럼**: {new_column}
- **불용어 제거**: {'예' if remove_stopwords else '아니오'}
- **무시할 단어 수**: {len(ignore_words) if ignore_words else 0}개
- **토큰화된 컬럼만 유지**: {'예' if keep_tokenized_column_only else '아니오'}
- **사용된 CPU 코어 수**: {cpu_count()}개

## 4. 처리 결과
- **출력 파일**: {output_filename}
- **총 토큰 수**: {total_tokens:,}개
- **고유 토큰 수**: {unique_tokens:,}개
- **평균 토큰 수/행**: {total_tokens/len(df):.1f}개

## 5. 성능 지표
- **처리 속도**: {len(df) / elapsed_time:.2f} 행/초
- **토큰화 속도**: {total_tokens / elapsed_time:.2f} 토큰/초
- **메모리 사용량**: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB

## 6. 작업 상태
- **상태**: 성공
- **처리 결과**: 텍스트가 성공적으로 토큰화됨
"""
    return report


def solution(data: object, text_column: str, output_filename: str, new_column: str = 'tokenized_text', ignore_words: list = None, remove_stopwords: bool = True, keep_tokenized_column_only: bool = False) -> tuple:
    """
    대용량 CSV의 특정 텍스트 컬럼을 한국어 토큰화 + 불용어 제거하여 새 컬럼으로 추가하는 고성능 버전.
    
    Returns:
    - tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    
    # CSV 로드 최적화
    dataFile = pd.read_csv(data, low_memory=False)
    dataFile[text_column] = dataFile[text_column].fillna("")

    stopwords = set()
    if remove_stopwords:
        stopwords = load_korean_stopwords('stopwords-ko.txt')

    if ignore_words:
        ignore_words = set(ignore_words)

    # 병렬 토큰화 처리
    texts = dataFile[text_column].tolist()
    logger = print  # 필요 시 로거로 대체 가능
    logger(f"🔁 Tokenizing {len(texts)} rows using {cpu_count()} cores...")

    tokenized_results = parallel_tokenize(texts, stopwords, ignore_words, remove_stopwords)
    dataFile[new_column] = tokenized_results

    if keep_tokenized_column_only:
        dataFile = dataFile[[new_column]]

    # CSV 저장
    dataFile.to_csv(output_filename, index=False, encoding='utf-8-sig')
    logger(f"✅ Saved tokenized result to {output_filename}")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 토큰 통계 계산
    all_tokens = " ".join(tokenized_results).split()
    total_tokens = len(all_tokens)
    unique_tokens = len(set(all_tokens))
    
    # 보고서 생성
    report = generate_report(
        df=dataFile,
        text_column=text_column,
        new_column=new_column,
        ignore_words=ignore_words,
        remove_stopwords=remove_stopwords,
        keep_tokenized_column_only=keep_tokenized_column_only,
        input_filename=data.name if hasattr(data, 'name') else str(data),
        output_filename=output_filename,
        elapsed_time=elapsed_time,
        total_tokens=total_tokens,
        unique_tokens=unique_tokens
    )
    
    return output_filename, report