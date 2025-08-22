import os
import json

args =\
    {
        'development': {
            'settings': {
                'mqtt_broker': 'mqtt3.thingspeak.com',
                'mqtt_port': 1883,
                'mqtt_topic': 'channels/2421172/subscribe',
                'client_id': '',
                'username': '',
                'password': '',
                'keepalive': 60,
                'output_dir': './tmp/mqtt_messages',  # 여러 파일 저장 디렉터리
                'save_interval': 60,  # 파일 저장 주기(초)
                'duration': 300,  # 구독 지속 시간(초, -1 또는 None이면 무한)
            },
            'output1': {
                'end_point': 'http://object-storage.rook.xxxx.xxx.xxx.xxx:xxxxx',
                'access_key': 'abc',
                'secret_key': 'abc',
                'bucket_name': 'bucket01',
                'object_path': 'dir/mqtt_messages/',  # 디렉터리(프리픽스)
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