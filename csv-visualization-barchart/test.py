from core import algorithm_csv_visualization_barchart as algorithm
from io import StringIO

if __name__ == '__main__' :
    with open('./tmp/test_input_data.csv', 'r', encoding='utf-8') as f:
        input_data = StringIO(f.read())
        
    algorithm.solution(
        data=input_data,
        feature_names='quantity',
        image_file_name='./tmp/test_output_data.png', 
        bins=9, 
        # color='green', 
        # xlabel='Feature Values', 
        # ylabel='Count'
    )