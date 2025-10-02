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
from typing import Dict, Any, Tuple, Optional

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

def create_image_boxplot(
    df: pd.DataFrame,
    group_by_column: str,
    value_column: str,
    image_file_name: str,
    design_params: Dict[str, Any]
) -> None:
    """
    matplotlib을 사용하여 이미지 박스플롯을 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 데이터프레임
    - group_by_column (str): 그룹화 기준 컬럼명
    - value_column (str): 값 컬럼명
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
    
    # Unicode minus 문제 해결
    rcParams['axes.unicode_minus'] = False
    
    # matplotlib 스타일 설정
    plt.style.use(image_params.get('matplotlib_style', 'default'))
    
    # 그래프 크기 설정
    fig_size = image_params.get('figure_size', {'width': 10, 'height': 8})
    plt.figure(figsize=(fig_size['width'], fig_size['height']))
    
    # 결측값 제거
    df_clean = df.dropna(subset=[group_by_column, value_column])
    
    # 그룹화
    grouped_data = [df_clean.loc[df_clean[group_by_column] == group, value_column].values
                    for group in df_clean[group_by_column].unique()]
    
    # 박스플롯 생성
    box_color = image_params.get('box_color', 'steelblue')
    whisker_color = image_params.get('whisker_color', 'black')
    median_color = image_params.get('median_color', 'red')
    outlier_color = image_params.get('outlier_color', 'red')
    
    bp = plt.boxplot(grouped_data, 
                     labels=df_clean[group_by_column].unique(),
                     patch_artist=True,
                     boxprops=dict(facecolor=box_color, alpha=common_params.get('alpha', 0.7)),
                     whiskerprops=dict(color=whisker_color),
                     capprops=dict(color=whisker_color),
                     medianprops=dict(color=median_color, linewidth=2),
                     flierprops=dict(marker='o', markerfacecolor=outlier_color, markersize=3))
    
    # 축 레이블 설정
    xlabel = common_params.get('xlabel', group_by_column)
    ylabel = common_params.get('ylabel', value_column)
    plt.xlabel(xlabel, fontsize=image_params.get('xlabel_fontsize', 12))
    plt.ylabel(ylabel, fontsize=image_params.get('ylabel_fontsize', 12))
    
    # 제목 설정
    title = common_params.get('title', f'Box Plot of {value_column} by {group_by_column}')
    plt.title(title, fontsize=image_params.get('title_fontsize', 14), fontweight='bold')
    
    # x축 레이블 회전
    rotation = common_params.get('xlabel_rotation', 45)
    plt.xticks(rotation=rotation, ha='right')
    
    # 그리드 설정
    if image_params.get('show_grid', True):
        plt.grid(True, alpha=0.3, linestyle='--')
    
    # 레이아웃 조정
    plt.tight_layout()
    
    # 이미지 저장
    dpi = image_params.get('dpi', 300)
    plt.savefig(image_file_name, dpi=dpi, bbox_inches='tight')
    plt.close()

def create_interactive_boxplot(
    df: pd.DataFrame,
    group_by_column: str,
    value_column: str,
    html_file_name: str,
    design_params: Dict[str, Any]
) -> None:
    """
    plotly를 사용하여 인터랙티브 박스플롯을 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 데이터프레임
    - group_by_column (str): 그룹화 기준 컬럼명
    - value_column (str): 값 컬럼명
    - html_file_name (str): 저장할 HTML 파일명
    - design_params (Dict[str, Any]): 디자인 파라미터 (common, interactive 키 포함)
    """
    # 파라미터 추출
    common_params = design_params.get('common', {})
    interactive_params = design_params.get('interactive', {})
    
    # 결측값 제거
    df_clean = df.dropna(subset=[group_by_column, value_column])
    
    # plotly express로 박스플롯 생성
    fig = px.box(df_clean, 
                 x=group_by_column, 
                 y=value_column,
                 color=group_by_column if interactive_params.get('color_by_group', True) else None,
                 title=common_params.get('title', f'Box Plot of {value_column} by {group_by_column}'))
    
    # 레이아웃 업데이트
    fig.update_layout(
        title_font_size=interactive_params.get('title_fontsize', 18),
        title_x=0.5,  # 제목 중앙 정렬
        xaxis_title=common_params.get('xlabel', group_by_column),
        yaxis_title=common_params.get('ylabel', value_column),
        xaxis_title_font_size=interactive_params.get('xlabel_fontsize', 14),
        yaxis_title_font_size=interactive_params.get('ylabel_fontsize', 14),
        font_family=interactive_params.get('font_family', 'Arial'),
        plot_bgcolor=interactive_params.get('plot_bgcolor', 'white'),
        paper_bgcolor=interactive_params.get('paper_bgcolor', 'white'),
        width=interactive_params.get('width', 1000),
        height=interactive_params.get('height', 600),
        margin=dict(l=50, r=50, t=80, b=50),
        showlegend=interactive_params.get('show_legend', True)
    )
    
    # x축 설정
    fig.update_xaxes(
        tickangle=common_params.get('xlabel_rotation', 45),
        tickfont_size=interactive_params.get('tick_fontsize', 12),
        showgrid=interactive_params.get('show_xgrid', True),
        gridcolor='lightgray',
        gridwidth=1
    )
    
    # y축 설정
    fig.update_yaxes(
        tickfont_size=interactive_params.get('tick_fontsize', 12),
        showgrid=interactive_params.get('show_ygrid', True),
        gridcolor='lightgray',
        gridwidth=1
    )
    
    # 박스플롯 스타일 설정
    fig.update_traces(
        opacity=common_params.get('alpha', 0.7),
        line=dict(width=interactive_params.get('box_line_width', 2)),
        marker=dict(
            size=interactive_params.get('outlier_size', 4),
            opacity=interactive_params.get('outlier_alpha', 0.8)
        )
    )
    
    # 호버 템플릿 설정
    hover_template = interactive_params.get('hover_template', 
                                     f'<b>%{{x}}</b><br>{value_column}: %{{y}}<br><extra></extra>')
    fig.update_traces(hovertemplate=hover_template)
    
    # HTML 파일로 저장
    plot(fig, filename=html_file_name, auto_open=False)

def generate_report(
    df: pd.DataFrame,
    group_by_column: str,
    value_column: str,
    output_file_name: str,
    design_params: Dict[str, Any],
    elapsed_time: float,
    chart_type: str
) -> str:
    """
    박스플롯 생성 작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - group_by_column (str): 그룹화 기준 컬럼명
    - value_column (str): 값 컬럼명
    - output_file_name (str): 저장된 파일 경로
    - design_params (Dict[str, Any]): 사용된 디자인 파라미터
    - elapsed_time (float): 소요 시간 (초)
    - chart_type (str): 차트 타입 ('image' 또는 'interactive')
    
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
- **작업 유형**: {chart_type.title()} 박스플롯 생성
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **행 수**: {len(df):,}행
- **컬럼 수**: {len(df.columns)}개
- **컬럼 목록**: {', '.join(df.columns)}

