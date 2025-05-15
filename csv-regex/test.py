import algorithm
import time
if __name__ == '__main__' :
    algorithm.solution(
                        input_data='./tmp/test_input_data.csv', 
                        target_column='근무조건_급여', 
                        regex_pattern='^(연봉제|월급제|시급제)', 
                        output_column='근무조건_급여_유형',
                        output_csv_path='./tmp/test_output_data.csv', 
                        )