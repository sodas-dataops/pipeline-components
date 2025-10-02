import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import plot
import platform
from matplotlib import rcParams
from matplotlib import font_manager
import time
import os
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List

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

def create_image_piechart(
    df: pd.DataFrame,
    feature_name: str,
    image_file_name: str,
    design_params: Dict[str, Any]
) -> None:
    """
    matplotlib을 사용하여 이미지 파이차트를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 데이터프레임
    - feature_name (str): 파이차트를 생성할 컬럼명
    - image_file_name (str): 저장할 이미지 파일명
    - design_params (Dict[str, Any]): 디자인 파라미터 (common, image 키 포함)
    """
    # 파라미터 추출
    common_params = design_params.get('common', {})
    image_params = design_params.get('image', {})
    
    # 시스템 기본 폰트 설정
    font_path = get_font_path()
    if font_path:
        font = font_manager.FontProperties(fname=font_path).get_name()
        rcParams['font.family'] = font
    
    rcParams['axes.unicode_minus'] = False
    
    # feature의 고유 값과 해당 값의 개수 구하기
    feature_counts = df[feature_name].value_counts()
    total = feature_counts.sum()
    
    # 파라미터 설정
    colors = image_params.get('colors', None)
    explode = image_params.get('explode', None)
    shadow = image_params.get('shadow', False)
    startangle = image_params.get('startangle', 90)
    
    # explode의 길이가 feature_counts와 맞지 않으면 기본값으로 설정
    if explode is not None and len(explode) != len(feature_counts):
        explode = [0] * len(feature_counts)
    
    # 사용자 정의 autopct 함수
    def custom_autopct(pct, all_vals, all_labels):
        absolute = int(round(pct * total / 100))
        label = all_labels[all_vals.index(absolute)]
        return f"{label}({absolute}, {pct:.1f}%)"
    
    # 파이 차트 생성
    fig_size = image_params.get('figure_size', {'width': 10, 'height': 8})
    plt.figure(figsize=(fig_size['width'], fig_size['height']))
    
    wedges, texts, autotexts = plt.pie(
        feature_counts,
        labels=None,
        autopct=lambda pct: custom_autopct(pct, feature_counts.tolist(), feature_counts.index.tolist()),
        startangle=startangle,
        colors=colors,
        explode=explode,
        shadow=shadow
    )
    
    # 차트의 형태를 원으로 맞추기
    plt.axis('equal')
    
    # 텍스트 크기와 스타일 설정
    text_fontsize = image_params.get('text_fontsize', 24)
    for autotext in autotexts:
        autotext.set_fontsize(text_fontsize)
        autotext.set_weight('bold')
    
    # 차트 제목 추가
    title = common_params.get('title', 'Pie Chart')
    title_fontsize = image_params.get('title_fontsize', 48)
    plt.title(title, fontsize=title_fontsize)
    
    # legend 추가
    legend_fontsize = image_params.get('legend_fontsize', 18)
    plt.legend(
        wedges,
        feature_counts.index,
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        fontsize=legend_fontsize
    )
    
    # 레이아웃 자동 조정
    plt.tight_layout()
    
    # 이미지 저장
    dpi = image_params.get('dpi', 300)
    plt.savefig(image_file_name, dpi=dpi, bbox_inches="tight")
    plt.close()

def create_interactive_piechart(
    df: pd.DataFrame,
    feature_name: str,
    html_file_name: str,
    design_params: Dict[str, Any]
) -> None:
    """
    plotly를 사용하여 인터랙티브 파이차트를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 데이터프레임
    - feature_name (str): 파이차트를 생성할 컬럼명
    - html_file_name (str): 저장할 HTML 파일명
    - design_params (Dict[str, Any]): 디자인 파라미터 (common, interactive 키 포함)
    """
    # 파라미터 추출
    common_params = design_params.get('common', {})
    interactive_params = design_params.get('interactive', {})
    
    # feature의 고유 값과 해당 값의 개수 구하기
    feature_counts = df[feature_name].value_counts()
    
    # plotly express로 파이차트 생성
    fig = px.pie(
        values=feature_counts.values,
        names=feature_counts.index,
        title=common_params.get('title', 'Pie Chart')
    )
    
    # 레이아웃 업데이트
    fig.update_layout(
        title_font_size=interactive_params.get('title_fontsize', 24),
        title_x=0.5,
        width=interactive_params.get('width', 800),
        height=interactive_params.get('height', 600),
        font_family=interactive_params.get('font_family', 'Arial'),
        plot_bgcolor=interactive_params.get('plot_bgcolor', 'white'),
        paper_bgcolor=interactive_params.get('paper_bgcolor', 'white'),
        showlegend=interactive_params.get('show_legend', True),
        legend=dict(
            font_size=interactive_params.get('legend_fontsize', 14),
            orientation=interactive_params.get('legend_orientation', 'v')
        )
    )
    
    # 파이차트 스타일 설정
    fig.update_traces(
        textposition=interactive_params.get('text_position', 'inside'),
        textinfo=interactive_params.get('text_info', 'label+percent'),
        textfont_size=interactive_params.get('text_fontsize', 12),
        marker=dict(
            line=dict(
                width=interactive_params.get('line_width', 2),
                color=interactive_params.get('line_color', 'white')
            )
        ),
        rotation=interactive_params.get('rotation', 0)
    )
    
    # 호버 템플릿 설정
    hover_template = interactive_params.get('hover_template', 
                                     '<b>%{label}</b><br>Value: %{value}<br>Percentage: %{percent}<br><extra></extra>')
    fig.update_traces(hovertemplate=hover_template)
    
    # HTML 파일로 저장
    plot(fig, filename=html_file_name, auto_open=False)

