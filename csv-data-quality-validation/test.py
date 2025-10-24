import os
import sys
from io import StringIO
import json

# 상위 디렉터리의 core 모듈을 import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from core import algorithm_csv_data_quality_validation as algorithm

def test_basic_validation():
    """기본 검증 테스트"""
    print("\n" + "="*60)
    print("테스트 1: 기본 검증")
    print("="*60)
    
    # 샘플 데이터 생성
    csv_data = """id,name,email,age,salary
1,홍길동,hong@example.com,25,50000
2,김철수,kim@example.com,30,60000
3,이영희,lee@example.com,28,55000"""
    
    settings = {
        'validation_rules': [
            {
                'column': 'id',
                'type': 'uniqueness',
                'unique': True,
                'name': 'id_uniqueness',
                'weight': 2.0
            },
            {
                'column': 'email',
                'type': 'pattern',
                'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                'name': 'email_format',
                'weight': 1.5
            },
            {
                'column': 'age',
                'type': 'range',
                'min_value': 0,
                'max_value': 120,
                'name': 'age_range',
                'weight': 1.0
            }
        ],
        'output_format': 'json',
        'include_details': True
    }
    
    output_file = 'tmp/test_output_basic.json'
    input_data = StringIO(csv_data)
    
    result_file, report = algorithm.solution(input_data, output_file, settings)
    
    # 결과 확인
    with open(result_file, 'r', encoding='utf-8') as f:
        result = json.load(f)
    
    print(f"결과 파일: {result_file}")
    print(f"품질 점수: {result['summary']['quality_score']:.2f}점")
    print(f"통과한 규칙: {result['summary']['passed_rules']}개")
    print(f"실패한 규칙: {result['summary']['failed_rules']}개")
    
    assert result['summary']['passed_rules'] == 3, "모든 규칙이 통과해야 함"
    assert result['summary']['quality_score'] == 100.0, "완벽한 데이터는 100점"
    
    print("✓ 기본 검증 테스트 통과")


def test_with_issues():
    """문제가 있는 데이터 테스트"""
    print("\n" + "="*60)
    print("테스트 2: 문제가 있는 데이터")
    print("="*60)
    
    # 샘플 데이터 생성 (문제 포함)
    csv_data = """id,name,email,age,salary,status
1,홍길동,hong@example.com,25,50000,active
2,김철수,kim@example.com,150,60000,active
3,,lee@example.com,28,55000,pending
4,박민수,park@invalid,35,70000,invalid
5,홍길동,hong@example.com,25,50000,active"""
    
    settings = {
        'validation_rules': [
            {
                'column': 'id',
                'type': 'uniqueness',
                'unique': True,
                'name': 'id_uniqueness',
                'weight': 2.0
            },
            {
                'column': 'email',
                'type': 'pattern',
                'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                'name': 'email_format',
                'weight': 1.5
            },
            {
                'column': 'age',
                'type': 'range',
                'min_value': 0,
                'max_value': 120,
                'name': 'age_range',
                'weight': 1.0
            },
            {
                'column': 'name',
                'type': 'completeness',
                'min_completeness': 0.95,
                'name': 'name_completeness',
                'weight': 1.0
            },
            {
                'column': 'status',
                'type': 'allowed_values',
                'allowed_values': ['active', 'inactive', 'pending'],
                'name': 'status_values',
                'weight': 1.0
            }
        ],
        'output_format': 'json',
        'include_details': True
    }
    
    output_file = 'tmp/test_output_issues.json'
    input_data = StringIO(csv_data)
    
    result_file, report = algorithm.solution(input_data, output_file, settings)
    
    # 결과 확인
    with open(result_file, 'r', encoding='utf-8') as f:
        result = json.load(f)
    
    print(f"결과 파일: {result_file}")
    print(f"품질 점수: {result['summary']['quality_score']:.2f}점")
    print(f"통과한 규칙: {result['summary']['passed_rules']}개")
    print(f"실패한 규칙: {result['summary']['failed_rules']}개")
    
    # 품질 점수 상세 정보
    quality_details = result['summary']['quality_score_details']
    print(f"\n품질 점수 상세:")
    print(f"  - 전체 가중치: {quality_details['total_weight']}")
    print(f"  - 달성 가중치: {quality_details['achieved_weight']}")
    print(f"  - 규칙별 점수:")
    for rule_score in quality_details['rule_scores']:
        status = "✓" if rule_score['passed'] else "✗"
        print(f"    {status} {rule_score['rule_name']}: 가중치 {rule_score['weight']}, 점수 {rule_score['score']}")
    
    assert result['summary']['failed_rules'] > 0, "문제가 있는 데이터는 실패해야 함"
    assert result['summary']['quality_score'] < 100.0, "완벽하지 않은 데이터는 100점 미만"
    
    print("✓ 문제가 있는 데이터 테스트 통과")


