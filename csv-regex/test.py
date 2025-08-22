from . import algorithm
import time
from io import StringIO

if __name__ == '__main__':
    # 파일을 읽어서 StringIO 객체로 변환
    with open('./tmp/test_input_data.csv', 'r', encoding='utf-8') as f:
        input_data = StringIO(f.read())
    
    algorithm.solution(
        input_data=input_data,
        target_column='근무조건_급여',
        regex_pattern='^(연봉제|월급제|시급제)',
        output_column='근무조건_급여_유형',
        output_csv_path='./tmp/test_output_data.csv',
    )