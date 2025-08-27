import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import args
from core import algorithm_mysql_to_csv as algorithm

def test_mysql_to_csv():
    """MySQL to CSV 기능을 테스트합니다."""
    print("MySQL to CSV 테스트 시작")
    
    # 개발 환경 설정 사용
    env_config = args['development']
    
    # 테스트용 출력 파일 경로
    test_output_path = './tmp/test_result.csv'
    os.makedirs(os.path.dirname(test_output_path), exist_ok=True)
    
    try:
        # 알고리즘 실행
        output_file, report_content = algorithm.solution(
            mysql_config=env_config['mysql'],
            sql_query=env_config['sql_query'],
            output_file_path=test_output_path
        )
        
        print(f"테스트 성공! 출력 파일: {output_file}")
        print("보고서 내용:")
        print(report_content)
        
    except (FileNotFoundError, OSError, RuntimeError) as e:
        print(f"테스트 실패: {e}")

if __name__ == "__main__":
    test_mysql_to_csv() 