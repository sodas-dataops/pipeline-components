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
                'x_column': 'x',
                'y_column': 'y', 
                'value_column': 'value',
                'chart_mode': 'image',
                'design_params': {
                    'common': {
                        'title': 'Heatmap',
                        'xlabel': 'X Axis',
                        'ylabel': 'Y Axis'
                    },
                    'image': {
                        'colormap': 'viridis',
                        'figure_size': {'width': 12, 'height': 8},
                        'annotate': False,
                        'format': '.2f',
                        'dpi': 300,
                        'title_fontsize': 16,
                        'label_fontsize': 12
                    },
                    'interactive': {
                        'colorscale': 'Viridis',
                        'width': 1000,
                        'height': 600,
                        'title_fontsize': 20,
                        'font_family': 'Arial',
                        'plot_bgcolor': 'white',
                        'paper_bgcolor': 'white'
                    }
                }
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
            'delete_input': json.loads(os.environ['DELETE_INPUT']) if 'DELETE_INPUT' in os.environ else False,
        }
    }