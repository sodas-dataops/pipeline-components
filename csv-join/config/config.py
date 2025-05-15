import os
import json

args =\
    {
        'development': {
            'left_table': {
                'type': 'ceph',
                'end_point': 'http://object-storage.rook.xxxx.xxx.xxx.xxx:xxxxx',
                'access_key': '',
                'secret_key': '',
                'bucket_name': '',
                'object_path': '',
            },
            'right_table': {
                'type': 'ceph',
                'end_point': 'http://object-storage.rook.xxxx.xxx.xxx.xxx:xxxxx',
                'access_key': '',
                'secret_key': '',
                'bucket_name': '',
                'object_path': '',
            },
            'left_on': ['xx'],
            'right_on': ['yy'],
            'how': 'inner',
            'lsuffix': '',
            'rsuffix': '',
            'sort': False,
            'result_table': {
                'type': 'ceph',
                'end_point': 'http://object-storage.rook.xxxx.xxx.xxx.xxx:xxxxx',
                'access_key': '',
                'secret_key': '',
                'bucket_name': '',
                'object_path': '',
            },
            'task_report': {
                'type': 'ceph',
                'end_point': 'http://object-storage.rook.xxxx.xxx.xxx.xxx:xxxxx',
                'access_key': '',
                'secret_key': '',
                'bucket_name': '',
                'object_path': '',
            },
        },
        'production': {
            'left_table': json.loads(os.environ['LEFT_TABLE']) if 'LEFT_TABLE' in os.environ else '',
            'right_table': json.loads(os.environ['RIGHT_TABLE']) if 'RIGHT_TABLE' in os.environ else '',
            'left_on': json.loads(os.environ['LEFT_ON']) if 'LEFT_ON' in os.environ else '',
            'right_on': json.loads(os.environ['RIGHT_ON']) if 'RIGHT_ON' in os.environ else '',
            'how': os.environ['HOW'] if 'HOW' in os.environ else '',
            'lsuffix': os.environ['LSUFFIX'] if 'LSUFFIX' in os.environ else '',
            'rsuffix': os.environ['RSUFFIX'] if 'RSUFFIX' in os.environ else '',
            'sort': json.loads(os.environ['SORT'].lower()) if 'SORT' in os.environ else True,
            'result_table': json.loads(os.environ['RESULT_TABLE']) if 'RESULT_TABLE' in os.environ else '',
            'task_report': json.loads(os.environ['TASK_REPORT']) if 'TASK_REPORT' in os.environ else '',
        }
    }