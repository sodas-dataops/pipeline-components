import pandas as pd
import numpy as np
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

def create_image_linechart(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    color_column: Optional[str],
    image_file_name: str,
    design_params: Dict[str, Any]
) -> None:
    """
    matplotlib을 사용하여 이미지 라인차트를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 데이터프레임
    - x_column (str): X축 컬럼명
    - y_column (str): Y축 컬럼명
    - color_column (Optional[str]): 색상 구분 컬럼명
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
    
    # 파라미터 setups
    fig_size = image_params.get('figure_size', {'width': 12, 'height': 8})
    line_width = image_params.get('line_width', 2)
    line_style = image_params.get('line_style', '-')
    marker_style = image_params.get('marker_style', 'o')
    marker_size = image_params.get('marker_size', 4)
    
    # 데이터 정렬 (x축 기준)
    df_sorted = df.sort_values(x_column)
    
    # 라인 차트 생성
    plt.figure(figsize=(fig_size['width'], fig_size['height']))
    
    if color_column and color_column in df_sorted.columns:
        # 색상으로 구분된 라인 차트
        unique_colors = df_sorted[color_column].unique()
        colors = plt.cm.Set3(np.linspace(0, 1, len(unique_colors)))
        
        for i, color_val in enumerate(unique_colors):
            mask = df_sorted[color_column] == color_val
            df_color = df_sorted[mask].sort_values(x_column)
            plt.plot(
                df_color[x_column], 
                df_color[y_column],
                color=colors[i],
                linewidth=line_width,
                linestyle=line_style,
                marker=marker_style,
                markersize=marker_size,
                label=str(color_val),
                alpha=0.8
            )
        plt.legend()
    else:
        # 기본 라인 차트
        plt.plot(
            df_sorted[x_column], 
            df_sorted[y_column],
            linewidth=line_width,
            linestyle=line_style,
            marker=marker_style,
            markersize=marker_size,
            alpha=0.8
        )
    
    # 차트 제목 및 라벨 설정
    title = common_params.get('title', 'Line Chart')
    title_fontsize = image_params.get('title_fontsize', 16)
    plt.title(title, fontsize=title_fontsize)
    
    xlabel = common_params.get('xlabel', x_column)
    ylabel = common_params.get('ylabel', y_column)
    label_fontsize = image_params.get('label_fontsize', 12)
    plt.xlabel(xlabel, fontsize=label_fontsize)
    plt.ylabel(ylabel, fontsize=label_fontsize)
    
    # 그리드 표시
    if image_params.get('show_grid', True):
        plt.grid(True, alpha=0.3)
    
    # 레이아웃 자동 조정
    plt.tight_layout()
    
    # 이미지 저장
    dpi = image_params.get('dpi', 300)
    plt.savefig(image_file_name, dpi=dpi, bbox_inches="tight")
    plt.close()

def create_interactive_linechart(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    color_column: Optional[str],
    html_file_name: str,
    design_params: Dict[str, Any]
) -> None:
    """
    plotly를 사용하여 인터랙티브 라인차트를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 데이터프레임
    - x_column (str): X축 컬럼명
    - y_column (str): Y축 컬럼명
    - color_column (Optional[str]): 색상 구분 컬럼명
    - html_file_name (str): 저장할 HTML 파일명
    - design_params (Dict[str, Any]): 디자인 파라미터 (common, interactive 키 포함)
    """
    # 파라미터 추출
    common_params = design_params.get('common', {})
    interactive_params = design_params.get('interactive', {})
    
    # 데이터 정렬 (x축 기준)
    df_sorted = df.sort_values(x_column)
    
    # plotly 라인차트 생성
    if color_column and color_column in df_sorted.columns:
        fig = px.line(
            df_sorted, 
            x=x_column, 
            y=y_column, 
            color=color_column,
            title=common_params.get('title', 'Line Chart'),
            hover_data=df_sorted.columns.tolist()
        )
    else:
        fig = px.line(
            df_sorted, 
            x=x_column, 
            y=y_column,
            title=common_params.get('title', 'Line Chart'),
            hover_data=df_sorted.columns.tolist()
        )
    
    # 레이아웃 업데이트
    fig.update_layout(
        title_font_size=interactive_params.get('title_fontsize', 20),
        title_x=0.5,
        width=interactive_params.get('width', 1000),
        height=interactive_params.get('height', 600),
        xaxis_title=common_params.get('xlabel', x_column),
        yaxis_title=common_params.get('ylabel', y_column),
        font_family=interactive_params.get('font_family', 'Arial'),
        plot_bgcolor=interactive_params.get('plot_bgcolor', 'white'),
        paper_bgcolor=interactive_params.get('paper_bgcolor', 'white'),
        showlegend=interactive_params.get('show_legend', True)
    )
    
    # 라인 스타일 설정
    line_width = interactive_params.get('line_width', 2)
    marker_size = interactive_params.get('marker_size', 6)
    
    fig.update_traces(
        line=dict(
            width=line_width,
            shape=interactive_params.get('line_shape', 'linear')  # 'linear', 'spline', 'hv', 'vh', 'hvh', 'vhv'
        ),
        marker=dict(
            size=marker_size,
            opacity=interactive_params.get('opacity', 0.8),
            line=dict(
                width=interactive_params.get('marker_line_width', 1),
                color=interactive_params.get('marker_line_color', 'white')
            )
        ),
        mode=interactive_params.get('mode', 'lines+markers')  # 'lines', 'markers', 'lines+markers'
    )
    
    # HTML 파일로 저장
    plot(fig, filename=html_file_name, auto_open=False)

def generate_report(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    color_column: Optional[str],
    output_file_name: str,
    design_params: Dict[str, Any],
    elapsed_time: float,
    chart_type: str
) -> str:
    """
    라인차트 생성 작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - x_column (str): X축 컬럼명
    - y_column (str): Y축 컬럼명
    - color_column (Optional[str]): 색상 구분 컬럼명
    - output_file_name (str): 저장된 파일 경로
    - design_params (Dict[str, Any]): 사용된 디자인 파라미터
    - elapsed_time (float): 소요 시간 (초)
    - chart_type (str): 차트 타입 ('image' 또는 'interactive')
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    def safe_describe(series: pd.Series) -> Dict[str, Any]:
        """안전하게 시리즈의 통계를 계산하는 함수"""
        try:
            # 빈 시리즈 처리
            if len(series) == 0:
                return {
                    'error': '빈 데이터',
                    'type': 'empty'
                }
            
            # 숫자형 데이터인지 확인
            if pd.api.types.is_numeric_dtype(series):
                try:
                    stats = series.describe()
                    return {
                        'mean': stats.get('mean'),
                        'std': stats.get('std'),
                        'min': stats.get('min'),
                        'max': stats.get('max'),
                        'count': stats.get('count'),
                        'type': 'numeric'
                    }
                except Exception as e:
                    return {
                        'error': f"숫자형 통계 계산 실패: {str(e)}",
                        'type': 'numeric_error'
                    }
            # datetime 데이터인지 확인
            elif pd.api.types.is_datetime64_any_dtype(series):
                try:
                    min_val = series.min()
                    max_val = series.max()
                    count_val = len(series.dropna())
                    range_val = max_val - min_val if pd.notna(min_val) and pd.notna(max_val) else None
                    
                    return {
                        'min': min_val,
                        'max': max_val,
                        'count': count_val,
                        'type': 'datetime',
                        'range': range_val
                    }
                except Exception as e:
                    return {
                        'error': f"datetime 통계 계산 실패: {str(e)}",
                        'type': 'datetime_error'
                    }
            # 문자열이나 기타 데이터 타입
            else:
                try:
                    count_val = len(series.dropna())
                    unique_val = series.nunique()
                    mode_series = series.mode()
                    most_frequent = mode_series.iloc[0] if len(mode_series) > 0 else None
                    
                    return {
                        'count': count_val,
                        'unique': unique_val,
                        'type': 'categorical',
                        'most_frequent': most_frequent
                    }
                except Exception as e:
                    return {
                        'error': f"범주형 통계 계산 실패: {str(e)}",
                        'type': 'categorical_error'
                    }
        except Exception as e:
            return {
                'error': f"통계 계산 실패: {str(e)}",
                'type': 'unknown'
            }
    
    def safe_correlation(x_series: pd.Series, y_series: pd.Series) -> str:
        """안전하게 상관계수를 계산하는 함수"""
        try:
            # 두 컬럼 모두 숫자형인 경우에만 상관계수 계산
            if pd.api.types.is_numeric_dtype(x_series) and pd.api.types.is_numeric_dtype(y_series):
                correlation = x_series.corr(y_series)
                return f"{correlation:.3f}" if not pd.isna(correlation) else "N/A (상관관계 없음)"
            else:
                return "N/A (비숫자형 데이터)"
        except Exception as e:
            return f"N/A (계산 오류: {str(e)})"
    
    # 안전한 통계 계산
    x_stats = safe_describe(df[x_column])
    y_stats = safe_describe(df[y_column])
    
    # 시계열 데이터 통계 계산 (Y축이 숫자형인 경우에만)
    trend_analysis = ""
    correlation_info = ""
    
    try:
        if y_stats.get('type') == 'numeric':
            try:
                df_sorted = df.sort_values(x_column)
                y_change = df_sorted[y_column].diff().dropna()
                
                if len(y_change) > 0:
                    trend_up = (y_change > 0).sum()
                    trend_down = (y_change < 0).sum()
                    trend_stable = (y_change == 0).sum()
                    
                    y_change_mean = y_change.mean() if pd.notna(y_change.mean()) else 0
                    y_change_std = y_change.std() if pd.notna(y_change.std()) else 0
                    
                    trend_analysis = f"""
### 시계열 특성
- **증가 추세**: {trend_up}개 포인트
- **감소 추세**: {trend_down}개 포인트
- **변화 없음**: {trend_stable}개 포인트
- **변화율 평균**: {y_change_mean:.3f}
- **변화율 표준편차**: {y_change_std:.3f}"""
                else:
                    trend_analysis = f"""
### 시계열 특성
- **분석 불가**: 변화율 데이터가 없음"""
                
                # 상관계수 계산
                correlation = safe_correlation(df[x_column], df[y_column])
                correlation_info = f"- **상관계수**: {correlation}"
            except Exception as e:
                trend_analysis = f"""
### 시계열 특성
- **분석 오류**: {str(e)}"""
        else:
            trend_analysis = f"""
### 시계열 특성
- **분석 불가**: Y축 데이터가 숫자형이 아님 ({y_stats.get('type', 'unknown')} 타입)"""
    except Exception as e:
        trend_analysis = f"""
### 시계열 특성
- **분석 오류**: {str(e)}"""
    
    def safe_format_number(value: Any, default: str = "N/A") -> str:
        """안전하게 숫자를 포맷팅하는 함수"""
        try:
            if value is None or pd.isna(value):
                return default
            if isinstance(value, (int, float)):
                return f"{value:.2f}"
            else:
                return str(value)
        except Exception:
            return default
    
    def safe_format_count(value: Any, default: str = "N/A") -> str:
        """안전하게 개수를 포맷팅하는 함수"""
        try:
            if value is None or pd.isna(value):
                return default
            if isinstance(value, (int, float)):
                return f"{int(value):,}개"
            else:
                return str(value)
        except Exception:
            return default
    
    # X축 통계 정보 생성
    def format_x_stats(stats: Dict[str, Any]) -> str:
        try:
            if stats.get('type') == 'numeric':
                return f"""### X축 ({x_column}) - 숫자형
- **평균**: {safe_format_number(stats.get('mean'))}
- **표준편차**: {safe_format_number(stats.get('std'))}
- **최솟값**: {safe_format_number(stats.get('min'))}
- **최댓값**: {safe_format_number(stats.get('max'))}
- **데이터 개수**: {safe_format_count(stats.get('count'))}"""
            elif stats.get('type') == 'datetime':
                return f"""### X축 ({x_column}) - 날짜/시간형
- **시작 시간**: {stats.get('min', 'N/A')}
- **종료 시간**: {stats.get('max', 'N/A')}
- **시간 범위**: {stats.get('range', 'N/A')}
- **데이터 개수**: {safe_format_count(stats.get('count'))}"""
            elif stats.get('type') == 'categorical':
                return f"""### X축 ({x_column}) - 범주형
- **데이터 개수**: {safe_format_count(stats.get('count'))}
- **고유값 개수**: {safe_format_count(stats.get('unique'))}
- **가장 빈번한 값**: {stats.get('most_frequent', 'N/A')}"""
            else:
                return f"""### X축 ({x_column}) - 알 수 없는 타입
- **오류**: {stats.get('error', '통계 계산 실패')}"""
        except Exception as e:
            return f"""### X축 ({x_column}) - 포맷팅 오류
- **오류**: {str(e)}"""
    
    # Y축 통계 정보 생성
    def format_y_stats(stats: Dict[str, Any]) -> str:
        try:
            if stats.get('type') == 'numeric':
                return f"""### Y축 ({y_column}) - 숫자형
- **평균**: {safe_format_number(stats.get('mean'))}
- **표준편차**: {safe_format_number(stats.get('std'))}
- **최솟값**: {safe_format_number(stats.get('min'))}
- **최댓값**: {safe_format_number(stats.get('max'))}
- **데이터 개수**: {safe_format_count(stats.get('count'))}"""
            elif stats.get('type') == 'datetime':
                return f"""### Y축 ({y_column}) - 날짜/시간형
- **시작 시간**: {stats.get('min', 'N/A')}
- **종료 시간**: {stats.get('max', 'N/A')}
- **시간 범위**: {stats.get('range', 'N/A')}
- **데이터 개수**: {safe_format_count(stats.get('count'))}"""
            elif stats.get('type') == 'categorical':
                return f"""### Y축 ({y_column}) - 범주형
- **데이터 개수**: {safe_format_count(stats.get('count'))}
- **고유값 개수**: {safe_format_count(stats.get('unique'))}
- **가장 빈번한 값**: {stats.get('most_frequent', 'N/A')}"""
            else:
                return f"""### Y축 ({y_column}) - 알 수 없는 타입
- **오류**: {stats.get('error', '통계 계산 실패')}"""
        except Exception as e:
            return f"""### Y축 ({y_column}) - 포맷팅 오류
- **오류**: {str(e)}"""
    
    color_info = ""
    if color_column and color_column in df.columns:
        unique_colors = df[color_column].nunique()
        color_info = f"- **색상 구분**: {color_column} ({unique_colors}개 카테고리)"
    
    try:
        # 안전한 성능 지표 계산
        try:
            processing_speed = len(df) / elapsed_time if elapsed_time > 0 else 0
            memory_usage = df.memory_usage(deep=True).sum() / 1024 / 1024
        except Exception:
            processing_speed = 0
            memory_usage = 0
        
        report = f"""# 라인차트 생성 작업 보고서

## 1. 작업 개요
- **작업 유형**: {chart_type.title()} 라인차트 생성
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **행 수**: {len(df):,}행
- **컬럼 수**: {len(df.columns)}개
- **컬럼 목록**: {', '.join(df.columns)}

## 3. 시각화 설정
- **X축 컬럼**: {x_column}
- **Y축 컬럼**: {y_column}
{color_info}
- **차트 타입**: {chart_type}
- **출력 파일**: {output_file_name}

## 4. 디자인 파라미터
- **제목**: {design_params.get('common', {}).get('title', 'Line Chart')}
- **X축 라벨**: {design_params.get('common', {}).get('xlabel', x_column)}
- **Y축 라벨**: {design_params.get('common', {}).get('ylabel', y_column)}

## 5. 데이터 통계
{format_x_stats(x_stats)}

{format_y_stats(y_stats)}

{trend_analysis}
{correlation_info}

## 6. 성능 지표
- **처리 속도**: {processing_speed:.2f} 행/초
- **메모리 사용량**: {memory_usage:.2f} MB

## 7. 작업 상태
- **상태**: 성공
- **처리 결과**: {chart_type.title()} 라인차트가 성공적으로 생성됨
"""
        return report
    except Exception as e:
        # 최종 안전망: 보고서 생성 실패 시 기본 보고서 반환
        return f"""# 라인차트 생성 작업 보고서

## 1. 작업 개요
- **작업 유형**: {chart_type.title()} 라인차트 생성
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **행 수**: {len(df):,}행
- **컬럼 수**: {len(df.columns)}개

## 3. 시각화 설정
- **X축 컬럼**: {x_column}
- **Y축 컬럼**: {y_column}
- **차트 타입**: {chart_type}
- **출력 파일**: {output_file_name}

## 4. 작업 상태
- **상태**: 성공 (보고서 생성 중 오류 발생)
- **처리 결과**: {chart_type.title()} 라인차트가 성공적으로 생성됨
- **보고서 오류**: {str(e)}
"""