def test_length_validation():
    """길이 검증 테스트"""
    print("\n" + "="*60)
    print("테스트 3: 길이 검증")
    print("="*60)
    
    csv_data = """id,name,email
1,홍길동,hong@example.com
2,김,very_long_email_address_that_exceeds_maximum_length@example.com
3,이영희,lee@example.com"""
    
    settings = {
        'validation_rules': [
            {
                'column': 'name',
                'type': 'length',
                'min_length': 2,
                'max_length': 10,
                'name': 'name_length',
                'weight': 1.0
            },
            {
                'column': 'email',
                'type': 'length',
                'max_length': 50,
                'name': 'email_length',
                'weight': 1.0
            }
        ],
        'output_format': 'json',
        'include_details': True
    }
    
    output_file = 'tmp/test_output_length.json'
    input_data = StringIO(csv_data)
    
    result_file, report = algorithm.solution(input_data, output_file, settings)
    
    with open(result_file, 'r', encoding='utf-8') as f:
        result = json.load(f)
    
    print(f"품질 점수: {result['summary']['quality_score']:.2f}점")
    print(f"통과한 규칙: {result['summary']['passed_rules']}개")
    print(f"실패한 규칙: {result['summary']['failed_rules']}개")
    
    print("✓ 길이 검증 테스트 통과")


def test_outlier_detection():
    """이상치 탐지 테스트"""
    print("\n" + "="*60)
    print("테스트 4: 이상치 탐지")
    print("="*60)
    
    csv_data = """id,income
1,50000
2,52000
3,51000
4,49000
5,1000000
6,45000
7,48000"""
    
    settings = {
        'validation_rules': [
            {
                'column': 'income',
                'type': 'outlier',
                'method': 'iqr',
                'threshold': 1.5,
                'name': 'income_outlier',
                'weight': 1.0
            }
        ],
        'output_format': 'json',
        'include_details': True
    }
    
    output_file = 'tmp/test_output_outlier.json'
    input_data = StringIO(csv_data)
    
    result_file, report = algorithm.solution(input_data, output_file, settings)
    
    with open(result_file, 'r', encoding='utf-8') as f:
        result = json.load(f)
    
    print(f"품질 점수: {result['summary']['quality_score']:.2f}점")
    print(f"통과한 규칙: {result['summary']['passed_rules']}개")
    
    # 이상치 정보 출력
    if result['validation_results']:
        outlier_result = result['validation_results'][0]
        if 'outlier_count' in outlier_result['details']:
            print(f"이상치 개수: {outlier_result['details']['outlier_count']}")
    
    print("✓ 이상치 탐지 테스트 통과")


def test_statistical_validation():
    """통계적 검증 테스트"""
    print("\n" + "="*60)
    print("테스트 5: 통계적 검증")
    print("="*60)
    
    csv_data = """id,score
1,85
2,90
3,75
4,95
5,80
6,88
7,82
8,92"""
    
    settings = {
        'validation_rules': [
            {
                'column': 'score',
                'type': 'statistical',
                'check': 'mean',
                'threshold': 85,
                'comparison': 'gte',
                'name': 'score_mean',
                'weight': 1.0
            }
        ],
        'output_format': 'json',
        'include_details': True
    }
    
    output_file = 'tmp/test_output_statistical.json'
    input_data = StringIO(csv_data)
    
    result_file, report = algorithm.solution(input_data, output_file, settings)
    
    with open(result_file, 'r', encoding='utf-8') as f:
        result = json.load(f)
    
    print(f"품질 점수: {result['summary']['quality_score']:.2f}점")
    print(f"통과한 규칙: {result['summary']['passed_rules']}개")
    
    # 통계값 출력
    if result['validation_results']:
        stat_result = result['validation_results'][0]
        if 'stat_value' in stat_result['details']:
            print(f"평균값: {stat_result['details']['stat_value']}")
    
    print("✓ 통계적 검증 테스트 통과")


