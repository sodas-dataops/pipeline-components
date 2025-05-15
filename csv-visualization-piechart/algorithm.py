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
    feature_name: str,
    image_file_name: str,
    chart_title: str,
    colors: list,
    explode: list,
    shadow: bool,
    elapsed_time: float
) -> str:
    """
    파이 차트 생성 작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - feature_name (str): 시각화한 feature의 컬럼명
    - image_file_name (str): 저장된 이미지 파일 경로
    - chart_title (str): 차트 제목
    - colors (list): 사용된 색상 목록
    - explode (list): 파이 조각 분리 정도
    - shadow (bool): 그림자 표시 여부
    - elapsed_time (float): 소요 시간 (초)
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    # 카테고리별 통계 계산
    feature_counts = df[feature_name].value_counts()
    total = feature_counts.sum()
    percentages = (feature_counts / total * 100).round(2)
    
    report = f"""# 파이 차트 생성 작업 보고서

## 1. 작업 개요
- **작업 유형**: 파이 차트 생성
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **행 수**: {len(df):,}행
- **컬럼 수**: {len(df.columns)}개
- **컬럼 목록**: {', '.join(df.columns)}

## 3. 시각화 설정
- **대상 컬럼**: {feature_name}
- **차트 제목**: {chart_title}
- **색상 수**: {len(colors) if colors else '기본값'}
- **그림자 효과**: {'사용' if shadow else '미사용'}

## 4. 처리 결과
- **출력 파일**: {image_file_name}
- **카테고리 수**: {len(feature_counts)}개
- **총 데이터 수**: {total:,}개
- **카테고리별 비율**:
{chr(10).join([f'  - {category}: {percentage}% ({count:,}개)' for category, (count, percentage) in zip(feature_counts.index, zip(feature_counts.values, percentages))])}

## 5. 성능 지표
- **처리 속도**: {len(df) / elapsed_time:.2f} 행/초
- **메모리 사용량**: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB

## 6. 작업 상태
- **상태**: 성공
- **처리 결과**: 파이 차트가 성공적으로 생성됨
"""
    return report

def solution(data: object, feature_name: str, image_file_name: str,
             chart_title: str = "Pie Chart",  # 차트 제목 추가
             colors: list = None, explode: list = None, shadow: bool = False) -> tuple:
    """
    CSV 파일에서 특정 feature를 기준으로 파이 차트를 생성하여 이미지 파일로 저장하는 함수.

    Parameters:
    - data: CSV 파일 경로
    - feature_name: 파이 차트를 만들 feature의 컬럼명
    - image_file_name: 저장할 이미지 파일 이름
    - chart_title: 차트 제목
    - colors: 색상 목록 (선택사항)
    - explode: 파이 조각의 분리 정도 (선택사항)
    - shadow: 그림자 표시 여부 (선택사항, 기본값 False)
    
    Returns:
    - tuple: (이미지 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    
    # CSV 데이터 로드
    dataFile = pd.read_csv(data)

    # 시스템 기본 폰트 설정
    font_path = get_font_path()
    font = font_manager.FontProperties(fname=font_path).get_name()
    rcParams['font.family'] = font
    
    # feature의 고유 값과 해당 값의 개수 구하기
    feature_counts = dataFile[feature_name].value_counts()
    total = feature_counts.sum()  # 전체 값 합계

    # explode의 길이가 feature_counts와 맞지 않으면 기본값으로 설정
    if explode is not None and len(explode) != len(feature_counts):
        explode = [0] * len(feature_counts)

    # 사용자 정의 autopct 함수
    def custom_autopct(pct, all_vals, all_labels):
        absolute = int(round(pct * total / 100))  # 절대 값 계산
        label = all_labels[all_vals.index(absolute)]  # 레이블 가져오기
        return f"{label}({absolute}, {pct:.1f}%)"  # 레이블, 값, 퍼센트 반환

    # 파이 차트 생성
    plt.figure(figsize=(10, 8))  # 차트 크기 조정
    wedges, texts, autotexts = plt.pie(
        feature_counts,
        labels=None,  # 레이블 제외
        autopct=lambda pct: custom_autopct(pct, feature_counts.tolist(), feature_counts.index.tolist()),
        startangle=90,
        colors=colors,
        explode=explode,
        shadow=shadow
    )
    
    # 차트의 형태를 원으로 맞추기
    plt.axis('equal')

    # 텍스트 크기와 스타일 설정
    for autotext in autotexts:
        autotext.set_fontsize(24)
        # autotext.set_color('white')  # 텍스트 색상을 흰색으로 설정 (조각과 대조)
        autotext.set_weight('bold')

    # 차트 제목 추가
    plt.title(chart_title, fontsize=48)

    # legend 추가 (폰트 크기 조정)
    plt.legend(
        wedges,
        feature_counts.index,
        # title="Legend",
        loc="center left",
        bbox_to_anchor=(1, 0.5),  # 차트 오른쪽에 위치, 가운데 정렬
        fontsize=18  # 레전드 폰트 크기 설정
    )
    
    # 레이아웃 자동 조정
    plt.tight_layout()

    # 이미지 파일로 저장 (크기를 자동 조정)
    plt.savefig(image_file_name, dpi=300, bbox_inches="tight")
    plt.close()

    # 소요 시간 계산
    end_time = time.time()
    elapsed_time = end_time - start_time

    # 보고서 생성
    report = generate_report(
        df=dataFile,
        feature_name=feature_name,
        image_file_name=image_file_name,
        chart_title=chart_title,
        colors=colors,
        explode=explode,
        shadow=shadow,
        elapsed_time=elapsed_time
    )

    return image_file_name, report