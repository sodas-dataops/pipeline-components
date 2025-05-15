import algorithm

if __name__ == '__main__' :
    algorithm.solution(
                        input_data=[
                            [
                                {
                                    "query": "https://www.work24.go.kr/wk/a/b/1500/empDetailAuthView.do?wantedAuthNo=K151122503190032&infoTypeCd=VALIDATION&infoTypeGroup=tb_workinfoworknet",
                                    "recommendations": [
                                    {
                                        "candidate": "https://www.work24.go.kr/wk/a/b/1500/empDetailAuthView.do?wantedAuthNo=K151122503190032&infoTypeCd=VALIDATION&infoTypeGroup=tb_workinfoworknet",
                                        "score": 1.0
                                    },
                                    {
                                        "candidate": "https://www.work24.go.kr/wk/a/b/1500/empDetailAuthView.do?wantedAuthNo=K151322503210002&infoTypeCd=VALIDATION&infoTypeGroup=tb_workinfoworknet",
                                        "score": 0.9017
                                    },
                                    {
                                        "candidate": "https://www.work24.go.kr/wk/a/b/1500/empDetailAuthView.do?wantedAuthNo=K151122503190057&infoTypeCd=VALIDATION&infoTypeGroup=tb_workinfoworknet",
                                        "score": 0.8853
                                    }
                                    ]
                                }
                            ],
                            [
                                {
                                    "query": "https://www.work24.go.kr/wk/a/b/1500/empDetailAuthView.do?wantedAuthNo=K170082503040013&infoTypeCd=VALIDATION&infoTypeGroup=tb_workinfoworknet",
                                    "recommendations": [
                                    {
                                        "candidate": "https://www.work24.go.kr/wk/a/b/1500/empDetailAuthView.do?wantedAuthNo=K170082503040013&infoTypeCd=VALIDATION&infoTypeGroup=tb_workinfoworknet",
                                        "score": 1.0
                                    },
                                    {
                                        "candidate": "https://www.work24.go.kr/wk/a/b/1500/empDetailAuthView.do?wantedAuthNo=K170082503140005&infoTypeCd=VALIDATION&infoTypeGroup=tb_workinfoworknet",
                                        "score": 0.9005
                                    },
                                    {
                                        "candidate": "https://www.work24.go.kr/wk/a/b/1500/empDetailAuthView.do?wantedAuthNo=Dd0cag2503240035&infoTypeCd=VALIDATION&infoTypeGroup=tb_workinfoworknet",
                                        "score": 0.8437
                                    }
                                    ]
                                }
                            ]
                        ], 
                        output_path='./tmp/test_output_data.json', 
                        )