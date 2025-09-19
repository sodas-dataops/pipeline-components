import pandas as pd
import matplotlib.pyplot as plt
import time
from datetime import datetime

def generate_report(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    image_file_name: str,
    color: str,
    xlabel: str,
    ylabel: str,
    elapsed_time: float
) -> str:
    """
    막대 그래프 생성 작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - x_column (str): x축에 사용된 컬럼명
    - y_column (str): y축에 사용된 컬럼명
    - image_file_name (str): 저장된 이미지 파일 경로
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
- **X축 컬럼**: {x_column}
- **Y축 컬럼**: {y_column}
- **막대 색상**: {color}
- **X축 레이블**: {xlabel}
- **Y축 레이블**: {ylabel}

## 4. 처리 결과
- **출력 파일**: {image_file_name}
- **X축 고유값 개수**: {df[x_column].nunique()}개
- **Y축 데이터 범위**: {df[y_column].min():.2f} ~ {df[y_column].max():.2f}
- **Y축 평균값**: {df[y_column].mean():.2f}
- **Y축 중앙값**: {df[y_column].median():.2f}

## 5. 성능 지표
- **처리 속도**: {len(df) / elapsed_time:.2f} 행/초
- **메모리 사용량**: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB

## 6. 작업 상태
- **상태**: 성공
- **처리 결과**: 막대 그래프가 성공적으로 생성됨
"""
    return report

def solution(data: object, x_column: str, y_column: str, image_file_name: str, color: str = 'blue', xlabel: str = None, ylabel: str = None) -> tuple:
    """
    CSV 파일에서 두 컬럼을 사용하여 막대 그래프를 생성하여 이미지 파일로 저장하는 함수.

    Parameters:
    - data: CSV 파일 경로 또는 StringIO 객체
    - x_column: x축에 사용할 컬럼명 (카테고리)
    - y_column: y축에 사용할 컬럼명 (수치값)
    - image_file_name: 저장할 이미지 파일 이름
    - color: 막대 그래프 막대 색상 (선택사항, 기본값 'blue')
    - xlabel: x축 레이블 (선택사항, 기본값은 x_column)
    - ylabel: y축 레이블 (선택사항, 기본값은 y_column)
    
    Returns:
    - tuple: (이미지 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    
    # CSV 데이터 로드
    dataFile = pd.read_csv(data)
    
    # 막대 그래프 생성
    plt.figure(figsize=(10, 6))
    
    # x축과 y축 데이터 추출
    x_data = dataFile[x_column]
    y_data = dataFile[y_column]
    
    # 막대 그래프 생성
    plt.bar(x_data, y_data, color=color, edgecolor='black')
    
    # 축 레이블 설정
    plt.xlabel(xlabel if xlabel else x_column)
    plt.ylabel(ylabel if ylabel else y_column)
    
    # x축 레이블 회전 (긴 레이블의 경우)
    plt.xticks(rotation=45, ha='right')
    
    # 레이아웃 조정
    plt.tight_layout()
    
    # 이미지 파일로 저장
    plt.savefig(image_file_name, dpi=300, bbox_inches='tight')
    plt.close()

    # 소요 시간 계산
    end_time = time.time()
    elapsed_time = end_time - start_time

    # 보고서 생성
    report = generate_report(
        df=dataFile,
        x_column=x_column,
        y_column=y_column,
        image_file_name=image_file_name,
        color=color,
        xlabel=xlabel if xlabel else x_column,
        ylabel=ylabel if ylabel else y_column,
        elapsed_time=elapsed_time
    )

    return image_file_name, report
