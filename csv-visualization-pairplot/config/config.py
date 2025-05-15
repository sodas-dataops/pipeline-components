import os
import json

args =\
    {
        'development': {
            'input1': {
                'type': 'ceph',
                'base_url': '...',
                'user_name': '...',
                'refresh_token': '...',
                'end_point': '...',
                'object_name': '...',
            },
            'feature_names': ['sepal_length', 'sepal_width', 'petal_length', 'petal_width'],
            'target_name': 'species',
            'output1': {
                'type': 'ceph',
                'base_url': '...',
                'user_name': '...',
                'refresh_token': '...',                
                'end_point': '...',
                'object_name': '...'
            }
        },
        'production': {
            'input1': json.loads(os.environ['INPUT1']) if 'INPUT1' in os.environ else '',
            'feature_names': json.loads(os.environ['FEATURE_NAMES']) if 'FEATURE_NAMES' in os.environ else '',
            'target_name': os.environ['TARGET_NAME'] if 'TARGET_NAME' in os.environ else '',
            'output1': json.loads(os.environ['OUTPUT1']) if 'OUTPUT1' in os.environ else ''
        }
    }