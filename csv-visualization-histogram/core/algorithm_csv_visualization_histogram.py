import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import plot
import time
import os
import warnings
from datetime import datetime
from typing import Dict, Any, Tuple, Optional

def is_numeric_column(series: pd.Series) -> bool:
    """
    시리즈가 숫자형 데이터인지 확인하는 함수.
    
    Parameters:
    - series (pd.Series): 확인할 시리즈
    
    Returns:
    - bool: 숫자형이면 True, 아니면 False
    """
    try:
        pd.to_numeric(series, errors='raise')
        return True
    except (ValueError, TypeError):
        return False

def create_image_histogram(
    df: pd.DataFrame,
    feature_name: str,
    image_file_name: str,
    design_params: Dict[str, Any]
) -> None:
    """
    matplotlib을 사용하여 이미지 히스토그램을 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 데이터프레임
    - feature_name (str): 히스토그램을 생성할 컬럼명
    - image_file_name (str): 저장할 이미지 파일명
    - design_params (Dict[str, Any]): 디자인 파라미터 (common, image 키 포함)
    """
    # 파라미터 추출
    common_params = design_params.get('common', {})
    image_params = design_params.get('image', {})
    
    # 데이터 타입 확인
    is_numeric = is_numeric_column(df[feature_name])
    if not is_numeric:
        warnings.warn(f"컬럼 '{feature_name}'은 숫자형이 아닙니다. 카테고리별 빈도 히스토그램을 생성합니다.")
    
    # matplotlib 스타일 설정
    plt.style.use(image_params.get('matplotlib_style', 'default'))
    
    # 그래프 크기 설정
    fig_size = image_params.get('figure_size', {'width': 10, 'height': 6})
    plt.figure(figsize=(fig_size['width'], fig_size['height']))
    
    # 히스토그램 생성
    bins = image_params.get('bins', 10)
    color = image_params.get('bar_color', 'blue')
    edge_color = image_params.get('edge_color', 'black')
    alpha = common_params.get('alpha', 0.7)
    
    if is_numeric:
        plt.hist(df[feature_name], 
                 bins=bins, 
                 color=color, 
                 edgecolor=edge_color,
                 alpha=alpha)
    else:
        # 문자열 데이터의 경우 카테고리별 빈도
        value_counts = df[feature_name].value_counts()
        plt.bar(range(len(value_counts)), value_counts.values, 
                color=color, edgecolor=edge_color, alpha=alpha)
        plt.xticks(range(len(value_counts)), value_counts.index, rotation=45)
    
    # 축 레이블 설정
    xlabel = common_params.get('xlabel', feature_name)
    ylabel = common_params.get('ylabel', 'Frequency')
    plt.xlabel(xlabel, fontsize=image_params.get('xlabel_fontsize', 12))
    plt.ylabel(ylabel, fontsize=image_params.get('ylabel_fontsize', 12))
    
    # 제목 설정
    default_title = f'Histogram of {feature_name}'
    title = common_params.get('title', default_title)
    plt.title(title, fontsize=image_params.get('title_fontsize', 14), fontweight='bold')
    
    # 그리드 설정
    if image_params.get('show_grid', True):
        plt.grid(True, alpha=0.3, linestyle='--')
    
    # 통계 정보 표시 (숫자형 데이터만)
    if common_params.get('show_stats', False) and is_numeric:
        try:
            mean_val = df[feature_name].mean()
            median_val = df[feature_name].median()
            plt.axvline(mean_val, color='red', linestyle='--', alpha=0.8, label=f'Mean: {mean_val:.2f}')
            plt.axvline(median_val, color='green', linestyle='--', alpha=0.8, label=f'Median: {median_val:.2f}')
            plt.legend()
        except Exception as e:
            warnings.warn(f"통계 정보 표시 중 오류 발생: {e}")
    
    # 레이아웃 조정
    plt.tight_layout()
    
    # 이미지 저장
    dpi = image_params.get('dpi', 300)
    plt.savefig(image_file_name, dpi=dpi, bbox_inches='tight')
    plt.close()

