import os
import json

args = \
    {
        'development': {
            'input1': {
                'end_point': '',
                'access_key': '',
                'secret_key': '',
                'bucket_name': 'bucket01',
                'object_path': 'dir01/input.csv',
            },
            'settings': {
                'datahub_api_url': 'http://sodas-profile.221.154.134.31.traefik.me:10017',
                'governance_api_url': 'http://api.221.154.134.31.traefik.me:10019',
                'datasetseries_id': 'your-datasetseries-id',
                'dataset_title': '새로운 데이터셋',
                'dataset_description': '데이터셋 설명',
                'distribution_bucket_name': 'bucket01',
                'distribution_title': '데이터 배포',
                'distribution_description': '데이터 배포 설명',
                'type': 'http://purl.org/dc/dcmitype/Dataset',
                'access_rights': 'http://purl.org/eprint/accessRights/OpenAccess',
                'license': 'http://creativecommons.org/licenses/by/4.0/'
            },
            'task_report': {
                'type': 'ceph',
                'end_point': 'http://object-storage.rook.xxx.xxx.xxx.xxx.traefik.me:xxxxx',
                'access_key': '',
                'secret_key': '',
                'bucket_name': 'bucket01',
                'object_path': 'dir01/task_report.md',
            },
        },
        'production': {
            'input1': json.loads(os.environ['INPUT1']) if 'INPUT1' in os.environ else '',
            'settings': json.loads(os.environ['SETTINGS']) if 'SETTINGS' in os.environ else {},
            'task_report': json.loads(os.environ['TASK_REPORT']) if 'TASK_REPORT' in os.environ else '',
        }
    } 