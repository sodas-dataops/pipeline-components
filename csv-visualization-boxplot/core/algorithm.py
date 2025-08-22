import pandas as pd
import matplotlib.pyplot as plt
import platform
from matplotlib import rcParams
from matplotlib import font_manager
import time
from datetime import datetime

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

def generate_report(
    df: pd.DataFrame,
    group_by_column: str,
    value_column: str,
    image_file_name: str,
    title: str,
    ylabel: str,
    elapsed_time: float
) -> str:
    """
    박스플롯 생성 작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - group_by_column (str): 그룹화 기준 컬럼명
    - value_column (str): 값 컬럼명
    - image_file_name (str): 저장된 이미지 파일 경로
    - title (str): 차트 제목
    - ylabel (str): y축 레이블
    - elapsed_time (float): 소요 시간 (초)
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    # 그룹별 통계 계산
    stats = {}
    for group in df[group_by_column].unique():
        group_data = df[df[group_by_column] == group][value_column]
        stats[group] = {
            'count': len(group_data),
            'mean': group_data.mean(),
            'median': group_data.median(),
            'std': group_data.std(),
            'min': group_data.min(),
            'max': group_data.max()
        }
    
    report = f"""# 박스플롯 생성 작업 보고서

## 1. 작업 개요
- **작업 유형**: 박스플롯 생성
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **행 수**: {len(df):,}행
- **컬럼 수**: {len(df.columns)}개
- **컬럼 목록**: {', '.join(df.columns)}

## 3. 시각화 설정
- **그룹화 컬럼**: {group_by_column}
- **값 컬럼**: {value_column}
- **차트 제목**: {title if title else 'Box Plot of Selected Features'}
- **Y축 레이블**: {ylabel}

## 4. 처리 결과
- **출력 파일**: {image_file_name}
- **그룹 수**: {len(stats)}개
- **그룹별 통계**:
{chr(10).join([f'  - {group}:' + chr(10) + 
              f'    - 데이터 수: {stats[group]["count"]:,}개' + chr(10) +
              f'    - 평균: {stats[group]["mean"]:.2f}' + chr(10) +
              f'    - 중앙값: {stats[group]["median"]:.2f}' + chr(10) +
              f'    - 표준편차: {stats[group]["std"]:.2f}' + chr(10) +
              f'    - 범위: {stats[group]["min"]:.2f} ~ {stats[group]["max"]:.2f}'
              for group in stats])}

## 5. 성능 지표
- **처리 속도**: {len(df) / elapsed_time:.2f} 행/초
- **메모리 사용량**: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB

## 6. 작업 상태
- **상태**: 성공
- **처리 결과**: 박스플롯이 성공적으로 생성됨
"""
    return report

def solution(data: object, group_by_column: str, value_column: str, image_file_name: str,
             title: str = None, ylabel: str = 'Values') -> tuple:
    """
    CSV 파일에서 그룹화된 데이터의 박스 플롯을 생성하여 이미지 파일로 저장하는 함수.

    Parameters:
    - data: CSV 파일 경로 또는 Pandas DataFrame 객체
    - group_by_column: 그룹화 기준 컬럼명
    - value_column: 박스 플롯에 사용할 값 컬럼명
    - image_file_name: 저장할 이미지 파일 이름
    - title: 그래프 제목 (선택사항)
    - ylabel: y축 레이블 (선택사항, 기본값 'Values')
    
    Returns:
    - tuple: (이미지 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    
    # CSV 데이터 로드
    dataFile = pd.read_csv(data, low_memory=False)

    # 시스템 기본 폰트 설정
    font_path = get_font_path()
    font = font_manager.FontProperties(fname=font_path).get_name()
    rcParams['font.family'] = font

    # Unicode minus 문제 해결
    rcParams['axes.unicode_minus'] = False
    
    # 결측값 제거
    dataFile = dataFile.dropna(subset=[group_by_column, value_column])

    # 그룹화
    grouped_data = [dataFile.loc[dataFile[group_by_column] == group, value_column].values
                    for group in dataFile[group_by_column].unique()]

    # 박스 플롯 생성
    plt.figure(figsize=(10, 8))
    plt.boxplot(grouped_data, labels=dataFile[group_by_column].unique())
    
    # 제목과 축 레이블 설정
    plt.title(title if title else 'Box Plot of Selected Features', fontsize=40)
    plt.ylabel(ylabel, fontsize=24)
    plt.xlabel(group_by_column, fontsize=24)

    plt.tick_params(axis='both', which='major', labelsize=18)

    # 이미지 파일로 저장
    plt.savefig(image_file_name, dpi=300)
    plt.close()

    # 소요 시간 계산
    end_time = time.time()
    elapsed_time = end_time - start_time

    # 보고서 생성
    report = generate_report(
        df=dataFile,
        group_by_column=group_by_column,
        value_column=value_column,
        image_file_name=image_file_name,
        title=title,
        ylabel=ylabel,
        elapsed_time=elapsed_time
    )

    return image_file_name, report