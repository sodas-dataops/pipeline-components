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
                'color_column': '',
                'size_column': '',
                'chart_mode': 'image',
                'design_params': {
                    'common': {
                        'title': 'Scatter Plot',
                        'xlabel': 'X Axis',
                        'ylabel': 'Y Axis'
                    },
                    'image': {
                        'figure_size': {'width': 10, 'height': 8},
                        'alpha': 0.6,
                        'point_size': 50,
                        'show_grid': True,
                        'dpi': 300,
                        'title_fontsize': 16,
                        'label_fontsize': 12
                    },
                    'interactive': {
                        'width': 1000,
                        'height': 600,
                        'title_fontsize': 20,
                        'font_family': 'Arial',
                        'plot_bgcolor': 'white',
                        'paper_bgcolor': 'white',
                        'show_legend': True,
                        'point_size': 8,
                        'opacity': 0.7,
                        'line_width': 1,
                        'line_color': 'white'
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