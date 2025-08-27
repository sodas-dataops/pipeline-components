from core import algorithm_csv_visualization_map as algorithm

if __name__ == '__main__' :
    algorithm.solution(
                        './tmp/test_input_data.csv', 
                        '기업정보.사업체명',
                        'latitude',
                        'longitude',
                        './tmp/test_output_data.html', 
                        )