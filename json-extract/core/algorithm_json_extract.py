import json
import time
from datetime import datetime
from io import StringIO

def generate_report(
    input_data: dict,
    extract_path: str,
    extracted_data,
    input_filename: str,
    output_filename: str,
    elapsed_time: float
) -> str:
    """
    JSON 추출 작업 보고서를 생성하는 함수.
    """
    
    # 추출된 데이터 타입 확인
    extracted_type = type(extracted_data).__name__
    
    # 추출된 데이터 크기 계산
    if isinstance(extracted_data, (dict, list)):
        extracted_size = len(str(extracted_data))
    else:
        extracted_size = len(str(extracted_data))
    
    report = f"""# JSON 추출 작업 보고서

## 1. 작업 개요
- **작업 유형**: JSON 데이터 추출
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **입력 파일**: {input_filename}
- **입력 데이터 크기**: {len(str(input_data)):,} 문자
- **입력 데이터 타입**: {type(input_data).__name__}

## 3. 추출 설정
- **추출 경로**: `{extract_path}`

## 4. 처리 결과
- **출력 파일**: {output_filename}
- **추출된 데이터 타입**: {extracted_type}
- **추출된 데이터 크기**: {extracted_size:,} 문자
- **추출 성공**: {'예' if extracted_data is not None else '아니오'}

## 5. 성능 지표
- **처리 속도**: {len(str(input_data)) / elapsed_time:.2f} 문자/초

## 6. 작업 상태
- **상태**: 완료
- **추출된 데이터 미리보기**: {str(extracted_data)[:200]}{'...' if len(str(extracted_data)) > 200 else ''}
"""
    return report

def extract_value_by_path(data: dict, path: str):
    """
    점 표기법을 사용하여 JSON 데이터에서 값을 추출하는 함수.
    """
    try:
        keys = path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    except (KeyError, TypeError, AttributeError):
        return None

def solution(input_data: StringIO, extract_path: str, output_json_path: str) -> tuple:
    """
    JSON 데이터에서 특정 경로의 값을 추출하는 함수.
    """
    start_time = time.time()
    
    try:
        # JSON 데이터 로드
        input_data.seek(0)  # StringIO 포인터를 처음으로 이동
        json_data = json.load(input_data)
        
        # 경로로 값 추출
        extracted_data = extract_value_by_path(json_data, extract_path)
        
        if extracted_data is None:
            raise ValueError(f"Failed to extract data from path: {extract_path}")
        
        # 결과를 JSON 파일로 저장
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=2)
        
        print(f"Data extracted from path '{extract_path}' and saved to {output_json_path}")
        print(f"Extracted data: {extracted_data}")
        
        # 소요 시간 계산
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # 보고서 생성
        report = generate_report(
            input_data=json_data,
            extract_path=extract_path,
            extracted_data=extracted_data,
            input_filename=input_data.name if hasattr(input_data, 'name') else 'input_data',
            output_filename=output_json_path,
            elapsed_time=elapsed_time
        )
        
        return output_json_path, report
        
    except (json.JSONDecodeError, ValueError, KeyError, TypeError) as e:
        print(f"Failed to process JSON data: {e}")
        raise
