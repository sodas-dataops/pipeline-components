import os
import json

args =\
    {
        'development': {
            'input1': {
                'type': 'ceph',
                'end_point': 'http://object-storage.rook.xxx.xxx.xxx.xxx.traefik.me:xxxxx',
                'access_key': '',
                'secret_key': '',
                'bucket_name': 'bucket01',
                'object_path': 'dir01/acompany_products.csv',
            },
            'input_cols': ['product_id'], 
            'is_asc': True,
            'output1': {
                'type': 'ceph',
                'end_point': 'http://object-storage.rook.xxx.xxx.xxx.xxx.traefik.me:xxxxx',
                'access_key': '',
                'secret_key': '',
                'bucket_name': 'bucket01',
                'object_path': 'dir01/acompany_products_2.csv',
            },
            'task_report': {
                'type': 'ceph',
                'end_point': 'http://object-storage.rook.xxx.xxx.xxx.xxx.traefik.me:xxxxx',
                'access_key': '',
                'secret_key': '',
                'bucket_name': 'bucket01',
                'object_path': 'dir01/sort_report.md',
            },
        },
        'production': {
            'input1': json.loads(os.environ['INPUT1']) if 'INPUT1' in os.environ else '',
            'input_cols': json.loads(os.environ['INPUT_COLS']) if 'INPUT_COLS' in os.environ else [],
            'is_asc': json.loads(os.environ['IS_ASC'].lower()) if 'IS_ASC' in os.environ else True,
            'output1': json.loads(os.environ['OUTPUT1']) if 'OUTPUT1' in os.environ else '',
            'task_report': json.loads(os.environ['TASK_REPORT']) if 'TASK_REPORT' in os.environ else '',
        }
    }