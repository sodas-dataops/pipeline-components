import algorithm

if __name__ == '__main__' :
    algorithm.solution(
                        api_url='http://semantic-hub.221.154.134.31.traefik.me:10019/api/v1/pipeline/upload', 
                        file_path_query='jobs/jobs-contents-wordcount.json', 
                        local_file_path='./tmp/input_file', 
                        )