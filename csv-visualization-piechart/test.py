import algorithm
from io import StringIO

if __name__ == '__main__' :
    with open('./tmp/test_input_data.csv', 'r', encoding='utf-8') as f:
        input_data = StringIO(f.read())

    algorithm.solution(
        input_data=input_data, 
        'quantity',
        './tmp/test_output_data.png', 
        colors=['#ff9999','#66b3ff','#99ff99','#ffcc99'],
        explode=[0, 0.1, 0, 0],
        autopct='%1.2f%%',
        shadow=True
    )