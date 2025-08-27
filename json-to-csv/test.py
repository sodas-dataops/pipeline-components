from core import algorithm_json_to_csv as algorithm

if __name__ == '__main__' :
    algorithm.solution(
        input_filename='./tmp/test_input_data.json',
        output_filename='./tmp/test_output_data.csv'
    )