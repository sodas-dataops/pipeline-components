import json
import os
from algorithm import solution

def test_json_upload():
    # 테스트용 JSON 데이터
    test_data = {
        "name": "Test Data",
        "value": 123,
        "items": ["item1", "item2", "item3"]
    }
    json_str = json.dumps(test_data)
    
    # 임시 파일 경로
    output_file = "./tmp/test_output.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 테스트 실행
    try:
        result = solution(json_str, output_file)
        print(f"Test passed! Output file: {result}")
        
        # 결과 확인
        with open(output_file, 'r') as f:
            loaded_data = json.load(f)
            assert loaded_data == test_data
            print("Data verification passed!")
            
    except Exception as e:
        print(f"Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    test_json_upload() 