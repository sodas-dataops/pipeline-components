import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import platform

def get_font_path():
    """
    OS에 따라 기본적인 한글 폰트를 반환하는 함수.
    Windows, macOS, Linux 환경을 모두 고려하여 설정.
    """
    if platform.system() == 'Windows':
        return 'C:/Windows/Fonts/malgun.ttf'  # Windows 맑은 고딕 폰트
    elif platform.system() == 'Darwin':  # macOS
        return '/System/Library/Fonts/AppleGothic.ttf'
    elif platform.system() == 'Linux':
        return '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
    else:
        return None

def solution(data: object, word_column: str, count_column: str, image_file_name: str, max_words: int = 200, background_color: str = 'white', colormap: str = 'tab10'):
    """
    CSV 파일에서 워드와 해당 단어의 빈도수를 기반으로 워드클라우드를 생성하여 이미지 파일로 저장하는 함수.
    OS에 따른 기본 한글 폰트를 자동으로 설정.

    Parameters:
    - data: CSV 파일 경로
    - word_column: 단어가 저장된 컬럼명
    - count_column: 단어의 빈도수가 저장된 컬럼명
    - image_file_name: 저장할 이미지 파일 이름
    - max_words: 워드클라우드에 표시할 최대 단어 수 (선택사항, 기본값 200)
    - background_color: 배경색 (선택사항, 기본값 'white')
    - colormap: 워드클라우드의 색상맵 (선택사항, 기본값 'tab10')
    """
    # CSV 데이터 로드
    dataFile = pd.read_csv(data)
    
    # 단어와 빈도수 딕셔너리 생성
    word_freq = dict(zip(dataFile[word_column], dataFile[count_column]))
    
    # 시스템 기본 폰트 설정
    font_path = get_font_path()
    
    # 워드클라우드 생성
    wordcloud = WordCloud(
        font_path=font_path,
        max_words=max_words,
        background_color=background_color,
        colormap=colormap,
        width=1080,
        height=720
    ).generate_from_frequencies(word_freq)
    
    # 워드클라우드 시각화
    plt.figure(figsize=(10, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    
    # 이미지 파일로 저장
    plt.savefig(image_file_name, dpi=600, format='png')
    plt.close()
