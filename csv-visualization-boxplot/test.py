import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core import algorithm_csv_visualization_boxplot as algorithm
from io import StringIO

if __name__ == '__main__' :
    # 테스트 데이터 생성
    test_data = """category,value
A,10
A,12
A,15
A,8
A,20
B,25
B,30
B,22
B,28
B,35
C,5
C,8
C,12
C,6
C,10
D,40
D,45
D,38
D,42
D,50"""
    
    # tmp 디렉토리 생성
    os.makedirs('./tmp', exist_ok=True)
    
    # 테스트 데이터를 파일로 저장
    with open('./tmp/test_input_data.csv', 'w', encoding='utf-8') as f:
        f.write(test_data)
    
    # 이미지 차트 테스트
    print("이미지 차트 생성 중...")
    with open('./tmp/test_input_data.csv', 'r', encoding='utf-8') as f:
        input_data_image = StringIO(f.read())
    
    design_params_image = {
        'common': {
            'title': 'Test Image Box Plot',
            'xlabel': 'Category',
            'ylabel': 'Value',
            'alpha': 0.8
        },
        'image': {
            'box_color': 'green',
            'show_grid': True,
            'title_fontsize': 18
        }
    }
    
    algorithm.solution(
        data=input_data_image,
        group_by_column='category',
        value_column='value',
        output_file_name='./tmp/test_output_image.png',
        chart_mode='image',
        design_params=design_params_image
    )
    
    # 인터랙티브 차트 테스트
    print("인터랙티브 차트 생성 중...")
    with open('./tmp/test_input_data.csv', 'r', encoding='utf-8') as f:
        input_data_interactive = StringIO(f.read())
    
    design_params_interactive = {
        'common': {
            'title': 'Test Interactive Box Plot',
            'xlabel': 'Category',
            'ylabel': 'Value',
            'alpha': 0.8
        },
        'interactive': {
            'color_by_group': True,
            'width': 1200,
            'height': 700,
            'title_fontsize': 20
        }
    }
    
    algorithm.solution(
        data=input_data_interactive,
        group_by_column='category',
        value_column='value',
        output_file_name='./tmp/test_output_interactive.html',
        chart_mode='interactive',
        design_params=design_params_interactive
    )
    
    print("테스트 완료!")