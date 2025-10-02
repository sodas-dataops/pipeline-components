import os
import json

args =\
    {
        'development': {
            'input1': {
                'end_point': 'http://object-storage.rook.xxx.xxx.xxx.xxx.traefik.me:xxxxx',
                'access_key': '',
                'secret_key': '',
                'bucket_name': 'test-bucket-1',
                'object_path': 'test_input_data.csv',
            },
            'settings': {
                'feature_names': ['sepal_length', 'sepal_width', 'petal_length', 'petal_width'],
                'target_name': 'species',
                'chart_mode': 'image',  # 'image' or 'interactive'
                'design_params': {
                    # 공통 디자인 설정 (이미지와 인터랙티브 모두 적용)
                    'common': {
                        'title': 'Pairplot of Iris Features',
                        'alpha': 0.7
                    },
                    
                    # 이미지 차트 전용 설정 (matplotlib/seaborn)
                    'image': {
                        'subplot_height': 3,
                        'figure_size': {
                            'width': 12,
                            'height': 10
                        },
                        'dpi': 300,
                        'title_fontsize': 16,
                        'matplotlib_style': 'default'
                    },
                    
                    # 인터랙티브 차트 전용 설정 (plotly)
                    'interactive': {
                        'marker_size': 6,
                        'marker_line_width': 0.5,
                        'width': 1200,
                        'height': 1000,
                        'show_legend': True,
                        'title_fontsize': 18,
                        'font_family': 'Arial',
                        'plot_bgcolor': 'white',
                        'paper_bgcolor': 'white',
                        'hover_template': '<b>%{x}</b><br>%{y}<br><extra></extra>'
                    }
                }
            },
            'output1': {
                'end_point': 'http://object-storage.rook.xxx.xxx.xxx.xxx.traefik.me:xxxxx',
                'access_key': '',
                'secret_key': '',
                'bucket_name': 'test-bucket-1',
                'object_path': 'test_output_data.png',
            },
            'task_report': {
                'end_point': 'http://object-storage.rook.xxx.xxx.xxx.xxx.traefik.me:xxxxx',
                'access_key': '',
                'secret_key': '',
                'bucket_name': 'test-bucket-1',
                'object_path': 'test_report.md',
            },
            'delete_input': False,
        },
        'production': {
            'input1': json.loads(os.environ['INPUT1']) if 'INPUT1' in os.environ else {},
            'settings': json.loads(os.environ['SETTINGS']) if 'SETTINGS' in os.environ else {},
            'output1': json.loads(os.environ['OUTPUT1']) if 'OUTPUT1' in os.environ else {},
            'task_report': json.loads(os.environ['TASK_REPORT']) if 'TASK_REPORT' in os.environ else {},
            'delete_input': os.getenv('DELETE_INPUT', 'false').lower() == 'true',
        }
    }