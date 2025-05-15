import os
import json

args = \
    {
        'development': {
            'number_of_input': 4,
            'input1': {
                'end_point': 'http://object-storage.rook.xxx.xxx.xxx.xxx.traefik.me:xxxxx',
                'access_key': '',
                'secret_key': '',
                'bucket_name': 'test-bucket-1',
                'object_path': 'test_input_data.json',
            },
            'input2': {
                'end_point': 'http://object-storage.rook.xxx.xxx.xxx.xxx.traefik.me:xxxxx',
                'access_key': '',
                'secret_key': '',
                'bucket_name': 'test-bucket-1',
                'object_path': 'test_input_data.json',
            },
            'input3': {
                'end_point': 'http://object-storage.rook.xxx.xxx.xxx.xxx.traefik.me:xxxxx',
                'access_key': '',
                'secret_key': '',
                'bucket_name': 'test-bucket-1',
                'object_path': 'test_input_data.json',
            },
            'input4': {
                'end_point': 'http://object-storage.rook.xxx.xxx.xxx.xxx.traefik.me:xxxxx',
                'access_key': '',
                'secret_key': '',
                'bucket_name': 'test-bucket-1',
                'object_path': 'test_input_data.json',
            },
            'output1': {
                'end_point': 'http://object-storage.rook.xxx.xxx.xxx.xxx.traefik.me:xxxxx',
                'access_key': '',
                'secret_key': '',
                'bucket_name': 'test-bucket-1',
                'object_path': 'test_output_data.json',
            },
            'delete_input': False,
        },
        'production': {
            'number_of_input': int(os.environ['NUMBER_OF_INPUT']) if 'NUMBER_OF_INPUT' in os.environ else 0,
            'input1': json.loads(os.environ['INPUT1']) if 'INPUT1' in os.environ else {},
            'input2': json.loads(os.environ['INPUT2']) if 'INPUT2' in os.environ else {},
            'input3': json.loads(os.environ['INPUT3']) if 'INPUT3' in os.environ else {},
            'input4': json.loads(os.environ['INPUT4']) if 'INPUT4' in os.environ else {},
            'output1': json.loads(os.environ['OUTPUT1']) if 'OUTPUT1' in os.environ else {},
            'delete_input': os.getenv('DELETE_INPUT', 'false').lower() == 'true',
        }
    }