def create_interactive_histogram(
    df: pd.DataFrame,
    feature_name: str,
    html_file_name: str,
    design_params: Dict[str, Any]
) -> None:
    """
    plotly를 사용하여 인터랙티브 히스토그램을 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 데이터프레임
    - feature_name (str): 히스토그램을 생성할 컬럼명
    - html_file_name (str): 저장할 HTML 파일명
    - design_params (Dict[str, Any]): 디자인 파라미터 (common, interactive 키 포함)
    """
    # 파라미터 추출
    common_params = design_params.get('common', {})
    interactive_params = design_params.get('interactive', {})
    
    # 데이터 타입 확인
    is_numeric = is_numeric_column(df[feature_name])
    if not is_numeric:
        warnings.warn(f"컬럼 '{feature_name}'은 숫자형이 아닙니다. 카테고리별 빈도 히스토그램을 생성합니다.")
    
    # plotly express로 히스토그램 생성
    default_title = f'Histogram of {feature_name}'
    
    if is_numeric:
        fig = px.histogram(df, 
                           x=feature_name,
                           nbins=interactive_params.get('bins', 10),
                           title=common_params.get('title', default_title))
    else:
        # 문자열 데이터의 경우 카테고리별 빈도
        value_counts = df[feature_name].value_counts()
        fig = px.bar(x=value_counts.index, 
                     y=value_counts.values,
                     title=common_params.get('title', default_title))
    
    # 레이아웃 업데이트
    fig.update_layout(
        title_font_size=interactive_params.get('title_fontsize', 18),
        title_x=0.5,  # 제목 중앙 정렬
        xaxis_title=common_params.get('xlabel', feature_name),
        yaxis_title=common_params.get('ylabel', 'Frequency'),
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
    
    # 히스토그램 스타일 설정
    fig.update_traces(
        marker_color=interactive_params.get('bar_color', 'blue'),
        marker_line_color=interactive_params.get('edge_color', 'black'),
        marker_line_width=interactive_params.get('edge_width', 1),
        opacity=common_params.get('alpha', 0.7)
    )
    
    # 통계 정보 표시 (숫자형 데이터만)
    if common_params.get('show_stats', False) and is_numeric:
        try:
            mean_val = df[feature_name].mean()
            median_val = df[feature_name].median()
            
            # 평균선 추가
            fig.add_vline(x=mean_val, line_dash="dash", line_color="red", 
                         annotation_text=f"Mean: {mean_val:.2f}")
            # 중앙값선 추가
            fig.add_vline(x=median_val, line_dash="dash", line_color="green", 
                         annotation_text=f"Median: {median_val:.2f}")
        except Exception as e:
            warnings.warn(f"통계 정보 표시 중 오류 발생: {e}")
    
    # 호버 템플릿 설정
    hover_template = interactive_params.get('hover_template', 
                                     f'<b>{feature_name}</b><br>Count: %{{y}}<br><extra></extra>')
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
    히스토그램 생성 작업 보고서를 생성하는 함수.
    
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
    # 빈 개수 추출
    bins = design_params.get('image', {}).get('bins', 10) if chart_type == 'image' else design_params.get('interactive', {}).get('bins', 10)
    
    # 제목 기본값 미리 계산
    default_title = f'Histogram of {feature_name}'
    
    # 디자인 파라미터에서 값들을 미리 추출
    common_params = design_params.get('common', {})
    title = common_params.get('title', default_title)
    xlabel = common_params.get('xlabel', feature_name)
    ylabel = common_params.get('ylabel', 'Frequency')
    alpha = common_params.get('alpha', 0.7)
    show_stats = common_params.get('show_stats', False)
    
    # 최빈값 계산
    mode_value = df[feature_name].mode().iloc[0] if not df[feature_name].mode().empty else 'N/A'
    
    # 모든 값들을 미리 계산하여 안전하게 처리
    row_count = len(df)
    col_count = len(df.columns)
    col_list = ', '.join(df.columns)
    execution_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    processing_speed = row_count / elapsed_time if elapsed_time > 0 else 0
    memory_usage = df.memory_usage(deep=True).sum() / 1024 / 1024
    
    # 데이터 타입 확인 및 안전한 통계값 계산
    is_numeric = is_numeric_column(df[feature_name])
    
    if is_numeric:
        try:
            min_val = df[feature_name].min()
            max_val = df[feature_name].max()
            mean_val = df[feature_name].mean()
            median_val = df[feature_name].median()
            std_val = df[feature_name].std()
            stats_available = True
        except Exception as e:
            warnings.warn(f"숫자형 통계 계산 중 오류 발생: {e}")
            min_val = max_val = mean_val = median_val = std_val = "N/A"
            stats_available = False
    else:
        # 문자열 데이터의 경우
        min_val = df[feature_name].min()
        max_val = df[feature_name].max()
        mean_val = median_val = std_val = "N/A (문자열 데이터)"
        stats_available = False
    
    report = f"""# 히스토그램 생성 작업 보고서

## 1. 작업 개요
- **작업 유형**: {chart_type.title()} 히스토그램 생성
- **실행 시간**: {execution_time}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **행 수**: {row_count:,}행
- **컬럼 수**: {col_count}개
- **컬럼 목록**: {col_list}

## 3. 시각화 설정
- **대상 컬럼**: {feature_name}
- **차트 타입**: {chart_type}
- **출력 파일**: {output_file_name}

## 4. 디자인 파라미터
- **제목**: {title}
- **X축 레이블**: {xlabel}
- **Y축 레이블**: {ylabel}
- **빈 개수**: {bins}개
- **투명도**: {alpha}
- **통계 표시**: {show_stats}

## 5. 처리 결과
- **데이터 타입**: {"숫자형" if is_numeric else "문자열형"}
- **데이터 범위**: {min_val if not stats_available else f"{min_val:.2f}"} ~ {max_val if not stats_available else f"{max_val:.2f}"}
- **평균값**: {mean_val if not stats_available else f"{mean_val:.2f}"}
- **중앙값**: {median_val if not stats_available else f"{median_val:.2f}"}
- **표준편차**: {std_val if not stats_available else f"{std_val:.2f}"}
- **최빈값**: {mode_value}

## 6. 성능 지표
- **처리 속도**: {processing_speed:.2f} 행/초
- **메모리 사용량**: {memory_usage:.2f} MB

## 7. 작업 상태
- **상태**: 성공
- **처리 결과**: {chart_type.title()} 히스토그램이 성공적으로 생성됨
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
    CSV 파일에서 특정 feature의 히스토그램을 생성하는 함수.
    chart_mode에 따라 이미지 또는 인터랙티브 차트를 생성합니다.

    Parameters:
    - data: CSV 파일 경로 또는 StringIO 객체
    - feature_name: 히스토그램을 생성할 feature의 컬럼명
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
        create_image_histogram(dataFile, feature_name, actual_output_file, design_params)
        chart_type = 'image'
    elif chart_mode == 'interactive':
        # 인터랙티브 차트 생성 (HTML 확장자 추가)
        actual_output_file = output_file_name if output_file_name.endswith('.html') else f"{output_file_name}.html"
        create_interactive_histogram(dataFile, feature_name, actual_output_file, design_params)
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
