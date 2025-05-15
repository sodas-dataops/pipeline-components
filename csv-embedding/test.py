import algorithm

if __name__ == '__main__' :
    algorithm.solution(
                        './tmp/sample.csv',
                        './tmp/embedding.npz',
                        'embedding_target',
                        '제공처_URL',
                        'jhgan/ko-sroberta-multitask'
                        )