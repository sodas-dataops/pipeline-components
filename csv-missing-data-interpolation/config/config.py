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
            'settings': {
                'interpolation_method': 'mean',
                'target_columns': [],
                'fill_direction': 'forward',
                'custom_value': 0,
                'knn_neighbors': 5
            },
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
            'settings': json.loads(os.environ['SETTINGS']) if 'SETTINGS' in os.environ else {},
            'output1': json.loads(os.environ['OUTPUT1']) if 'OUTPUT1' in os.environ else '',
            'task_report': json.loads(os.environ['TASK_REPORT']) if 'TASK_REPORT' in os.environ else '',
            'delete_input': os.environ.get('DELETE_INPUT', 'false').lower() == 'true',
        }
    }