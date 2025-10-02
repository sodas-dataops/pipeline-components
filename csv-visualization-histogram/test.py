import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core import algorithm_csv_visualization_histogram as algorithm
from io import StringIO

if __name__ == '__main__' :
    # 테스트 데이터 생성
    test_data = """quantity
10
15
20
25
30
35
40
45
50
55
60
65
70
75
80
85
90
95
100
105
110
115
120
125
130
135
140
145
150
155
160
165
170
175
180
185
190
195
200
205
210
215
220
225
230
235
240
245
250"""
    
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
            'title': 'Test Image Histogram',
            'xlabel': 'Quantity',
            'ylabel': 'Frequency',
            'alpha': 0.8,
            'show_stats': True
        },
        'image': {
            'bins': 15,
            'bar_color': 'green',
            'show_grid': True,
            'title_fontsize': 18
        }
    }
    
    algorithm.solution(
        data=input_data_image,
        feature_name='quantity',
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
            'title': 'Test Interactive Histogram',
            'xlabel': 'Quantity',
            'ylabel': 'Frequency',
            'alpha': 0.8,
            'show_stats': True
        },
        'interactive': {
            'bins': 20,
            'bar_color': 'red',
            'width': 1200,
            'height': 700,
            'title_fontsize': 20
        }
    }
    
    algorithm.solution(
        data=input_data_interactive,
        feature_name='quantity',
        output_file_name='./tmp/test_output_interactive.html',
        chart_mode='interactive',
        design_params=design_params_interactive
    )
    
    print("테스트 완료!")