def generate_report(
    df: pd.DataFrame,
    feature_name: str,
    output_file_name: str,
    design_params: Dict[str, Any],
    elapsed_time: float,
    chart_type: str
) -> str:
    """
    파이 차트 생성 작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - feature_name (str): 시각화한 feature의 컬럼명
    - output_file_name (str): 저장된 파일 경로
    - design_params (Dict[str, Any]): 사용된 디자인 파라미터
    - elapsed_time (float): 소요 시간 (초)
    - chart_type (str): 차트 타입 ('image' 또는 'interactive')
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    # 카테고리별 통계 계산
    feature_counts = df[feature_name].value_counts()
    total = feature_counts.sum()
    percentages = (feature_counts / total * 100).round(2)
    
    report = f"""# 파이 차트 생성 작업 보고서

## 1. 작업 개요
- **작업 유형**: {chart_type.title()} 파이 차트 생성
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **행 수**: {len(df):,}행
- **컬럼 수**: {len(df.columns)}개
- **컬럼 목록**: {', '.join(df.columns)}

## 3. 시각화 설정
- **대상 컬럼**: {feature_name}
- **차트 타입**: {chart_type}
- **출력 파일**: {output_file_name}

## 4. 디자인 파라미터
- **제목**: {design_params.get('common', {}).get('title', 'Pie Chart')}
- **카테고리 수**: {len(feature_counts)}개

## 5. 처리 결과
- **총 데이터 수**: {total:,}개
- **카테고리별 비율**:
{chr(10).join([f'  - {category}: {percentage}% ({count:,}개)' for category, (count, percentage) in zip(feature_counts.index, zip(feature_counts.values, percentages))])}

## 6. 성능 지표
- **처리 속도**: {len(df) / elapsed_time:.2f} 행/초
- **메모리 사용량**: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB

## 7. 작업 상태
- **상태**: 성공
- **처리 결과**: {chart_type.title()} 파이 차트가 성공적으로 생성됨
"""
    return report

def solution(
    data: object, 
    feature_name: str, 
    output_file_name: str, 
    chart_mode: str = 'image',
    design_params: Optional[Dict[str, Any]] = None
) -> Tuple[str, str]:
    """
    CSV 파일에서 특정 feature를 기준으로 파이 차트를 생성하는 함수.
    chart_mode에 따라 이미지 또는 인터랙티브 차트를 생성합니다.

    Parameters:
    - data: CSV 파일 경로 또는 StringIO 객체
    - feature_name: 파이 차트를 만들 feature의 컬럼명
    - output_file_name: 저장할 파일 이름
    - chart_mode: 차트 모드 ('image' 또는 'interactive')
    - design_params: 디자인 파라미터 (선택사항)
    
    Returns:
    - tuple: (출력 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    
    # 기본 디자인 파라미터 설정
    if design_params is None:
        design_params = {}
    
    # CSV 데이터 로드
    dataFile = pd.read_csv(data)
    
    # 차트 모드에 따라 차트 생성 및 실제 파일 경로 결정
    if chart_mode == 'image':
        # 이미지 차트 생성 (기본적으로 PNG 확장자 추가)
        actual_output_file = output_file_name if output_file_name.endswith(('.png', '.jpg', '.jpeg', '.svg', '.pdf')) else f"{output_file_name}.png"
        create_image_piechart(dataFile, feature_name, actual_output_file, design_params)
        chart_type = 'image'
    elif chart_mode == 'interactive':
        # 인터랙티브 차트 생성 (HTML 확장자 추가)
        actual_output_file = output_file_name if output_file_name.endswith('.html') else f"{output_file_name}.html"
        create_interactive_piechart(dataFile, feature_name, actual_output_file, design_params)
        chart_type = 'interactive'
    else:
        raise ValueError(f"지원하지 않는 차트 모드입니다: {chart_mode}. 'image' 또는 'interactive'를 사용하세요.")
    
    # 소요 시간 계산
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 보고서 생성
    report = generate_report(
        df=dataFile,
        feature_name=feature_name,
        output_file_name=actual_output_file,
        design_params=design_params,
        elapsed_time=elapsed_time,
        chart_type=chart_type
    )
    
    return actual_output_file, report