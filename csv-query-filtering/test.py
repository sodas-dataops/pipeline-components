import os
import pandas as pd
from io import StringIO
from core import algorithm_csv_query_filtering as algorithm

def create_test_data():
    """테스트용 데이터 생성"""
    data = {
        'temperature': [25.5, 999.9, 30.2, 15.8, 999.9, 22.1, 28.7, 999.9],
        'wind_speed': [10.5, 15.2, 999.9, 8.3, 12.7, 999.9, 9.8, 11.4],
        'pressure': [1013.2, 9999.9, 1008.5, 1015.8, 9999.9, 1010.3, 1005.7, 9999.9],
        'humidity': [65, 70, 55, 80, 45, 75, 60, 85],
        'station': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    }
    return pd.DataFrame(data)

def test_basic_filtering():
    """기본 필터링 테스트"""
    print("=== 기본 필터링 테스트 ===")
    
    # 테스트 데이터 생성
    df = create_test_data()
    test_data = StringIO(df.to_csv(index=False))
    
    # 필터 설정: temperature != 999.9 AND wind_speed < 50
    settings = {
        'filters': [
            {
                'column': 'temperature',
                'operator': 'ne',
                'value': 999.9
            },
            {
                'column': 'wind_speed',
                'operator': 'lt',
                'value': 50
            }
        ],
        'logic': 'AND'
    }
    
    # 필터링 실행
    output_file, report = algorithm.solution(test_data, './tmp/test_basic_filtering.csv', settings)
    
    # 결과 확인
    result_df = pd.read_csv(output_file)
    print(f"원본 데이터: {len(df)}행")
    print(f"필터링 결과: {len(result_df)}행")
    print("필터링된 데이터:")
    print(result_df)
    print()

def test_complex_filtering():
    """복합 필터링 테스트"""
    print("=== 복합 필터링 테스트 ===")
    
    # 테스트 데이터 생성
    df = create_test_data()
    test_data = StringIO(df.to_csv(index=False))
    
    # 필터 설정: (temperature != 999.9 OR wind_speed != 999.9) AND pressure < 1015
    settings = {
        'filters': [
            {
                'column': 'temperature',
                'operator': 'ne',
                'value': 999.9
            },
            {
                'column': 'wind_speed',
                'operator': 'ne',
                'value': 999.9
            },
            {
                'column': 'pressure',
                'operator': 'lt',
                'value': 1015
            }
        ],
        'logic': 'OR'  # 첫 두 조건은 OR로 결합, 마지막 조건은 AND로 결합
    }
    
    # 필터링 실행
    output_file, report = algorithm.solution(test_data, './tmp/test_complex_filtering.csv', settings)
    
    # 결과 확인
    result_df = pd.read_csv(output_file)
    print(f"원본 데이터: {len(df)}행")
    print(f"필터링 결과: {len(result_df)}행")
    print("필터링된 데이터:")
    print(result_df)
    print()

def test_string_filtering():
    """문자열 필터링 테스트"""
    print("=== 문자열 필터링 테스트 ===")
    
    # 테스트 데이터 생성
    df = create_test_data()
    test_data = StringIO(df.to_csv(index=False))
    
    # 필터 설정: station이 'A', 'B', 'C' 중 하나
    settings = {
        'filters': [
            {
                'column': 'station',
                'operator': 'in',
                'value': ['A', 'B', 'C']
            }
        ],
        'logic': 'AND'
    }
    
    # 필터링 실행
    output_file, report = algorithm.solution(test_data, './tmp/test_string_filtering.csv', settings)
    
    # 결과 확인
    result_df = pd.read_csv(output_file)
    print(f"원본 데이터: {len(df)}행")
    print(f"필터링 결과: {len(result_df)}행")
    print("필터링된 데이터:")
    print(result_df)
    print()

def test_range_filtering():
    """범위 필터링 테스트"""
    print("=== 범위 필터링 테스트 ===")
    
    # 테스트 데이터 생성
    df = create_test_data()
    test_data = StringIO(df.to_csv(index=False))
    
    # 필터 설정: temperature가 20과 30 사이
    settings = {
        'filters': [
            {
                'column': 'temperature',
                'operator': 'between',
                'value': [20, 30]
            }
        ],
        'logic': 'AND'
    }
    
    # 필터링 실행
    output_file, report = algorithm.solution(test_data, './tmp/test_range_filtering.csv', settings)
    
    # 결과 확인
    result_df = pd.read_csv(output_file)
    print(f"원본 데이터: {len(df)}행")
    print(f"필터링 결과: {len(result_df)}행")
    print("필터링된 데이터:")
    print(result_df)
    print()

