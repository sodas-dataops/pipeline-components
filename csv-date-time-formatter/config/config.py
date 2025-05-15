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
            'display_mode': 'replace',
            'suffix': '_new',
            'in_format': '%Y-%m-%d %H:%M:%S', 
            'out_format': '%Y/%m/%d',
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
            'display_mode': os.environ['DISPLAY_MODE'] if 'DISPLAY_MODE' in os.environ else 'replace',
            'suffix': os.environ['SUFFIX'] if 'SUFFIX' in os.environ else '_new',
            'in_format': os.environ['IN_FORMAT'] if 'IN_FORMAT' in os.environ else '%Y-%m-%d %H:%M:%S',
            'out_format': os.environ['OUT_FORMAT'] if 'OUT_FORMAT' in os.environ else '%Y/%m/%d',
            'output1': json.loads(os.environ['OUTPUT1']) if 'OUTPUT1' in os.environ else '',
            'task_report': json.loads(os.environ['TASK_REPORT']) if 'TASK_REPORT' in os.environ else '',
        }
    }