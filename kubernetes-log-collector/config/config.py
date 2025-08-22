import os
import json

args =\
    {
        'development': {
            'settings': {
                'kubeconfig_base64': '',  # 직접 입력 가능
                'namespace': 'default',
                'pod': '',
                'container': '',
                'mode': 'follow',  # 'once' or 'follow'
                'save_interval': 5,  # follow 모드에서 파일 분할 저장 주기(초)
                'duration': 300,      # follow 모드에서 모니터링 기간(초, None이면 무한)
                'output_dir': './tmp/logs',
            },
            'output1': {
                'end_point': 'http://object-storage.rook.xxxx.xxx.xxx.xxx:xxxxx',
                'access_key': 'abc',
                'secret_key': 'abc',
                'bucket_name': 'bucket01',
                'object_path': 'dir/k8s_logs/',
            },
            'task_report': {
                'end_point': 'http://object-storage.rook.xxxx.xxx.xxx.xxx:xxxxx',
                'access_key': 'abc',
                'secret_key': 'abc',
                'bucket_name': 'bucket01',
                'object_path': 'dir/report.md',
            },
        },
        'production': {
            'settings': json.loads(os.environ['SETTINGS']) if 'SETTINGS' in os.environ else '',
            'output1': json.loads(os.environ['OUTPUT1']) if 'OUTPUT1' in os.environ else '',
            'task_report': json.loads(os.environ['TASK_REPORT']) if 'TASK_REPORT' in os.environ else '',
        }
    } 