import os
import json

args = \
    {
        'development': {
            'input1': {
                'type': 'ceph',
                'end_point': 'http://object-storage.rook.xxx.xxx.xxx.xxx.traefik.me:xxxxx',
                'access_key': '',
                'secret_key': '',
                'bucket_name': 'bucket01',
                'object_path': 'dir01/input.json',
            },
            'settings': {
                'flatten_json': False,  # JSON 평탄화 여부 (기본값: False)
                'flatten_separator': '_',  # 평탄화 시 사용할 구분자
                'preserve_keys': [],  # 평탄화하지 않고 보존할 키 목록 (기본값: [])
            },
            'output1': {
                'type': 'ceph',
                'end_point': 'http://object-storage.rook.xxx.xxx.xxx.xxx.traefik.me:xxxxx',
                'access_key': '',
                'secret_key': '',
                'bucket_name': 'bucket01',
                'object_path': 'dir01/output.csv',
            },
            'task_report': {
                'type': 'ceph',
                'end_point': 'http://object-storage.rook.xxx.xxx.xxx.xxx.traefik.me:xxxxx',
                'access_key': '',
                'secret_key': '',
                'bucket_name': 'bucket01',
                'object_path': 'dir01/task_report.md',
            },
        },
        'production': {
            'input1': json.loads(os.environ['INPUT1']) if 'INPUT1' in os.environ else '',
            'settings': json.loads(os.environ['SETTINGS']) if 'SETTINGS' in os.environ else {},
            'output1': json.loads(os.environ['OUTPUT1']) if 'OUTPUT1' in os.environ else '',
            'task_report': json.loads(os.environ['TASK_REPORT']) if 'TASK_REPORT' in os.environ else '',
        }
    }
