import os
import json

args = {
    'development': {
        'query_embeddings_data': {
            'type': 'ceph',
            'end_point': '',
            'access_key': '',
            'secret_key': '',
            'bucket_name': 'bucket01',
            'object_path': 'dir01/input.npz',
        },
        'candidate_embeddings_data': {
            'type': 'ceph',
            'end_point': '',
            'access_key': '',
            'secret_key': '',
            'bucket_name': 'bucket01',
            'object_path': 'dir01/input.npz',
        },
        'settings': {
            'top_n': 3,
            'threshold': 0.8,
        },
        'output1': {
            'type': 'ceph',
            'end_point': '',
            'access_key': '',
            'secret_key': '',
            'bucket_name': 'bucket01',
            'object_path': 'dir01/result.json',
        },
        'task_report': {
            'type': 'ceph',
            'end_point': '',
            'access_key': '',
            'secret_key': '',
            'bucket_name': 'bucket01',
            'object_path': 'dir01/task_report.md',
        },
    },
    'production': {
        'query_embeddings_data': json.loads(os.environ['QUERY_EMBEDDINGS_DATA']) if 'QUERY_EMBEDDINGS_DATA' in os.environ else '',
        'candidate_embeddings_data': json.loads(os.environ['CANDIDATE_EMBEDDINGS_DATA']) if 'CANDIDATE_EMBEDDINGS_DATA' in os.environ else '',
        'settings': json.loads(os.environ['SETTINGS']) if 'SETTINGS' in os.environ else {},
        'output1': json.loads(os.environ['OUTPUT1']) if 'OUTPUT1' in os.environ else '',
        'task_report': json.loads(os.environ['TASK_REPORT']) if 'TASK_REPORT' in os.environ else '',
    }
}