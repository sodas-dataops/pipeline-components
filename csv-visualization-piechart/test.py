import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core import algorithm_csv_visualization_piechart as algorithm
from io import StringIO

if __name__ == '__main__' :
    # 테스트 데이터 생성
    test_data = """category,quantity
A,25
B,30
C,20
D,15
E,10
F,5
G,3
H,2"""
    
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
            'title': 'Test Image Pie Chart'
        },
        'image': {
            'colors': ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc', '#c2c2f0', '#ffb3e6', '#c4e17f'],
            'explode': [0, 0.1, 0, 0, 0, 0, 0, 0],
            'shadow': True,
            'text_fontsize': 20,
            'title_fontsize': 40
        }
    }
    
    algorithm.solution(
        data=input_data_image,
        feature_name='category',
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
            'title': 'Test Interactive Pie Chart'
        },
        'interactive': {
            'width': 1000,
            'height': 700,
            'text_position': 'outside',
            'text_info': 'label+percent+value',
            'text_fontsize': 14,
            'title_fontsize': 28
        }
    }
    
    algorithm.solution(
        data=input_data_interactive,
        feature_name='category',
        output_file_name='./tmp/test_output_interactive.html',
        chart_mode='interactive',
        design_params=design_params_interactive
    )
    
    print("테스트 완료!")