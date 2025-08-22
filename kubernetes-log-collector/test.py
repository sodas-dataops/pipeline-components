import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import base64
import tempfile
from config.config import args
from core import algorithm

def decode_kubeconfig_from_env(kubeconfig_b64):
    if not kubeconfig_b64:
        raise RuntimeError('KUBECONFIG_BASE64 환경변수가 필요합니다.')
    kubeconfig_bytes = base64.b64decode(kubeconfig_b64)
    tmp = tempfile.NamedTemporaryFile(delete=False, mode='wb', suffix='.yaml')
    tmp.write(kubeconfig_bytes)
    tmp.close()
    return tmp.name

def test_k8s_log_collector():
    print("Kubernetes Log Collector 테스트 시작")
    env_config = args['development']
    try:
        saved_files, report_content = algorithm.solution(
            settings=env_config['settings'],
            kubeconfig_path=decode_kubeconfig_from_env(env_config['settings']['kubeconfig_base64'])
        )
        print(f"테스트 성공! 저장 파일: {saved_files}")
        print("보고서 내용:")
        print(report_content)
        for f in saved_files:
            print(f"  - {f}")
    except Exception as e:
        print(f"테스트 실패: {e}")

if __name__ == "__main__":
    test_k8s_log_collector() 