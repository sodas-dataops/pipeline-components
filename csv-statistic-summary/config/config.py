import os
import json

args =\
    {
        'development': {
            'input1': {
                'type': 'ceph',
                'end_point': 'http://object-storage.rook.xxxx.xxx.xxx.xxx:xxxxx',
                'access_key': '',
                'secret_key': '',
                'bucket_name': '',
                'object_path': '',
            },
            'input_cols': [], 
            'group_by': [],
            'statistics': [],
            'percentile_amounts': [],
            'trimmed_mean_amounts': 0.0,
            'output1': {
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
            'input1': json.loads(os.environ['INPUT1']) if 'INPUT1' in os.environ else '',
            'input_cols': json.loads(os.environ['INPUT_COLS']) if 'INPUT_COLS' in os.environ else [],
            'group_by': json.loads(os.environ['GROUP_BY']) if 'GROUP_BY' in os.environ else [],
            'statistics': json.loads(os.environ['STATISTICS']) if 'STATISTICS' in os.environ else [],
            'percentile_amounts': json.loads(os.environ['PERCENTILE_AMOUNTS']) if 'PERCENTILE_AMOUNTS' in os.environ else None,
            'trimmed_mean_amounts': float(os.environ['TRIMMED_MEAN_AMOUNTS']) if 'TRIMMED_MEAN_AMOUNTS' in os.environ else None,
            'output1': json.loads(os.environ['OUTPUT1']) if 'OUTPUT1' in os.environ else '',
            'task_report': json.loads(os.environ['TASK_REPORT']) if 'TASK_REPORT' in os.environ else '',
        }
    }