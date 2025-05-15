import pandas as pd
import matplotlib.pyplot as plt
import platform
from matplotlib import rcParams
from matplotlib import font_manager

def get_font_path():
    """
    OS에 따라 기본적인 한글 폰트를 반환하는 함수.
    Windows, macOS, Linux 환경을 모두 고려하여 설정.
    """
    if platform.system() == 'Windows':
        return 'C:/Windows/Fonts/malgun.ttf'  # Windows 맑은 고딕 폰트
    elif platform.system() == 'Darwin':  # macOS
        return '/System/Library/Fonts/Supplemental/AppleGothic.ttf'
    elif platform.system() == 'Linux':
        return '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
    else:
        return None

def solution(data: object, feature_names: list, image_file_name: str, title: str = None, ylabel: str = 'Values'):
    """
    CSV 파일에서 여러 feature의 박스 플롯을 생성하여 이미지 파일로 저장하는 함수.

    Parameters:
    - data: CSV 파일 경로
    - feature_names: 박스 플롯을 생성할 feature들의 컬럼명 리스트
    - image_file_name: 저장할 이미지 파일 이름
    - title: 그래프 제목 (선택사항)
    - ylabel: y축 레이블 (선택사항, 기본값 'Values')
    """
    # CSV 데이터 로드
    dataFile = pd.read_csv(data)

    # 시스템 기본 폰트 설정
    font_path = get_font_path()
    font = font_manager.FontProperties(fname=font_path).get_name()
    rcParams['font.family'] = font

    # DejaVu Sans로 백업 폰트 설정 (MINUS SIGN 문제 해결)
    rcParams['axes.unicode_minus'] = False
    
    # feature_names에 해당하는 데이터 선택
    data_to_plot = dataFile[feature_names]
    
    # 박스 플롯 생성
    plt.figure(figsize=(10, 6))
    plt.boxplot(data_to_plot.dropna().values, labels=feature_names)
    
    # 제목과 축 레이블 설정
    plt.title(title if title else 'Box Plot of Selected Features')
    plt.ylabel(ylabel)
    
    # 이미지 파일로 저장
    plt.savefig(image_file_name, dpi=300)
    plt.close()
