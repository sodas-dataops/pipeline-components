import algorithm

if __name__ == '__main__' :
    algorithm.solution(
                        './tmp/test_input_data.csv', 
                        'tokenized_text',
                        './tmp/test_output_data.png',
                        max_words=150,
                        background_color='black',
                        colormap='plasma'
                        )