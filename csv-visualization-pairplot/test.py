import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core import algorithm_csv_visualization_pairplot as algorithm
from io import StringIO

if __name__ == '__main__' :
    # 테스트 데이터 생성 (Iris 데이터셋 샘플)
    test_data = """sepal_length,sepal_width,petal_length,petal_width,species
5.1,3.5,1.4,0.2,setosa
4.9,3.0,1.4,0.2,setosa
4.7,3.2,1.3,0.2,setosa
4.6,3.1,1.5,0.2,setosa
5.0,3.6,1.4,0.2,setosa
5.4,3.9,1.7,0.4,setosa
4.6,3.4,1.4,0.3,setosa
5.0,3.4,1.5,0.2,setosa
4.4,2.9,1.4,0.2,setosa
4.9,3.1,1.5,0.1,setosa
7.0,3.2,4.7,1.4,versicolor
6.4,3.2,4.5,1.5,versicolor
6.9,3.1,4.9,1.5,versicolor
5.5,2.3,4.0,1.3,versicolor
6.5,2.8,4.6,1.5,versicolor
5.7,2.8,4.5,1.3,versicolor
6.3,3.3,4.7,1.6,versicolor
4.9,2.4,3.3,1.0,versicolor
6.6,2.9,4.6,1.3,versicolor
5.2,2.7,3.9,1.4,versicolor
6.3,3.3,6.0,2.5,virginica
5.8,2.7,5.1,1.9,virginica
7.1,3.0,5.9,2.1,virginica
6.3,2.9,5.6,1.8,virginica
6.5,3.0,5.8,2.2,virginica
7.6,3.0,6.6,2.1,virginica
4.9,2.5,4.5,1.7,virginica
7.3,2.9,6.3,1.8,virginica
6.7,2.5,5.8,1.8,virginica
7.2,3.6,6.1,2.5,virginica"""
    
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
            'title': 'Test Image Pairplot',
            'alpha': 0.8
        },
        'image': {
            'subplot_height': 4,
            'title_fontsize': 18
        }
    }
    
    algorithm.solution(
        data=input_data_image,
        feature_names=['sepal_length', 'sepal_width', 'petal_length', 'petal_width'],
        target_name='species',
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
            'title': 'Test Interactive Pairplot',
            'alpha': 0.8
        },
        'interactive': {
            'marker_size': 8,
            'width': 1400,
            'height': 1200,
            'title_fontsize': 20
        }
    }
    
    algorithm.solution(
        data=input_data_interactive,
        feature_names=['sepal_length', 'sepal_width', 'petal_length', 'petal_width'],
        target_name='species',
        output_file_name='./tmp/test_output_interactive.html',
        chart_mode='interactive',
        design_params=design_params_interactive
    )
    
    print("테스트 완료!")
