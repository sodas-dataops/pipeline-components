import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.offline import plot
import time
import os
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List

def create_image_pairplot(
    df: pd.DataFrame,
    feature_names: List[str],
    target_name: str,
    image_file_name: str,
    design_params: Dict[str, Any]
) -> None:
    """
    matplotlib/seaborn을 사용하여 이미지 pairplot을 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 데이터프레임
    - feature_names (List[str]): pairplot에 사용할 feature 컬럼명들
    - target_name (str): 색상 구분에 사용할 target 컬럼명
    - image_file_name (str): 저장할 이미지 파일명
    - design_params (Dict[str, Any]): 디자인 파라미터 (common, image 키 포함)
    """
    # 파라미터 추출
    common_params = design_params.get('common', {})
    image_params = design_params.get('image', {})
    
    # matplotlib 스타일 설정
    plt.style.use(image_params.get('matplotlib_style', 'default'))
    
    # 데이터 준비
    plot_data = df[feature_names + [target_name]].copy()
    
    # seaborn pairplot 생성
    fig_size = image_params.get('figure_size', {'width': 12, 'height': 10})
    height = image_params.get('subplot_height', 3)
    
    # seaborn pairplot 생성
    g = sns.pairplot(
        plot_data, 
        hue=target_name,
        height=height,
        plot_kws={'alpha': common_params.get('alpha', 0.7)},
        diag_kws={'alpha': common_params.get('alpha', 0.7)}
    )
    
    # 제목 설정
    title = common_params.get('title', f'Pairplot of {", ".join(feature_names)}')
    g.fig.suptitle(title, fontsize=image_params.get('title_fontsize', 16), y=1.02)
    
    # 레이아웃 조정
    plt.tight_layout()
    
    # 이미지 저장
    dpi = image_params.get('dpi', 300)
    plt.savefig(image_file_name, dpi=dpi, bbox_inches='tight')
    plt.close()

def create_interactive_pairplot(
    df: pd.DataFrame,
    feature_names: List[str],
    target_name: str,
    html_file_name: str,
    design_params: Dict[str, Any]
) -> None:
    """
    plotly를 사용하여 인터랙티브 pairplot을 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 데이터프레임
    - feature_names (List[str]): pairplot에 사용할 feature 컬럼명들
    - target_name (str): 색상 구분에 사용할 target 컬럼명
    - html_file_name (str): 저장할 HTML 파일명
    - design_params (Dict[str, Any]): 디자인 파라미터 (common, interactive 키 포함)
    """
    # 파라미터 추출
    common_params = design_params.get('common', {})
    interactive_params = design_params.get('interactive', {})
    
    # 데이터 준비
    plot_data = df[feature_names + [target_name]].copy()
    
    # subplot 생성
    n_features = len(feature_names)
    fig = make_subplots(
        rows=n_features, 
        cols=n_features,
        subplot_titles=[f'{col1} vs {col2}' if col1 != col2 else f'{col1}' 
                       for col1 in feature_names for col2 in feature_names],
        shared_xaxes=False,
        shared_yaxes=False
    )
    
    # 각 subplot에 그래프 추가
    for i, col1 in enumerate(feature_names):
        for j, col2 in enumerate(feature_names):
            row, col = i + 1, j + 1
            
            if i == j:
                # 대각선: 히스토그램
                for target_val in plot_data[target_name].unique():
                    data_subset = plot_data[plot_data[target_name] == target_val]
                    fig.add_trace(
                        go.Histogram(
                            x=data_subset[col1],
                            name=f'{target_name}={target_val}',
                            opacity=common_params.get('alpha', 0.7),
                            showlegend=(i == 0 and j == 0)  # 첫 번째 subplot에서만 legend 표시
                        ),
                        row=row, col=col
                    )
            else:
                # 비대각선: 산점도
                for target_val in plot_data[target_name].unique():
                    data_subset = plot_data[plot_data[target_name] == target_val]
                    fig.add_trace(
                        go.Scatter(
                            x=data_subset[col1],
                            y=data_subset[col2],
                            mode='markers',
                            name=f'{target_name}={target_val}',
                            opacity=common_params.get('alpha', 0.7),
                            showlegend=(i == 0 and j == 1),  # 첫 번째 비대각선 subplot에서만 legend 표시
                            marker=dict(
                                size=interactive_params.get('marker_size', 6),
                                line=dict(
                                    width=interactive_params.get('marker_line_width', 0.5),
                                    color='white'
                                )
                            )
                        ),
                        row=row, col=col
                    )
    
    # 레이아웃 업데이트
    title = common_params.get('title', f'Interactive Pairplot of {", ".join(feature_names)}')
    fig.update_layout(
        title_text=title,
        title_font_size=interactive_params.get('title_fontsize', 18),
        title_x=0.5,
        width=interactive_params.get('width', 1200),
        height=interactive_params.get('height', 1000),
        font_family=interactive_params.get('font_family', 'Arial'),
        plot_bgcolor=interactive_params.get('plot_bgcolor', 'white'),
        paper_bgcolor=interactive_params.get('paper_bgcolor', 'white'),
        showlegend=interactive_params.get('show_legend', True)
    )
    
    # x축과 y축 레이블 설정
    for i, col in enumerate(feature_names):
        fig.update_xaxes(title_text=col, row=i+1, col=n_features)
        fig.update_yaxes(title_text=col, row=1, col=i+1)
    
    # 호버 템플릿 설정
    hover_template = interactive_params.get('hover_template', 
                                     '<b>%{x}</b><br>%{y}<br><extra></extra>')
    fig.update_traces(hovertemplate=hover_template)
    
    # HTML 파일로 저장
    plot(fig, filename=html_file_name, auto_open=False)

