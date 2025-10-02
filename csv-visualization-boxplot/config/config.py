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
                'group_by_column': 'category',
                'value_column': 'value',
                'chart_mode': 'image',  # 'image' or 'interactive'
                'design_params': {
                    # 공통 디자인 설정 (이미지와 인터랙티브 모두 적용)
                    'common': {
                        'title': 'Box Plot of Value by Category',
                        'xlabel': 'Category',
                        'ylabel': 'Value',
                        'xlabel_rotation': 45,
                        'alpha': 0.7
                    },
                    
                    # 이미지 차트 전용 설정 (matplotlib)
                    'image': {
                        'box_color': 'steelblue',
                        'whisker_color': 'black',
                        'median_color': 'red',
                        'outlier_color': 'red',
                        'figure_size': {
                            'width': 10,
                            'height': 8
                        },
                        'dpi': 300,
                        'show_grid': True,
                        'title_fontsize': 16,
                        'xlabel_fontsize': 12,
                        'ylabel_fontsize': 12,
                        'tick_fontsize': 10,
                        'matplotlib_style': 'default'
                    },
                    
                    # 인터랙티브 차트 전용 설정 (plotly)
                    'interactive': {
                        'color_by_group': True,
                        'width': 1000,
                        'height': 600,
                        'show_xgrid': True,
                        'show_ygrid': True,
                        'show_legend': True,
                        'title_fontsize': 18,
                        'xlabel_fontsize': 14,
                        'ylabel_fontsize': 14,
                        'tick_fontsize': 12,
                        'font_family': 'Arial',
                        'plot_bgcolor': 'white',
                        'paper_bgcolor': 'white',
                        'box_line_width': 2,
                        'outlier_size': 4,
                        'outlier_alpha': 0.8,
                        'hover_template': '<b>%{x}</b><br>Value: %{y}<br><extra></extra>'
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