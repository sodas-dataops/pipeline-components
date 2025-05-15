import algorithm

if __name__ == '__main__' :
    algorithm.solution(
                        './tmp/test_input_data.csv', 
                        ["근무조건_급여_유형", "근무조건_급여_금액", "기업정보_회사명", "근무조건_지역_latitude", "근무조건_지역_longitude", "상세내용", "근무조건_4대보험"],
                        ["근로조건_급여_유형", "근로조건_급여_금액", "기업정보_사업체명", "구인사항_근무지_latitude", "구인사항_근무지_longitude", "구인사항_직무내용", "근로조건_가입보험"],
                        './tmp/test_output_data.csv'
                        )