def generate_report(
    df: pd.DataFrame,
    feature_names: List[str],
    target_name: str,
    output_file_name: str,
    design_params: Dict[str, Any],
    elapsed_time: float,
    chart_type: str
) -> str:
    """
    pairplot 생성 작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - feature_names (List[str]): 사용된 feature 컬럼명들
    - target_name (str): 사용된 target 컬럼명
    - output_file_name (str): 저장된 파일 경로
    - design_params (Dict[str, Any]): 사용된 디자인 파라미터
    - elapsed_time (float): 소요 시간 (초)
    - chart_type (str): 차트 타입 ('image' 또는 'interactive')
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    report = f"""# Pairplot 생성 작업 보고서

## 1. 작업 개요
- **작업 유형**: {chart_type.title()} Pairplot 생성
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **행 수**: {len(df):,}행
- **컬럼 수**: {len(df.columns)}개
- **컬럼 목록**: {', '.join(df.columns)}

## 3. 시각화 설정
- **Feature 컬럼들**: {', '.join(feature_names)}
- **Target 컬럼**: {target_name}
- **차트 타입**: {chart_type}
- **출력 파일**: {output_file_name}

## 4. 디자인 파라미터
- **제목**: {design_params.get('common', {}).get('title', f'Pairplot of {", ".join(feature_names)}')}
- **투명도**: {design_params.get('common', {}).get('alpha', 0.7)}
- **Feature 개수**: {len(feature_names)}개

## 5. 데이터 통계
- **Target 값 분포**:
"""
    
    # Target 값 분포 추가
    target_counts = df[target_name].value_counts()
    for value, count in target_counts.items():
        report += f"  - {value}: {count}개 ({count/len(df)*100:.1f}%)\n"
    
    # Feature별 통계 추가
    report += f"""
## 6. Feature별 통계
"""
    for feature in feature_names:
        if df[feature].dtype in ['int64', 'float64']:
            report += f"- **{feature}**: 평균 {df[feature].mean():.2f}, 표준편차 {df[feature].std():.2f}\n"
        else:
            report += f"- **{feature}**: 범주형 데이터\n"
    
    report += f"""
## 7. 성능 지표
- **처리 속도**: {len(df) / elapsed_time:.2f} 행/초
- **메모리 사용량**: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB

## 8. 작업 상태
- **상태**: 성공
- **처리 결과**: {chart_type.title()} pairplot이 성공적으로 생성됨
"""
    return report

def solution(
    data: object, 
    feature_names: List[str], 
    target_name: str, 
    output_file_name: str, 
    chart_mode: str = 'image',
    design_params: Optional[Dict[str, Any]] = None
) -> Tuple[str, str]:
    """
    CSV 파일에서 feature들 간의 pairplot을 생성하는 함수.
    chart_mode에 따라 이미지 또는 인터랙티브 차트를 생성합니다.

    Parameters:
    - data: CSV 파일 경로 또는 StringIO 객체
    - feature_names: pairplot에 사용할 feature 컬럼명들
    - target_name: 색상 구분에 사용할 target 컬럼명
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
        create_image_pairplot(dataFile, feature_names, target_name, actual_output_file, design_params)
        chart_type = 'image'
    elif chart_mode == 'interactive':
        # 인터랙티브 차트 생성 (HTML 확장자 추가)
        actual_output_file = output_file_name if output_file_name.endswith('.html') else f"{output_file_name}.html"
        create_interactive_pairplot(dataFile, feature_names, target_name, actual_output_file, design_params)
        chart_type = 'interactive'
    else:
        raise ValueError(f"지원하지 않는 차트 모드입니다: {chart_mode}. 'image' 또는 'interactive'를 사용하세요.")
    
    # 소요 시간 계산
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 보고서 생성
    report = generate_report(
        df=dataFile,
        feature_names=feature_names,
        target_name=target_name,
        output_file_name=actual_output_file,
        design_params=design_params,
        elapsed_time=elapsed_time,
        chart_type=chart_type
    )
    
    return actual_output_file, report