def test_null_filtering():
    """NULL 값 필터링 테스트"""
    print("=== NULL 값 필터링 테스트 ===")
    
    # NULL 값이 포함된 테스트 데이터 생성
    data = {
        'temperature': [25.5, None, 30.2, 15.8, None, 22.1],
        'wind_speed': [10.5, 15.2, None, 8.3, 12.7, 9.8],
        'station': ['A', 'B', 'C', 'D', 'E', 'F']
    }
    df = pd.DataFrame(data)
    test_data = StringIO(df.to_csv(index=False))
    
    # 필터 설정: temperature가 NULL이 아닌 값
    settings = {
        'filters': [
            {
                'column': 'temperature',
                'operator': 'is_not_null',
                'value': None
            }
        ],
        'logic': 'AND'
    }
    
    # 필터링 실행
    output_file, report = algorithm.solution(test_data, './tmp/test_null_filtering.csv', settings)
    
    # 결과 확인
    result_df = pd.read_csv(output_file)
    print(f"원본 데이터: {len(df)}행")
    print(f"필터링 결과: {len(result_df)}행")
    print("필터링된 데이터:")
    print(result_df)
    print()

def test_case_sensitive_filtering():
    """대소문자 구분 필터링 테스트"""
    print("=== 대소문자 구분 필터링 테스트 ===")
    
    # 대소문자가 섞인 테스트 데이터 생성
    data = {
        'station': ['SEOUL', 'seoul', 'Seoul', 'BUSAN', 'busan', 'Busan'],
        'region': ['North', 'north', 'NORTH', 'South', 'south', 'SOUTH'],
        'temperature': [25.5, 26.1, 24.8, 28.3, 27.9, 26.5]
    }
    df = pd.DataFrame(data)
    
    # 1. 대소문자 구분 (case_sensitive=True)
    print("1. 대소문자 구분 (case_sensitive=True)")
    test_data = StringIO(df.to_csv(index=False))
    settings = {
        'filters': [
            {
                'column': 'station',
                'operator': 'eq',
                'value': 'SEOUL'
            }
        ],
        'logic': 'AND',
        'case_sensitive': True
    }
    
    output_file, report = algorithm.solution(test_data, './tmp/test_case_sensitive_true.csv', settings)
    result_df = pd.read_csv(output_file)
    print(f"   결과: {len(result_df)}행 (SEOUL만 매칭)")
    print(f"   매칭된 값: {result_df['station'].tolist()}")
    
    # 2. 대소문자 무시 (case_sensitive=False)
    print("\n2. 대소문자 무시 (case_sensitive=False)")
    test_data = StringIO(df.to_csv(index=False))
    settings = {
        'filters': [
            {
                'column': 'station',
                'operator': 'eq',
                'value': 'seoul'
            }
        ],
        'logic': 'AND',
        'case_sensitive': False
    }
    
    output_file, report = algorithm.solution(test_data, './tmp/test_case_sensitive_false.csv', settings)
    result_df = pd.read_csv(output_file)
    print(f"   결과: {len(result_df)}행 (seoul, SEOUL, Seoul 모두 매칭)")
    print(f"   매칭된 값: {result_df['station'].tolist()}")
    
    # 3. contains 연산자로 대소문자 테스트
    print("\n3. contains 연산자로 대소문자 테스트")
    test_data = StringIO(df.to_csv(index=False))
    settings = {
        'filters': [
            {
                'column': 'region',
                'operator': 'contains',
                'value': 'north'
            }
        ],
        'logic': 'AND',
        'case_sensitive': False
    }
    
    output_file, report = algorithm.solution(test_data, './tmp/test_contains_case_insensitive.csv', settings)
    result_df = pd.read_csv(output_file)
    print(f"   결과: {len(result_df)}행 (north, North, NORTH 모두 매칭)")
    print(f"   매칭된 값: {result_df['region'].tolist()}")
    print()

if __name__ == '__main__':
    # 임시 디렉토리 생성
    os.makedirs('./tmp', exist_ok=True)
    
    print("CSV Query Filtering 테스트 시작\n")
    
    try:
        test_basic_filtering()
        test_complex_filtering()
        test_string_filtering()
        test_range_filtering()
        test_null_filtering()
        test_case_sensitive_filtering()
        
        print("모든 테스트가 성공적으로 완료되었습니다!")
        
    except Exception as e:
        print(f"테스트 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