def test_cross_column_validation():
    """다중 컬럼 검증 테스트"""
    print("\n" + "="*60)
    print("테스트 6: 다중 컬럼 검증")
    print("="*60)
    
    csv_data = """id,start_date,end_date
1,2024-01-01,2024-01-31
2,2024-02-01,2024-02-29
3,2024-03-01,2024-02-28
4,2024-04-01,2024-04-30"""
    
    settings = {
        'validation_rules': [
            {
                'type': 'cross_column',
                'comparison_type': 'simple',
                'columns': ['start_date', 'end_date'],
                'operator': '<',
                'name': 'date_range_check',
                'weight': 2.0
            }
        ],
        'output_format': 'json',
        'include_details': True
    }
    
    output_file = 'tmp/test_output_cross_column.json'
    input_data = StringIO(csv_data)
    
    result_file, report = algorithm.solution(input_data, output_file, settings)
    
    with open(result_file, 'r', encoding='utf-8') as f:
        result = json.load(f)
    
    print(f"품질 점수: {result['summary']['quality_score']:.2f}점")
    print(f"통과한 규칙: {result['summary']['passed_rules']}개")
    print(f"실패한 규칙: {result['summary']['failed_rules']}개")
    
    print("✓ 다중 컬럼 검증 테스트 통과")


def test_weighted_score():
    """가중치 기반 점수 테스트"""
    print("\n" + "="*60)
    print("테스트 7: 가중치 기반 점수 계산")
    print("="*60)
    
    csv_data = """id,name,email,age
1,홍길동,hong@example.com,25
2,김철수,kim@example.com,150
3,이영희,lee@example.com,28"""
    
    settings = {
        'validation_rules': [
            {
                'column': 'id',
                'type': 'uniqueness',
                'unique': True,
                'name': 'id_uniqueness',
                'weight': 2.0  # 높은 가중치
            },
            {
                'column': 'email',
                'type': 'pattern',
                'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                'name': 'email_format',
                'weight': 1.5
            },
            {
                'column': 'age',
                'type': 'range',
                'min_value': 0,
                'max_value': 120,
                'name': 'age_range',
                'weight': 1.0  # 낮은 가중치
            }
        ],
        'output_format': 'json',
        'include_details': True
    }
    
    output_file = 'tmp/test_output_weighted.json'
    input_data = StringIO(csv_data)
    
    result_file, report = algorithm.solution(input_data, output_file, settings)
    
    with open(result_file, 'r', encoding='utf-8') as f:
        result = json.load(f)
    
    print(f"품질 점수: {result['summary']['quality_score']:.2f}점")
    
    # 점수 계산 확인
    quality_details = result['summary']['quality_score_details']
    print(f"\n가중치 계산:")
    print(f"  - 전체 가중치: {quality_details['total_weight']}")
    print(f"  - 달성 가중치: {quality_details['achieved_weight']}")
    print(f"  - 예상 점수: {quality_details['achieved_weight'] / quality_details['total_weight'] * 100:.2f}점")
    
    # 2개 통과 (id, email), 1개 실패 (age)
    # 가중치: 2.0 + 1.5 = 3.5 / 4.5 = 77.78점
    expected_score = (2.0 + 1.5) / (2.0 + 1.5 + 1.0) * 100
    assert abs(result['summary']['quality_score'] - expected_score) < 0.01, f"예상 점수: {expected_score:.2f}점"
    
    print("✓ 가중치 기반 점수 계산 테스트 통과")


def run_all_tests():
    """모든 테스트 실행"""
    print("\n" + "="*60)
    print("데이터 품질 검증 컴포넌트 테스트 시작")
    print("="*60)
    
    try:
        test_basic_validation()
        test_with_issues()
        test_length_validation()
        test_outlier_detection()
        test_statistical_validation()
        test_cross_column_validation()
        test_weighted_score()
        
        print("\n" + "="*60)
        print("✓ 모든 테스트 통과!")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n✗ 테스트 실패: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 예외 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    run_all_tests()