def solution(
    data: object, 
    x_column: str, 
    y_column: str, 
    output_file_name: str, 
    chart_mode: str = 'image',
    color_column: Optional[str] = None,
    design_params: Optional[Dict[str, Any]] = None
) -> Tuple[str, str]:
    """
    CSV 파일에서 라인차트를 생성하는 함수.
    chart_mode에 따라 이미지 또는 인터랙티브 차트를 생성합니다.

    Parameters:
    - data: CSV 파일 경로 또는 StringIO 객체
    - x_column: X축에 사용할 컬럼명
    - y_column: Y축에 사용할 컬럼명
    - output_file_name: 저장할 파일 이름
    - chart_mode: 차트 모드 ('image' 또는 'interactive')
    - color_column: 색상 구분에 사용할 컬럼명 (선택사항)
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
    if color_column and color_column not in dataFile.columns:
        raise ValueError(f"색상 컬럼 '{color_column}'이 데이터에 존재하지 않습니다.")
    
    # 차트 모드에 따라 차트 생성 및 실제 파일 경로 결정
    if chart_mode == 'image':
        # 이미지 차트 생성 (기본적으로 PNG 확장자 추가)
        actual_output_file = output_file_name if output_file_name.endswith(('.png', '.jpg', '.jpeg', '.svg', '.pdf')) else f"{output_file_name}.png"
        create_image_linechart(dataFile, x_column, y_column, color_column, actual_output_file, design_params)
        chart_type = 'image'
    elif chart_mode == 'interactive':
        # 인터랙티브 차트 생성 (HTML 확장자 추가)
        actual_output_file = output_file_name if output_file_name.endswith('.html') else f"{output_file_name}.html"
        create_interactive_linechart(dataFile, x_column, y_column, color_column, actual_output_file, design_params)
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
        color_column=color_column,
        output_file_name=actual_output_file,
        design_params=design_params,
        elapsed_time=elapsed_time,
        chart_type=chart_type
    )
    
    return actual_output_file, report