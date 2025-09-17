from core import algorithm_csv_explode as algorithm
from io import StringIO

if __name__ == '__main__':
    print("=== CSV Explode 테스트 시작 ===")
    
    with open('./tmp/test_input_data.csv', 'r', encoding='utf-8') as f:
        input_data = StringIO(f.read())
    
    print("\n1. List 타입 테스트 (관심사들 컬럼)")
    algorithm.solution(
        input_data=input_data, 
        target_column='관심사들',
        column_type='list',
        output_column='관심사',
        output_csv_path='./tmp/test_output_list.csv', 
    )
    
    print("\n2. Delimited 타입 테스트 (취미 컬럼)")
    with open('./tmp/test_input_data.csv', 'r', encoding='utf-8') as f:
        input_data = StringIO(f.read())
    algorithm.solution(
        input_data=input_data, 
        target_column='취미',
        column_type='delimited',
        output_column='취미_분해',
        output_csv_path='./tmp/test_output_delimited.csv', 
    )
    
    print("\n3. JSON 타입 테스트 (정보 컬럼)")
    with open('./tmp/test_input_data.csv', 'r', encoding='utf-8') as f:
        input_data = StringIO(f.read())
    algorithm.solution(
        input_data=input_data, 
        target_column='정보',
        column_type='json',
        output_column='정보_분해',
        output_csv_path='./tmp/test_output_json.csv', 
    )
    
    print("\n=== 모든 테스트 완료 ===")