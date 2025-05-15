import algorithm

if __name__ == '__main__' :
    algorithm.solution(
                        input_data='./tmp/test_input_data.csv', 
                        target_column='근무조건_급여_금액',
                        transform_function_str="lambda x: int(x.replace(',', '').replace('만원', '0000').replace('원', '')) if pd.notna(x) and x != '' and x != 'nan' else None", 
                        output_column='근무조건_급여_금액',
                        output_csv_path='./tmp/test_output_data.csv', 
                        )