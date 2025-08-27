from core import algorithm_csv_arithmetic_operation as algorithm
from io import StringIO

if __name__ == '__main__' :
    with open('./tmp/test_input_data.csv', 'r', encoding='utf-8') as f:
        input_data = StringIO(f.read())
        
    algorithm.solution(
        data=input_data, 
        output_filename='./tmp/test_output_data.csv', 
        operands=['price', 'quantity'],
        operators=['*'],
        column_name='revenue'
    )