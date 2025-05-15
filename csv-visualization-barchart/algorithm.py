import pandas as pd
import matplotlib.pyplot as plt
import time
from datetime import datetime

def generate_report(
    df: pd.DataFrame,
    feature_names: str,
    image_file_name: str,
    bins: int,
    color: str,
    xlabel: str,
    ylabel: str,
    elapsed_time: float
) -> str:
    """
    막대 그래프 생성 작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - feature_names (str): 시각화한 feature의 컬럼명
    - image_file_name (str): 저장된 이미지 파일 경로
    - bins (int): 사용된 빈 개수
    - color (str): 사용된 막대 색상
    - xlabel (str): x축 레이블
    - ylabel (str): y축 레이블
    - elapsed_time (float): 소요 시간 (초)
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    report = f"""# 막대 그래프 생성 작업 보고서

## 1. 작업 개요
- **작업 유형**: 막대 그래프 생성
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **행 수**: {len(df):,}행
- **컬럼 수**: {len(df.columns)}개
- **컬럼 목록**: {', '.join(df.columns)}

## 3. 시각화 설정
- **대상 컬럼**: {feature_names}
- **빈 개수**: {bins}개
- **막대 색상**: {color}
- **X축 레이블**: {xlabel if xlabel else feature_names}
- **Y축 레이블**: {ylabel}

## 4. 처리 결과
- **출력 파일**: {image_file_name}
- **데이터 범위**: {df[feature_names].min():.2f} ~ {df[feature_names].max():.2f}
- **평균값**: {df[feature_names].mean():.2f}
- **중앙값**: {df[feature_names].median():.2f}

## 5. 성능 지표
- **처리 속도**: {len(df) / elapsed_time:.2f} 행/초
- **메모리 사용량**: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB

## 6. 작업 상태
- **상태**: 성공
- **처리 결과**: 막대 그래프가 성공적으로 생성됨
"""
    return report

def solution(data: object, feature_names: str, image_file_name: str, bins: int = 10, color: str = 'blue', xlabel: str = None, ylabel: str = 'Frequency') -> tuple:
    """
    CSV 파일에서 특정 feature의 막대 그래프를 생성하여 이미지 파일로 저장하는 함수.

    Parameters:
    - data: CSV 파일 경로
    - feature_names: 막대 그래프를 생성할 feature의 컬럼명
    - image_file_name: 저장할 이미지 파일 이름
    - bins: 막대 그래프의 빈 개수 (선택사항, 기본값 10)
    - color: 막대 그래프 막대 색상 (선택사항, 기본값 'blue')
    - xlabel: x축 레이블 (선택사항)
    - ylabel: y축 레이블 (선택사항, 기본값 'Frequency')
    
    Returns:
    - tuple: (이미지 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    
    # CSV 데이터 로드
    dataFile = pd.read_csv(data)
    
    # 막대 그래프 생성
    plt.figure(figsize=(10, 6))
    plt.hist(dataFile[feature_names], bins=bins, color=color, edgecolor='black')
    
    # 축 레이블 설정
    plt.xlabel(xlabel if xlabel else feature_names)
    plt.ylabel(ylabel)
    
    # 이미지 파일로 저장
    plt.savefig(image_file_name, dpi=300)
    plt.close()

    # 소요 시간 계산
    end_time = time.time()
    elapsed_time = end_time - start_time

    # 보고서 생성
    report = generate_report(
        df=dataFile,
        feature_names=feature_names,
        image_file_name=image_file_name,
        bins=bins,
        color=color,
        xlabel=xlabel,
        ylabel=ylabel,
        elapsed_time=elapsed_time
    )

    return image_file_name, report