## 3. 시각화 설정
- **그룹화 컬럼**: {group_by_column}
- **값 컬럼**: {value_column}
- **차트 타입**: {chart_type}
- **출력 파일**: {output_file_name}

## 4. 디자인 파라미터
- **제목**: {design_params.get('common', {}).get('title', f'Box Plot of {value_column} by {group_by_column}')}
- **X축 레이블**: {design_params.get('common', {}).get('xlabel', group_by_column)}
- **Y축 레이블**: {design_params.get('common', {}).get('ylabel', value_column)}
- **투명도**: {design_params.get('common', {}).get('alpha', 0.7)}
- **X축 레이블 회전**: {design_params.get('common', {}).get('xlabel_rotation', 45)}도

## 5. 처리 결과
- **그룹 수**: {len(stats)}개
- **그룹별 통계**:
{chr(10).join([f'  - {group}:' + chr(10) + 
              f'    - 데이터 수: {stats[group]["count"]:,}개' + chr(10) +
              f'    - 평균: {stats[group]["mean"]:.2f}' + chr(10) +
              f'    - 중앙값: {stats[group]["median"]:.2f}' + chr(10) +
              f'    - 표준편차: {stats[group]["std"]:.2f}' + chr(10) +
              f'    - 범위: {stats[group]["min"]:.2f} ~ {stats[group]["max"]:.2f}'
              for group in stats])}

## 6. 성능 지표
- **처리 속도**: {len(df) / elapsed_time:.2f} 행/초
- **메모리 사용량**: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB

## 7. 작업 상태
- **상태**: 성공
- **처리 결과**: {chart_type.title()} 박스플롯이 성공적으로 생성됨
"""
    return report

def solution(
    data: object, 
    group_by_column: str, 
    value_column: str, 
    output_file_name: str, 
    chart_mode: str = 'image',
    design_params: Optional[Dict[str, Any]] = None
) -> Tuple[str, str]:
    """
    CSV 파일에서 그룹화된 데이터의 박스플롯을 생성하는 함수.
    chart_mode에 따라 이미지 또는 인터랙티브 차트를 생성합니다.

    Parameters:
    - data: CSV 파일 경로 또는 StringIO 객체
    - group_by_column: 그룹화 기준 컬럼명
    - value_column: 박스플롯에 사용할 값 컬럼명
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
    dataFile = pd.read_csv(data, low_memory=False)
    
    # 차트 모드에 따라 차트 생성 및 실제 파일 경로 결정
    if chart_mode == 'image':
        # 이미지 차트 생성 (기본적으로 PNG 확장자 추가)
        actual_output_file = output_file_name if output_file_name.endswith(('.png', '.jpg', '.jpeg', '.svg', '.pdf')) else f"{output_file_name}.png"
        create_image_boxplot(dataFile, group_by_column, value_column, actual_output_file, design_params)
        chart_type = 'image'
    elif chart_mode == 'interactive':
        # 인터랙티브 차트 생성 (HTML 확장자 추가)
        actual_output_file = output_file_name if output_file_name.endswith('.html') else f"{output_file_name}.html"
        create_interactive_boxplot(dataFile, group_by_column, value_column, actual_output_file, design_params)
        chart_type = 'interactive'
    else:
        raise ValueError(f"지원하지 않는 차트 모드입니다: {chart_mode}. 'image' 또는 'interactive'를 사용하세요.")
    
    # 소요 시간 계산
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 보고서 생성
    report = generate_report(
        df=dataFile,
        group_by_column=group_by_column,
        value_column=value_column,
        output_file_name=actual_output_file,
        design_params=design_params,
        elapsed_time=elapsed_time,
        chart_type=chart_type
    )
    
    return actual_output_file, report