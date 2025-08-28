from core import algorithm_upload_object_file_to_restapi as algorithm

if __name__ == '__main__' :
    algorithm.solution(
        api_url='http://semantic-hub.xxx.xxx.xxx.xxx:xxxxx/api/v1/pipeline/upload', 
        file_path_query='jobs/jobs-contents-wordcount.json', 
        local_file_path='./tmp/input_file', 
    )