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
            'settings': {
                'lat_column': 'latitude',
                'lon_column': 'longitude',
                'check_missing': True,
                'check_range': True,
                'check_duplicates': False,
                'check_extreme_values': True,
                'check_precision': False,
                'precision_threshold': 6,
                'check_geographic_consistency': False,
                'region_column': '',
                'max_lat_std': 1.0,
                'max_lon_std': 1.0
            },
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
            'delete_input': False,
        },
        'production': {
            'input1': json.loads(os.environ['INPUT1']) if 'INPUT1' in os.environ else '',
            'settings': json.loads(os.environ['SETTINGS']) if 'SETTINGS' in os.environ else {},
            'output1': json.loads(os.environ['OUTPUT1']) if 'OUTPUT1' in os.environ else '',
            'task_report': json.loads(os.environ['TASK_REPORT']) if 'TASK_REPORT' in os.environ else '',
            'delete_input': os.getenv('DELETE_INPUT', 'false').lower() == 'true',
        }
    }