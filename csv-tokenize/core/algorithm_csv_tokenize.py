import pandas as pd
from konlpy.tag import Okt
from multiprocessing import Pool, cpu_count
import threading
from concurrent.futures import ThreadPoolExecutor
import os
import time
from datetime import datetime

# ===== 1) Okt 전역 1회 생성 =====
_okt = None
_okt_lock = threading.Lock()

def _get_okt():
    global _okt
    if _okt is not None:
        return _okt
    # === 중요: 동시 초기화 방지 ===
    with _okt_lock:
        if _okt is None:          # double-checked locking
            _okt = Okt()
    return _okt

# ===== 불용어 로더 =====
def load_korean_stopwords(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f)

# ===== 2) 토큰화 함수 (전역 OKT 사용) =====
def tokenize_and_clean(text, stopwords, ignore_words, remove_stopwords, min_length: int = 1, max_length: int = None):
    okt = _get_okt()
    s = str(text)
    tokens = okt.nouns(s)

    if min_length:
        tokens = [t for t in tokens if len(t) >= min_length]

    if max_length:
        tokens = [t for t in tokens if len(t) <= max_length]

    if remove_stopwords and stopwords:
        # stopwords / ignore_words는 set 가정
        tokens = [t for t in tokens if t not in stopwords]

    if ignore_words:
        tokens = [t for t in tokens if t not in ignore_words]

    return " ".join(tokens)


# ===== 3) 스레드풀 병렬화 (기본 권장) =====
def parallel_tokenize_thread(texts, stopwords, ignore_words, remove_stopwords, min_length, max_length, workers=None):
    """
    JVM 공유를 위해 스레드풀 권장. workers 기본값은 최소(2, cpu_count()).
    """
    if workers is None:
        # 컨테이너 vCPU 2개라면 2로 충분. 과도한 스레드는 오히려 컨텍스트 스위칭 증가.
        workers = max(2, min(8, os.cpu_count() or 2))

    # 불변 캡처: set으로 확정
    sw = stopwords or set()
    ig = ignore_words or set()

    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(lambda x: tokenize_and_clean(x, sw, ig, remove_stopwords, min_length, max_length), texts))

# ===== 4) (옵션) 멀티프로세싱 병렬화 =====
# 프로세스별로 JVM을 띄워야 하므로 메모리 여유가 있을 때만 사용 권장
# -> 2 vCPU / 2GiB에서는 비추천
_okt_mp = None
def _pool_init():
    global _okt_mp
    _okt_mp = Okt()

def _work_mp(args):
    text, sw, ig, rm = args
    s = str(text)
    tokens = _okt_mp.nouns(s)
    if rm and sw:
        tokens = [t for t in tokens if t not in sw]
    if ig:
        tokens = [t for t in tokens if t not in ig]
    return " ".join(tokens)

def parallel_tokenize_mp(texts, stopwords, ignore_words, remove_stopwords, processes=None):
    if processes is None:
        # 컨테이너 리소스 한도에 맞춰 고정
        processes = max(1, min(2, cpu_count()))
    n = len(texts)
    chunksize = max(1, n // (processes * 8))  # IPC 오버헤드 감소를 위한 적절한 청크

    sw = stopwords or set()
    ig = ignore_words or set()

    with Pool(processes=processes, initializer=_pool_init) as pool:
        return pool.map(_work_mp, [(t, sw, ig, remove_stopwords) for t in texts], chunksize)


def generate_report(
    df: pd.DataFrame,
    text_column: str,
    new_column: str,
    min_length: int,
    max_length: None,
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
- **토큰 최소 길이**: {min_length}
- **토큰 최대 길이**: {max_length}
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


def solution(
    data: object, 
    text_column: str, 
    output_filename: str, 
    new_column: str = 'tokenized_text', 
    min_length: int = 1,
    max_length: int = None,
    ignore_words: list = None, 
    remove_stopwords: bool = True, 
    keep_tokenized_column_only: bool = False,
    backend: str = 'thread',    # "thread" | "process"
    workers: int = None         # thread workers or process count (옵션)
) -> tuple:
    """
    대용량 CSV의 특정 텍스트 컬럼을 한국어 토큰화 + 불용어 제거하여 새 컬럼으로 추가하는 고성능 버전.

    Parameters:
    - data: CSV 파일 경로
    - text_column: 토큰화할 텍스트 컬럼명
    - output_filename: 결과를 저장할 CSV 파일의 이름
    - new_column: 토큰화된 텍스트를 저장할 새 컬럼명
    - min_length: 토큰 최소 길이
    - max_length: 토큰 최대 길이
    - ignore_words: 무시할 단어 목록
    - remove_stopwords: 불용어 제거 여부
    - keep_tokenized_column_only: 토큰화된 컬럼만 유지 여부
    - backend: 병렬 처리 백엔드 ("thread" | "process")
    - workers: 스레드 또는 프로세스 수 (옵션)
    
    Returns:
    - tuple: (저장된 파일 경로, 보고서 내용)
    """
    logger = print  # 필요 시 로거로 대체 가능
    start_time = time.time()
    
    # CSV 로드 최적화
    dataFile = pd.read_csv(data, low_memory=False)
    if text_column not in dataFile.columns:
        raise ValueError(f"Column '{text_column}' not found in CSV.")
    dataFile[text_column] = dataFile[text_column].fillna("")

    stopwords = set()
    if remove_stopwords:
        stopwords = load_korean_stopwords('stopwords-ko.txt')

    ignore_words = set(ignore_words) if ignore_words else set()

    # 병렬 토큰화 처리
    texts = dataFile[text_column].tolist()
    logger(f"🔁 Tokenizing {len(texts)} rows... backend: {backend}, workers: {workers or (os.cpu_count() or 1)}")

    if backend == 'process':
        tokenized_results = parallel_tokenize_mp(
            texts, stopwords, ignore_words, remove_stopwords,
            min_length, max_length,
            processes=workers
        )
    else:
        _get_okt()
        tokenized_results = parallel_tokenize_thread(
            texts, stopwords, ignore_words, remove_stopwords,
            min_length, max_length,
            workers=workers
        )

    dataFile[new_column] = tokenized_results

    if keep_tokenized_column_only:
        dataFile = dataFile[[new_column]]

    # CSV 저장
    dataFile.to_csv(output_filename, index=False, encoding='utf-8-sig')
    logger(f"Saved tokenized result to {output_filename}")
    
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
        min_length=min_length,
        max_length=max_length,
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