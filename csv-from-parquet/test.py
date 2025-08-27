from core import algorithm_csv_from_parquet as algorithm

if __name__ == '__main__' :
    algorithm.solution(
                        './tmp/test_input_data.parquet', 
                        './tmp/test_output_data.csv', 
                        )