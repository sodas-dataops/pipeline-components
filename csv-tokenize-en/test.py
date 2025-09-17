from core import algorithm_csv_tokenize_en as algorithm
import time
from io import StringIO

if __name__ == '__main__' :
    with open('./tmp/test_input_data.csv', 'r', encoding='utf-8') as f:
        input_data = StringIO(f.read())
        
    start_time = time.time()
    algorithm.solution(
        data=input_data, 
        text_column='description',
        output_filename='./tmp/test_output_data.csv', 
        remove_stopwords=True, 
        ignore_words=[],
        keep_tokenized_column_only=True
    )
    end_time = time.time()
    print(f"Execution time: {end_time - start_time} seconds")