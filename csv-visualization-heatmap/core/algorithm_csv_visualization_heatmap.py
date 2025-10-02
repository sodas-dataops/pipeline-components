import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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
from io import StringIO

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

def create_image_heatmap(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    value_column: str,
    image_file_name: str,
    design_params: Dict[str, Any]
) -> None:
    """
    matplotlib을 사용하여 이미지 히트맵을 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 데이터프레임
    - x_column (str): X축 컬럼명
    - y_column (str): Y축 컬럼명
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
    
    rcParams['axes.unicode_minus'] = False
    
    # 피벗 테이블 생성
    pivot_table = df.pivot_table(
        values=value_column, 
        index=y_column, 
        columns=x_column, 
        aggfunc='mean',
        fill_value=0
    )
    
    # 파라미터 설정
    cmap = image_params.get('colormap', 'viridis')
    fig_size = image_params.get('figure_size', {'width': 12, 'height': 8})
    annot = image_params.get('annotate', False)
    fmt = image_params.get('format', '.2f')
    
    # 히트맵 생성
    plt.figure(figsize=(fig_size['width'], fig_size['height']))
    
    sns.heatmap(
        pivot_table,
        cmap=cmap,
        annot=annot,
        fmt=fmt,
        cbar_kws={'label': value_column}
    )
    
    # 차트 제목 및 라벨 설정
    title = common_params.get('title', 'Heatmap')
    title_fontsize = image_params.get('title_fontsize', 16)
    plt.title(title, fontsize=title_fontsize)
    
    xlabel = common_params.get('xlabel', x_column)
    ylabel = common_params.get('ylabel', y_column)
    label_fontsize = image_params.get('label_fontsize', 12)
    plt.xlabel(xlabel, fontsize=label_fontsize)
    plt.ylabel(ylabel, fontsize=label_fontsize)
    
    # 레이아웃 자동 조정
    plt.tight_layout()
    
    # 이미지 저장
    dpi = image_params.get('dpi', 300)
    plt.savefig(image_file_name, dpi=dpi, bbox_inches="tight")
    plt.close()

def create_interactive_heatmap(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    value_column: str,
    html_file_name: str,
    design_params: Dict[str, Any]
) -> None:
    """
    plotly를 사용하여 인터랙티브 히트맵을 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 데이터프레임
    - x_column (str): X축 컬럼명
    - y_column (str): Y축 컬럼명
    - value_column (str): 값 컬럼명
    - html_file_name (str): 저장할 HTML 파일명
    - design_params (Dict[str, Any]): 디자인 파라미터 (common, interactive 키 포함)
    """
    # 파라미터 추출
    common_params = design_params.get('common', {})
    interactive_params = design_params.get('interactive', {})
    
    # 피벗 테이블 생성
    pivot_table = df.pivot_table(
        values=value_column, 
        index=y_column, 
        columns=x_column, 
        aggfunc='mean',
        fill_value=0
    )
    
    # plotly 히트맵 생성
    fig = go.Figure(data=go.Heatmap(
        z=pivot_table.values,
        x=pivot_table.columns,
        y=pivot_table.index,
        colorscale=interactive_params.get('colorscale', 'Viridis'),
        hoverongaps=False,
        hovertemplate=f'<b>{x_column}</b>: %{{x}}<br>' +
                     f'<b>{y_column}</b>: %{{y}}<br>' +
                     f'<b>{value_column}</b>: %{{z}}<br>' +
                     '<extra></extra>'
    ))
    
    # 레이아웃 업데이트
    fig.update_layout(
        title=common_params.get('title', 'Heatmap'),
        title_font_size=interactive_params.get('title_fontsize', 20),
        title_x=0.5,
        width=interactive_params.get('width', 1000),
        height=interactive_params.get('height', 600),
        xaxis_title=common_params.get('xlabel', x_column),
        yaxis_title=common_params.get('ylabel', y_column),
        font_family=interactive_params.get('font_family', 'Arial'),
        plot_bgcolor=interactive_params.get('plot_bgcolor', 'white'),
        paper_bgcolor=interactive_params.get('paper_bgcolor', 'white')
    )
    
    # HTML 파일로 저장
    plot(fig, filename=html_file_name, auto_open=False)

def generate_report(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    value_column: str,
    output_file_name: str,
    design_params: Dict[str, Any],
    elapsed_time: float,
    chart_type: str
) -> str:
    """
    히트맵 생성 작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - x_column (str): X축 컬럼명
    - y_column (str): Y축 컬럼명
    - value_column (str): 값 컬럼명
    - output_file_name (str): 저장된 파일 경로
    - design_params (Dict[str, Any]): 사용된 디자인 파라미터
    - elapsed_time (float): 소요 시간 (초)
    - chart_type (str): 차트 타입 ('image' 또는 'interactive')
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    # 피벗 테이블 생성
    pivot_table = df.pivot_table(
        values=value_column, 
        index=y_column, 
        columns=x_column, 
        aggfunc='mean',
        fill_value=0
    )
    
    # 통계 계산
    unique_x_values = df[x_column].nunique()
    unique_y_values = df[y_column].nunique()
    total_cells = unique_x_values * unique_y_values
    non_zero_cells = (pivot_table != 0).sum().sum()
    
    report = f"""# 히트맵 생성 작업 보고서

## 1. 작업 개요
- **작업 유형**: {chart_type.title()} 히트맵 생성
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **행 수**: {len(df):,}행
- **컬럼 수**: {len(df.columns)}개
- **컬럼 목록**: {', '.join(df.columns)}

## 3. 시각화 설정
- **X축 컬럼**: {x_column}
- **Y축 컬럼**: {y_column}
- **값 컬럼**: {value_column}
- **차트 타입**: {chart_type}
- **출력 파일**: {output_file_name}

## 4. 디자인 파라미터
- **제목**: {design_params.get('common', {}).get('title', 'Heatmap')}
- **X축 라벨**: {design_params.get('common', {}).get('xlabel', x_column)}
- **Y축 라벨**: {design_params.get('common', {}).get('ylabel', y_column)}

## 5. 처리 결과
- **고유 X값 수**: {unique_x_values:,}개
- **고유 Y값 수**: {unique_y_values:,}개
- **총 셀 수**: {total_cells:,}개
- **비어있지 않은 셀 수**: {non_zero_cells:,}개
- **데이터 밀도**: {(non_zero_cells / total_cells * 100):.2f}%

## 6. 성능 지표
- **처리 속도**: {len(df) / elapsed_time:.2f} 행/초
- **메모리 사용량**: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB

## 7. 작업 상태
- **상태**: 성공
- **처리 결과**: {chart_type.title()} 히트맵이 성공적으로 생성됨
"""
    return report

