import algorithm
from io import StringIO

if __name__ == '__main__' :
    with open('./tmp/sample_embeddings.npz', 'rb') as f:
        query_npz = StringIO(f.read())
    with open('./tmp/sample_embeddings2.npz', 'rb') as f:
        candidate_npz = StringIO(f.read())
        
    algorithm.solution(
        query_npz=query_npz,
        candidate_npz=candidate_npz,
        output_filename='./tmp/recommendations.json',
        top_n=3,
        threshold=0.8
    )