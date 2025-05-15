import pandas as pd
from konlpy.tag import Okt

# korean_stopwords.txt 파일에서 불용어 리스트 로드
def load_korean_stopwords(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f]

def solution(data: object, text_column: str, output_filename: str, new_column: str = 'tokenized_text', ignore_words: list = None, remove_stopwords: bool = True, keep_tokenized_column_only: bool = False):
    """
    CSV 파일에서 특정 텍스트 컬럼의 데이터를 한국어 토큰화하고, 불용어 제거 후 공백으로 구분된 텍스트로 새 컬럼을 생성하는 함수.

    Parameters:
    - data: CSV 파일 경로
    - text_column: 토큰화할 텍스트 컬럼명
    - output_filename: 저장할 CSV 파일 이름
    - new_column: 토큰화된 결과를 저장할 새 컬럼명 (기본값 'tokenized_text')
    - ignore_words: 불용어 리스트 (기본값 None)
    - remove_stopwords: 불용어 제거 여부 (기본값 True)
    - keep_tokenized_column_only: 토큰화된 컬럼만을 남길지 여부 (기본값 False)
    """
    # CSV 데이터 로드
    dataFile = pd.read_csv(data)

    # 한국어 토큰화 객체 생성
    okt = Okt()

    if remove_stopwords:
        # 불용어 리스트 로드
        stopwords = load_korean_stopwords('stopwords-ko.txt')

    # 불용어 제거 및 토큰화 함수 정의
    def tokenize_and_clean(text):
        tokens = okt.nouns(str(text))  # 텍스트를 토큰화
        if remove_stopwords and stopwords:
            tokens = [token for token in tokens if token not in stopwords]  # 불용어 제거
        if ignore_words:
            tokens = [token for token in tokens if token not in ignore_words]  # 불용어 제거
        return " ".join(tokens)  # 공백으로 구분된 문자열로 반환

    # text_column의 텍스트 데이터를 토큰화하고 불용어 제거 후 새 컬럼에 추가
    dataFile[new_column] = dataFile[text_column].dropna().apply(tokenize_and_clean)

    # 토큰화된 컬럼만 남기는 옵션 처리
    if keep_tokenized_column_only:
        dataFile = dataFile[[new_column]]

    # 결과를 CSV 파일로 저장
    dataFile.to_csv(output_filename, index=False)
