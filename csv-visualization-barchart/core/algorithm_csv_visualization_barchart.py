import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import plot
import time
import os
from datetime import datetime
from typing import Dict, Any, Tuple, Optional

def create_image_barchart(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    image_file_name: str,
    design_params: Dict[str, Any]
) -> None:
    """
    matplotlib을 사용하여 이미지 막대 그래프를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 데이터프레임
    - x_column (str): x축 컬럼명
    - y_column (str): y축 컬럼명
    - image_file_name (str): 저장할 이미지 파일명
    - design_params (Dict[str, Any]): 디자인 파라미터 (common, image 키 포함)
    """
    # 파라미터 추출
    common_params = design_params.get('common', {})
    image_params = design_params.get('image', {})
    
    # matplotlib 스타일 설정
    plt.style.use(image_params.get('matplotlib_style', 'default'))
    
    # 그래프 크기 설정
    fig_size = image_params.get('figure_size', {'width': 12, 'height': 8})
    plt.figure(figsize=(fig_size['width'], fig_size['height']))
    
    # x축과 y축 데이터 추출
    x_data = df[x_column]
    y_data = df[y_column]
    
    # 막대 그래프 생성
    bar_color = image_params.get('bar_color', 'steelblue')
    edge_color = image_params.get('edge_color', 'black')
    edge_width = image_params.get('edge_width', 0.5)
    alpha = common_params.get('alpha', 0.8)
    
    bars = plt.bar(x_data, y_data, 
                   color=bar_color, 
                   edgecolor=edge_color, 
                   linewidth=edge_width,
                   alpha=alpha)
    
    # 축 레이블 설정
    xlabel = common_params.get('xlabel', x_column)
    ylabel = common_params.get('ylabel', y_column)
    plt.xlabel(xlabel, fontsize=image_params.get('xlabel_fontsize', 12))
    plt.ylabel(ylabel, fontsize=image_params.get('ylabel_fontsize', 12))
    
    # 제목 설정
    title = common_params.get('title', f'{xlabel} vs {ylabel}')
    plt.title(title, fontsize=image_params.get('title_fontsize', 14), fontweight='bold')
    
    # x축 레이블 회전
    rotation = common_params.get('xlabel_rotation', 45)
    plt.xticks(rotation=rotation, ha='right')
    
    # 그리드 설정
    if image_params.get('show_grid', True):
        plt.grid(True, alpha=0.3, linestyle='--')
    
    # 막대 위에 값 표시
    if common_params.get('show_values', False):
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}', ha='center', va='bottom',
                    fontsize=image_params.get('value_fontsize', 10))
    
    # 레이아웃 조정
    plt.tight_layout()
    
    # 이미지 저장
    dpi = image_params.get('dpi', 300)
    plt.savefig(image_file_name, dpi=dpi, bbox_inches='tight')
    plt.close()

