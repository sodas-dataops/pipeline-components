import os
import json

args =\
    {
        'development': {
            'settings': {
                'host': 'relational.fel.cvut.cz',
                'port': 3306,
                'database': 'financial',
                'username': 'guest',
                'password': 'ctu-relational',
                'charset': 'utf8mb4',
                'sql_query': 'SELECT * FROM district LIMIT 100',
            },
            'output1': {
                'end_point': 'http://object-storage.rook.xxxx.xxx.xxx.xxx:xxxxx',
                'access_key': 'abc',
                'secret_key': 'abc',
                'bucket_name': 'bucket01',
                'object_path': 'dir/mysql_result.csv',
            },
            'task_report': {
                'end_point': 'http://object-storage.rook.xxxx.xxx.xxx.xxx:xxxxx',
                'access_key': 'abc',
                'secret_key': 'abc',
                'bucket_name': 'bucket01',
                'object_path': 'dir/report.md',
            },
        },
        'production': {
            'settings': json.loads(os.environ['SETTINGS']) if 'SETTINGS' in os.environ else '',
            'output1': json.loads(os.environ['OUTPUT1']) if 'OUTPUT1' in os.environ else '',
            'task_report': json.loads(os.environ['TASK_REPORT']) if 'TASK_REPORT' in os.environ else '',
        }
    } 