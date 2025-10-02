import os
import json

args =\
    {
        'development': {
            'input1': {
                'end_point': 'http://object-storage.rook.xxxx.xxx.xxx.xxx:xxxxx',
                'access_key': 'abc',
                'secret_key': 'abc',
                'bucket_name': 'bucket01',
                'object_path': 'dir/input.csv',
            },
            'operands': ['col1', 'col2'],
            'operators': ['+'],
            'column_name': 'col3',
            'strict_mode': True,
            'output1': {
                'end_point': 'http://object-storage.rook.xxxx.xxx.xxx.xxx:xxxxx',
                'access_key': 'abc',
                'secret_key': 'abc',
                'bucket_name': 'bucket01',
                'object_path': 'dir/output.csv',
            },
            'task_report': {
                'end_point': 'http://object-storage.rook.xxxx.xxx.xxx.xxx:xxxxx',
                'access_key': 'abc',
                'secret_key': 'abc',
                'bucket_name': 'bucket01',
                'object_path': 'dir/report.md',
            },
            'delete_input': False,
        },
        'production': {
            'input1': json.loads(os.environ['INPUT1']) if 'INPUT1' in os.environ else '',
            'operands': json.loads(os.environ['OPERANDS']) if 'OPERANDS' in os.environ else [],
            'operators': json.loads(os.environ['OPERATORS']) if 'OPERATORS' in os.environ else [],
            'column_name': os.environ['COLUMN_NAME'] if 'COLUMN_NAME' in os.environ else '',
            'strict_mode': os.environ.get('STRICT_MODE', 'true').lower() == 'true',
            'output1': json.loads(os.environ['OUTPUT1']) if 'OUTPUT1' in os.environ else '',
            'task_report': json.loads(os.environ['TASK_REPORT']) if 'TASK_REPORT' in os.environ else '',
            'delete_input': os.environ.get('DELETE_INPUT', 'false').lower() == 'true',
        }
    }