def create_interactive_barchart(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    html_file_name: str,
    design_params: Dict[str, Any]
) -> None:
    """
    plotly를 사용하여 인터랙티브 막대 그래프를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 데이터프레임
    - x_column (str): x축 컬럼명
    - y_column (str): y축 컬럼명
    - html_file_name (str): 저장할 HTML 파일명
    - design_params (Dict[str, Any]): 디자인 파라미터 (common, interactive 키 포함)
    """
    # 파라미터 추출
    common_params = design_params.get('common', {})
    interactive_params = design_params.get('interactive', {})
    
    # 기본 색상 팔레트
    color_palette = interactive_params.get('color_palette', 'viridis')
    
    # plotly express로 막대 그래프 생성
    fig = px.bar(df, 
                 x=x_column, 
                 y=y_column,
                 color=y_column if interactive_params.get('color_by_value', False) else None,
                 color_continuous_scale=color_palette,
                 title=common_params.get('title', f'{x_column} vs {y_column}'))
    
    # 레이아웃 업데이트
    fig.update_layout(
        title_font_size=interactive_params.get('title_fontsize', 18),
        title_x=0.5,  # 제목 중앙 정렬
        xaxis_title=common_params.get('xlabel', x_column),
        yaxis_title=common_params.get('ylabel', y_column),
        xaxis_title_font_size=interactive_params.get('xlabel_fontsize', 14),
        yaxis_title_font_size=interactive_params.get('ylabel_fontsize', 14),
        font_family=interactive_params.get('font_family', 'Arial'),
        plot_bgcolor=interactive_params.get('plot_bgcolor', 'white'),
        paper_bgcolor=interactive_params.get('paper_bgcolor', 'white'),
        width=interactive_params.get('width', 1000),
        height=interactive_params.get('height', 600),
        margin=dict(l=50, r=50, t=80, b=50)
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
    
    # 막대 스타일 설정
    fig.update_traces(
        marker_line_color=interactive_params.get('edge_color', 'black'),
        marker_line_width=interactive_params.get('edge_width', 1),
        opacity=common_params.get('alpha', 0.8),
        texttemplate=common_params.get('show_values', False) and '%{y:.1f}' or None,
        textposition='outside'
    )
    
    # 호버 템플릿 설정
    hover_template = interactive_params.get('hover_template', 
                                     f'<b>%{{x}}</b><br>{y_column}: %{{y}}<br><extra></extra>')
    fig.update_traces(hovertemplate=hover_template)
    
    # HTML 파일로 저장
    plot(fig, filename=html_file_name, auto_open=False)

def generate_report(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    output_file_name: str,
    design_params: Dict[str, Any],
    elapsed_time: float,
    chart_type: str
) -> str:
    """
    막대 그래프 생성 작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - x_column (str): x축에 사용된 컬럼명
    - y_column (str): y축에 사용된 컬럼명
    - output_file_name (str): 저장된 파일 경로
    - design_params (Dict[str, Any]): 사용된 디자인 파라미터
    - elapsed_time (float): 소요 시간 (초)
    - chart_type (str): 차트 타입 ('image' 또는 'interactive')
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    report = f"""# 막대 그래프 생성 작업 보고서

## 1. 작업 개요
- **작업 유형**: {chart_type.title()} 막대 그래프 생성
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **행 수**: {len(df):,}행
- **컬럼 수**: {len(df.columns)}개
- **컬럼 목록**: {', '.join(df.columns)}

## 3. 시각화 설정
- **X축 컬럼**: {x_column}
- **Y축 컬럼**: {y_column}
- **차트 타입**: {chart_type}
- **출력 파일**: {output_file_name}

## 4. 디자인 파라미터
- **제목**: {design_params.get('common', {}).get('title', f'{x_column} vs {y_column}')}
- **X축 레이블**: {design_params.get('common', {}).get('xlabel', x_column)}
- **Y축 레이블**: {design_params.get('common', {}).get('ylabel', y_column)}
- **투명도**: {design_params.get('common', {}).get('alpha', 0.8)}
- **값 표시**: {design_params.get('common', {}).get('show_values', False)}
- **X축 레이블 회전**: {design_params.get('common', {}).get('xlabel_rotation', 45)}도

## 5. 처리 결과
- **X축 고유값 개수**: {df[x_column].nunique()}개
- **Y축 데이터 범위**: {df[y_column].min():.2f} ~ {df[y_column].max():.2f}
- **Y축 평균값**: {df[y_column].mean():.2f}
- **Y축 중앙값**: {df[y_column].median():.2f}

## 6. 성능 지표
- **처리 속도**: {len(df) / elapsed_time:.2f} 행/초
- **메모리 사용량**: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB

## 7. 작업 상태
- **상태**: 성공
- **처리 결과**: {chart_type.title()} 막대 그래프가 성공적으로 생성됨
"""
    return report

def solution(
    data: object, 
    x_column: str, 
    y_column: str, 
    output_file_name: str, 
    chart_mode: str = 'image',
    design_params: Optional[Dict[str, Any]] = None
) -> Tuple[str, str]:
    """
    CSV 파일에서 두 컬럼을 사용하여 막대 그래프를 생성하는 함수.
    chart_mode에 따라 이미지 또는 인터랙티브 차트를 생성합니다.

    Parameters:
    - data: CSV 파일 경로 또는 StringIO 객체
    - x_column: x축에 사용할 컬럼명 (카테고리)
    - y_column: y축에 사용할 컬럼명 (수치값)
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
        create_image_barchart(dataFile, x_column, y_column, actual_output_file, design_params)
        chart_type = 'image'
    elif chart_mode == 'interactive':
        # 인터랙티브 차트 생성 (HTML 확장자 추가)
        actual_output_file = output_file_name if output_file_name.endswith('.html') else f"{output_file_name}.html"
        create_interactive_barchart(dataFile, x_column, y_column, actual_output_file, design_params)
        chart_type = 'interactive'
    else:
        raise ValueError(f"지원하지 않는 차트 모드입니다: {chart_mode}. 'image' 또는 'interactive'를 사용하세요.")
    
    # 소요 시간 계산
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 보고서 생성
    report = generate_report(
        df=dataFile,
        x_column=x_column,
        y_column=y_column,
        output_file_name=actual_output_file,
        design_params=design_params,
        elapsed_time=elapsed_time,
        chart_type=chart_type
    )
    
    return actual_output_file, report