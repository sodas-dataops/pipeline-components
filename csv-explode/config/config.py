import os
import json

args = \
    {
        'development': {
            'input1': {
                'end_point': 'http://object-storage.rook.xxx.xxx.xxx.xxx.traefik.me:xxxxx',
                'access_key': '',
                'secret_key': '',
                'bucket_name': 'test-bucket-1',
                'object_path': 'test_input_data.csv',
            },
            'settings': {
                'target_column': 'column_name',
                'column_type': 'list',  # 지원 타입: 'list', 'json', 'delimited'
                'output_column': 'exploded_column',
                'delimiter': ',',  # delimited 타입 사용시 구분자 (선택사항)
            },
            'output1': {
                'end_point': 'http://object-storage.rook.xxx.xxx.xxx.xxx.traefik.me:xxxxx',
                'access_key': '',
                'secret_key': '',
                'bucket_name': 'test-bucket-1',
                'object_path': 'test_output_data.csv',
            },
            'task_report': {
                'end_point': 'http://object-storage.rook.xxx.xxx.xxx.xxx.traefik.me:xxxxx',
                'access_key': '',
                'secret_key': '',
                'bucket_name': 'test-bucket-1',
                'object_path': 'test_report.md',
            },
            'delete_input': False,
        },
        'production': {
            'input1': json.loads(os.environ['INPUT1']) if 'INPUT1' in os.environ else {},
            'settings': json.loads(os.environ['SETTINGS']) if 'SETTINGS' in os.environ else {},
            'output1': json.loads(os.environ['OUTPUT1']) if 'OUTPUT1' in os.environ else {},
            'task_report': json.loads(os.environ['TASK_REPORT']) if 'TASK_REPORT' in os.environ else {},
            'delete_input': os.getenv('DELETE_INPUT', 'false').lower() == 'true',
        }
    }
