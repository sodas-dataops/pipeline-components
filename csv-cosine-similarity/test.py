import algorithm

if __name__ == '__main__' :
    algorithm.solution(
                        './tmp/sample_embeddings.npz',
                        './tmp/sample_embeddings2.npz',
                        './tmp/recommendations.json',
                        top_n=3,
                        threshold=0.8
                        )