import os
import json

args = {
    'development': {
        'input1': {
            'type': 'ceph',
            'end_point': '',
            'access_key': '',
            'secret_key': '',
            'bucket_name': 'bucket01',
            'object_path': 'dir01/input.csv',
        },
        'settings': {
            'target_column': 'embedding_target',
            'idx_column': '',
            'model_name': 'jhgan/ko-sroberta-multitask',
        },
        'output1': {
            'type': 'ceph',
            'end_point': '',
            'access_key': '',
            'secret_key': '',
            'bucket_name': 'bucket01',
            'object_path': 'dir01/embeddings.npz',
        },
        'task_report': {
            'type': 'ceph',
            'end_point': '',
            'access_key': '',
            'secret_key': '',
            'bucket_name': 'bucket01',
            'object_path': 'dir01/embedding_report.md',
        },
    },
    'production': {
        'input1': json.loads(os.environ['INPUT1']) if 'INPUT1' in os.environ else '',
        'settings': json.loads(os.environ['SETTINGS']) if 'SETTINGS' in os.environ else {},
        'output1': json.loads(os.environ['OUTPUT1']) if 'OUTPUT1' in os.environ else '',
        'task_report': json.loads(os.environ['TASK_REPORT']) if 'TASK_REPORT' in os.environ else '',
    }
}