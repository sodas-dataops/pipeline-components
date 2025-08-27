from core import algorithm_csv_merge as algorithm
from io import StringIO

if __name__ == '__main__' :
    with open('./tmp/test_input_data.csv', 'r', encoding='utf-8') as f:
        input_data = StringIO(f.read())
        
    algorithm.solution(
        input_data=input_data, 
        output_csv_path='./tmp/test_output_data.csv', 
    )