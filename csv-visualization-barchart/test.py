from core import algorithm_csv_visualization_barchart as algorithm
from io import StringIO

if __name__ == '__main__' :
    # 이미지 차트 테스트
    print("이미지 차트 생성 중...")
    with open('./tmp/test_input_data.csv', 'r', encoding='utf-8') as f:
        input_data_image = StringIO(f.read())
    
    design_params_image = {
        'common': {
            'title': 'Test Image Bar Chart',
            'xlabel': 'Category',
            'ylabel': 'Value',
            'show_values': True,
            'alpha': 0.8
        },
        'image': {
            'bar_color': 'green',
            'show_grid': True,
            'title_fontsize': 18
        }
    }
    
    algorithm.solution(
        data=input_data_image,
        x_column='category',
        y_column='value',
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
            'title': 'Test Interactive Bar Chart',
            'xlabel': 'Category',
            'ylabel': 'Value',
            'show_values': True
        },
        'interactive': {
            'color_palette': 'plasma',
            'color_by_value': True,
            'width': 1200,
            'height': 700,
            'title_fontsize': 20
        }
    }
    
    algorithm.solution(
        data=input_data_interactive,
        x_column='category',
        y_column='value',
        output_file_name='./tmp/test_output_interactive.html',
        chart_mode='interactive',
        design_params=design_params_interactive
    )
    
    print("테스트 완료!")