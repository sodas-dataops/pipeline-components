import algorithm
import time

if __name__ == '__main__' :
    start_time = time.time()
    algorithm.solution(
                        './tmp/test_input_data.csv', 
                        '상세내용',
                        './tmp/test_output_data.csv', 
                        remove_stopwords=True, 
                        ignore_words=[],
                        keep_tokenized_column_only=True
                        )
    end_time = time.time()
    print(f"실행 시간: {end_time - start_time} 초")