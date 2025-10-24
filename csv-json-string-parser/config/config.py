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
                'target_column': 'payload',
                'column_mapping': {
                    'channel_id': 'channel_id',
                    'created_at': 'created_at',
                    'entry_id': 'entry_id',
                    'field1': 'field1',
                    'field2': 'field2',
                    'field3': 'field3',
                    'field4': 'field4',
                    'field5': 'field5',
                    'field6': 'field6',
                    'field7': 'field7',
                    'field8': 'field8',
                    'latitude': 'latitude',
                    'longitude': 'longitude',
                    'elevation': 'elevation',
                    'status': 'status'
                },
                'keep_unknown': False,
                'error_handling': 'skip'
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
        },
        'production': {
            'input1': json.loads(os.environ['INPUT1']) if 'INPUT1' in os.environ else '',
            'settings': json.loads(os.environ['SETTINGS']) if 'SETTINGS' in os.environ else {},
            'output1': json.loads(os.environ['OUTPUT1']) if 'OUTPUT1' in os.environ else '',
            'task_report': json.loads(os.environ['TASK_REPORT']) if 'TASK_REPORT' in os.environ else '',
            'delete_input': json.loads(os.environ['DELETE_INPUT']) if 'DELETE_INPUT' in os.environ else False,
        }
    }
