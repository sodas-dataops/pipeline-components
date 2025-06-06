import os
import json

args =\
    {
        'development': {
            'settings': {
                'json_data': '{"key": "value"}',  # 예시 JSON 데이터
            },
            'output1': {
                'type': 'ceph',
                'end_point': 'http://object-storage.rook.xxx.xxx.xxx.xxx.traefik.me:xxxxx',
                'access_key': '',
                'secret_key': '',
                'bucket_name': 'bucket01',
                'object_path': 'dir01/output.json',
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
            'settings': json.loads(os.environ['SETTINGS']) if 'SETTINGS' in os.environ else {},
            'output1': json.loads(os.environ['OUTPUT1']) if 'OUTPUT1' in os.environ else '',
            'task_report': json.loads(os.environ['TASK_REPORT']) if 'TASK_REPORT' in os.environ else '',
        }
    } 