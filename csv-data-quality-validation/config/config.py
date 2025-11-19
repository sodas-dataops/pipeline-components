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
                'validation_rules': [
                    {
                        'column': 'id',
                        'type': 'uniqueness',
                        'unique': True,
                        'name': 'id_uniqueness',
                        'weight': 2.0
                    },
                    {
                        'column': 'email',
                        'type': 'pattern',
                        'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                        'name': 'email_format',
                        'weight': 1.5
                    },
                    {
                        'column': 'age',
                        'type': 'range',
                        'min_value': 0,
                        'max_value': 120,
                        'name': 'age_range',
                        'weight': 1.0
                    },
                    {
                        'column': 'name',
                        'type': 'completeness',
                        'min_completeness': 0.95,
                        'name': 'name_completeness',
                        'weight': 1.0
                    },
                    {
                        'column': 'salary',
                        'type': 'custom',
                        'name': 'positive_salary_check',
                        'condition': {
                            'type': 'all',
                            'comparison': 'gt',
                            'threshold': 0
                        },
                        'weight': 1.5
                    },
                    {
                        'column': 'age',
                        'type': 'custom',
                        'name': 'mean_age_check',
                        'condition': {
                            'type': 'mean',
                            'comparison': 'gte',
                            'threshold': 25
                        },
                        'weight': 0.5
                    },
                    {
                        'column': 'name',
                        'type': 'length',
                        'min_length': 2,
                        'max_length': 50,
                        'name': 'name_length',
                        'weight': 1.0
                    },
                    {
                        'column': 'status',
                        'type': 'allowed_values',
                        'allowed_values': ['active', 'inactive', 'pending'],
                        'name': 'status_values',
                        'weight': 1.0
                    },
                    {
                        'column': 'income',
                        'type': 'outlier',
                        'method': 'iqr',
                        'threshold': 1.5,
                        'name': 'income_outlier',
                        'weight': 0.5
                    },
                    {
                        'column': 'score',
                        'type': 'statistical',
                        'check': 'mean',
                        'threshold': 70,
                        'comparison': 'gte',
                        'name': 'score_mean',
                        'weight': 1.0
                    },
                    {
                        'column': 'created_at',
                        'type': 'data_type',
                        'expected_type': 'datetime',
                        'datetime_format': '%Y-%m-%d %H:%M:%S',
                        'name': 'created_at_datetime',
                        'weight': 1.0
                    }
                ],
                'output_format': 'json',
                'include_details': True
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