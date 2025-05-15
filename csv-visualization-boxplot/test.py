import algorithm

if __name__ == '__main__' :
    algorithm.solution(
                        './tmp/test_input_data.csv', 
                        'quantity',
                        'price',
                        './tmp/test_output_data.png', 
                        title='Distribution of Feature Column', 
                        ylabel='Values'
                        )