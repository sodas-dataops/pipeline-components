import algorithm

if __name__ == '__main__' :
    algorithm.solution(
                        './tmp/test_input_data.csv', 
                        'quantity',
                        './tmp/test_output_data.png', 
                        colors=['#ff9999','#66b3ff','#99ff99','#ffcc99'],
                        explode=[0, 0.1, 0, 0],
                        autopct='%1.2f%%',
                        shadow=True)