def solution(
    data: object, 
    x_column: str, 
    y_column: str, 
    value_column: str, 
    output_file_name: str, 
    chart_mode: str = 'image',
    design_params: Optional[Dict[str, Any]] = None
) -> Tuple[str, str]:
    """
    CSV 파일에서 히트맵을 생성하는 함수.
    chart_mode에 따라 이미지 또는 인터랙티브 차트를 생성합니다.

    Parameters:
    - data: CSV 파일 경로 또는 StringIO 객체
    - x_column: X축에 사용할 컬럼명
    - y_column: Y축에 사용할 컬럼명
    - value_column: 히트맵의 값으로 사용할 컬럼명
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
    
    # 컬럼 존재 확인
    if x_column not in dataFile.columns:
        raise ValueError(f"X축 컬럼 '{x_column}'이 데이터에 존재하지 않습니다.")
    if y_column not in dataFile.columns:
        raise ValueError(f"Y축 컬럼 '{y_column}'이 데이터에 존재하지 않습니다.")
    if value_column not in dataFile.columns:
        raise ValueError(f"값 컬럼 '{value_column}'이 데이터에 존재하지 않습니다.")
    
    # 차트 모드에 따라 차트 생성 및 실제 파일 경로 결정
    if chart_mode == 'image':
        # 이미지 차트 생성 (기본적으로 PNG 확장자 추가)
        actual_output_file = output_file_name if output_file_name.endswith(('.png', '.jpg', '.jpeg', '.svg', '.pdf')) else f"{output_file_name}.png"
        create_image_heatmap(dataFile, x_column, y_column, value_column, actual_output_file, design_params)
        chart_type = 'image'
    elif chart_mode == 'interactive':
        # 인터랙티브 차트 생성 (HTML 확장자 추가)
        actual_output_file = output_file_name if output_file_name.endswith('.html') else f"{output_file_name}.html"
        create_interactive_heatmap(dataFile, x_column, y_column, value_column, actual_output_file, design_params)
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
        value_column=value_column,
        output_file_name=actual_output_file,
        design_params=design_params,
        elapsed_time=elapsed_time,
        chart_type=chart_type
    )
    
    return actual_output_file, report