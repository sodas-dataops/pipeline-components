from core import algorithm_json_extract as algorithm
from io import StringIO
import json

if __name__ == '__main__':
    # 테스트 케이스 1: 중첩 객체 추출
    print("=== 테스트 케이스 1: 중첩 객체 추출 ===")
    test_data1 = {"a": {"b": "c"}}
    input_data1 = StringIO(json.dumps(test_data1))
    
    algorithm.solution(
        input_data=input_data1,
        extract_path="a",
        output_json_path='./tmp/test_output1.json'
    )
    
    # 테스트 케이스 2: 깊은 경로 값 추출
    print("\n=== 테스트 케이스 2: 깊은 경로 값 추출 ===")
    test_data2 = {"a": {"b": "c"}}
    input_data2 = StringIO(json.dumps(test_data2))
    
    algorithm.solution(
        input_data=input_data2,
        extract_path="a.b",
        output_json_path='./tmp/test_output2.json'
    )
    
    # 테스트 케이스 3: 배열 값 추출
    print("\n=== 테스트 케이스 3: 배열 값 추출 ===")
    test_data3 = {"a": {"b": ["c"]}}
    input_data3 = StringIO(json.dumps(test_data3))
    
    algorithm.solution(
        input_data=input_data3,
        extract_path="a.b",
        output_json_path='./tmp/test_output3.json'
    )
    
    print("\n모든 테스트가 완료되었습니다!")
