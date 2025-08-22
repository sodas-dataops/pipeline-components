import algorithm

if __name__ == '__main__' :
    algorithm.solution(
        input_filename='./tmp/input_date.csv', 
        output_filename='./tmp/output_data.csv', 
        target_cols=['col1', 'col2'],
        optional_cols=['col3'],
        delimiter=' ',
        new_col_name='concatenated_col',
    )