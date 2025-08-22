import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import args
from . import algorithm

def test_mqtt_subscriber():
    print("MQTT Subscriber 테스트 시작")
    env_config = args['development']
    output_dir = './tmp/test_mqtt_messages'
    os.makedirs(output_dir, exist_ok=True)
    try:
        output_path, report_content = algorithm.solution(
            settings=env_config['settings']
        )
        print(f"테스트 성공! 출력 파일: {output_path}")
        print("보고서 내용:")
        print(report_content)
        with open(output_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"메시지 샘플 (최대 3개):")
            for line in lines[:3]:
                print(line.strip())
    except Exception as e:
        print(f"테스트 실패: {e}")

if __name__ == "__main__":
    test_mqtt_subscriber() 