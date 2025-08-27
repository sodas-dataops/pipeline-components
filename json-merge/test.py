from core import algorithm_json_merge as algorithm

BASE_URL = "https://www.work24.go.kr/wk/a/b/1500/empDetailAuthView.do"
COMMON_QS = "infoTypeCd=VALIDATION&infoTypeGroup=tb_workinfoworknet"


def mk_url(wanted_auth_no: str) -> str:
    return f"{BASE_URL}?wantedAuthNo={wanted_auth_no}&{COMMON_QS}"


if __name__ == "__main__":
    algorithm.solution(
        input_data=[
            [
                {
                    "query": mk_url("K151122503190032"),
                    "recommendations": [
                        {"candidate": mk_url("K151122503190032"), "score": 1.0},
                        {"candidate": mk_url("K151322503210002"), "score": 0.9017},
                        {"candidate": mk_url("K151122503190057"), "score": 0.8853},
                    ],
                }
            ],
            [
                {
                    "query": mk_url("K170082503040013"),
                    "recommendations": [
                        {"candidate": mk_url("K170082503040013"), "score": 1.0},
                        {"candidate": mk_url("K170082503140005"), "score": 0.9005},
                        {"candidate": mk_url("Dd0cag2503240035"), "score": 0.8437},
                    ],
                }
            ],
        ],
        output_path="./tmp/test_output_data.json",
    )