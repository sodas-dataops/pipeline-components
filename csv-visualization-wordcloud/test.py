from core import algorithm_csv_visualization_wordcloud as algorithm
from io import StringIO

if __name__ == '__main__' :
    with open('./tmp/test_input_data.csv', 'r', encoding='utf-8') as f:
        input_data = StringIO(f.read())
        
    algorithm.solution(
        data=input_data,
        word_column='tokenized_text',
        count_column='count',
        image_file_name='./tmp/test_output_data.png',
        max_words=150,
        background_color='black',
        colormap='plasma'   
    )