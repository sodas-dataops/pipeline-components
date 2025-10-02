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
                'feature_name': 'quantity',
                'chart_mode': 'image',  # 'image' or 'interactive'
                'design_params': {
                    # 공통 디자인 설정 (이미지와 인터랙티브 모두 적용)
                    'common': {
                        'title': 'Pie Chart of Quantity'
                    },
                    
                    # 이미지 차트 전용 설정 (matplotlib)
                    'image': {
                        'colors': None,  # 기본 색상 사용
                        'explode': None,  # 분리 효과 없음
                        'shadow': False,
                        'startangle': 90,
                        'figure_size': {
                            'width': 10,
                            'height': 8
                        },
                        'dpi': 300,
                        'text_fontsize': 24,
                        'title_fontsize': 48,
                        'legend_fontsize': 18
                    },
                    
                    # 인터랙티브 차트 전용 설정 (plotly)
                    'interactive': {
                        'width': 800,
                        'height': 600,
                        'show_legend': True,
                        'legend_fontsize': 14,
                        'legend_orientation': 'v',
                        'text_position': 'inside',
                        'text_info': 'label+percent',
                        'text_fontsize': 12,
                        'line_width': 2,
                        'line_color': 'white',
                        'rotation': 0,
                        'title_fontsize': 24,
                        'font_family': 'Arial',
                        'plot_bgcolor': 'white',
                        'paper_bgcolor': 'white',
                        'hover_template': '<b>%{label}</b><br>Value: %{value}<br>Percentage: %{percent}<br><extra></extra>'
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