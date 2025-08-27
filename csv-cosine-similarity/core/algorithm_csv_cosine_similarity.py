import numpy as np
import json
from sklearn.metrics.pairwise import cosine_similarity
import time
import math
import os
from datetime import datetime

def generate_report(query_count: int, candidate_count: int, matched_count: int, 
                  avg_recommendations: float, input_files: dict, output_filename: str,
                  input_sizes: dict, output_size: int, elapsed_time: float,
                  top_n: int, threshold: float, batch_size: int) -> str:
    """
    작업 보고서를 생성하는 함수.
    
    Parameters:
    - query_count (int): 쿼리 데이터 수
    - candidate_count (int): 후보 데이터 수
    - matched_count (int): 매칭된 쿼리 수
    - avg_recommendations (float): 평균 추천 개수
    - input_files (dict): 입력 파일 경로
    - output_filename (str): 출력 파일 경로
    - input_sizes (dict): 입력 파일 크기 (bytes)
    - output_size (int): 출력 파일 크기 (bytes)
    - elapsed_time (float): 소요 시간 (초)
    - top_n (int): 최대 추천 개수
    - threshold (float): 유사도 임계값
    - batch_size (int): 배치 크기
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    report = f"""# 코사인 유사도 기반 추천 작업 보고서

## 1. 작업 개요
- **작업 유형**: 코사인 유사도 기반 추천
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **쿼리 데이터**:
  - 파일: {input_files['query']}
  - 크기: {input_sizes['query'] / 1024:.2f} KB
  - 데이터 수: {query_count}개
- **후보 데이터**:
  - 파일: {input_files['candidate']}
  - 크기: {input_sizes['candidate'] / 1024:.2f} KB
  - 데이터 수: {candidate_count}개

## 3. 추천 설정
- **최대 추천 개수**: {top_n}
- **유사도 임계값**: {threshold}
- **배치 크기**: {batch_size}

## 4. 처리 결과
- **출력 파일**: {output_filename}
- **파일 크기**: {output_size / 1024:.2f} KB
- **매칭된 쿼리 수**: {matched_count}개
- **매칭률**: {matched_count / query_count * 100:.2f}%
- **평균 추천 개수**: {avg_recommendations:.2f}개

## 5. 성능 지표
- **처리 속도**: {(input_sizes['query'] + input_sizes['candidate']) / elapsed_time / 1024:.2f} KB/s
- **쿼리 처리 속도**: {query_count / elapsed_time:.2f} 쿼리/초
- **추천 처리 속도**: {matched_count / elapsed_time:.2f} 추천/초

## 6. 작업 상태
- **상태**: 성공
- **처리 결과**: 코사인 유사도 기반 추천이 성공적으로 수행됨
"""
    return report

def process_batch(query_embeddings, candidate_embeddings, query_ids, candidate_ids, 
                 batch_start, batch_end, top_n, threshold):
    """배치 단위로 유사도 계산 및 결과 생성"""
    batch_results = []
    batch_sim_matrix = cosine_similarity(query_embeddings[batch_start:batch_end], candidate_embeddings)
    
    for i, sim_vector in enumerate(batch_sim_matrix):
        sim_scores = list(enumerate(sim_vector))
        sim_scores = [s for s in sim_scores if s[1] >= threshold]
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[:top_n]

        if not sim_scores:
            continue

        result = {
            "query": query_ids[batch_start + i].item() if hasattr(query_ids[batch_start + i], 'item') else str(query_ids[batch_start + i]),
            "recommendations": [
                {
                    "candidate": candidate_ids[idx].item() if hasattr(candidate_ids[idx], 'item') else str(candidate_ids[idx]),
                    "score": round(float(score), 4)
                } for idx, score in sim_scores
            ]
        }
        batch_results.append(result)
    
    return batch_results

def solution(query_npz: object, candidate_npz: object, output_filename: str, top_n: int, threshold: float, batch_size: int = 1000):
    """
    코사인 유사도를 기반으로 피 추천 대상(query)와 추천 대상(candidate) 간 매칭 결과 생성

    Parameters:
    - query_npz (object): 쿼리 임베딩 npz 파일
    - candidate_npz (object): 추천 후보 임베딩 npz 파일
    - output_filename (str): 추천 결과 저장할 JSON 파일 경로
    - top_n (int): 최대 추천 개수
    - threshold (float): 유사도 임계값
    - batch_size (int): 배치 처리 크기 (기본값: 1000)

    Returns:
    - tuple: (추천 결과, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] 코사인 유사도 기반 추천 작업을 시작합니다.")
    print(f"- 최대 추천 개수: {top_n}")
    print(f"- 유사도 임계값: {threshold}")
    print(f"- 배치 크기: {batch_size}")
    
    # 데이터 로드
    print("\n[1/4] 임베딩 데이터를 로드합니다...")
    query_data = np.load(query_npz, allow_pickle=True)
    candidate_data = np.load(candidate_npz, allow_pickle=True)
    
    query_embeddings = query_data['embeddings']
    query_ids = query_data['idxs'] if 'idxs' in query_data else np.arange(len(query_embeddings)).astype(str)
    print(f"- 쿼리 데이터: {len(query_embeddings)}개")

    candidate_embeddings = candidate_data['embeddings']
    candidate_ids = candidate_data['idxs'] if 'idxs' in candidate_data else np.arange(len(candidate_embeddings)).astype(str)
    print(f"- 후보 데이터: {len(candidate_embeddings)}개")

    # 입력 파일 크기 확인
    input_sizes = {
        'query': os.path.getsize(query_npz.name if hasattr(query_npz, 'name') else query_npz),
        'candidate': os.path.getsize(candidate_npz.name if hasattr(candidate_npz, 'name') else candidate_npz)
    }
    print(f"- 쿼리 파일 크기: {input_sizes['query'] / 1024:.2f} KB")
    print(f"- 후보 파일 크기: {input_sizes['candidate'] / 1024:.2f} KB")

    # 배치 처리
    print("\n[2/4] 배치 단위로 유사도를 계산합니다...")
    results = []
    total_queries = len(query_embeddings)
    num_batches = math.ceil(total_queries / batch_size)
    matched_count = 0

    for batch_idx in range(num_batches):
        batch_start = batch_idx * batch_size
        batch_end = min((batch_idx + 1) * batch_size, total_queries)
        
        print(f"- 배치 {batch_idx + 1}/{num_batches} 처리 중... ({batch_start + 1}~{batch_end}번째 쿼리)")
        
        batch_results = process_batch(
            query_embeddings, candidate_embeddings, 
            query_ids, candidate_ids,
            batch_start, batch_end, top_n, threshold
        )
        
        matched_count += len(batch_results)
        results.extend(batch_results)
        
        # 메모리 해제
        del batch_results
        if batch_idx < num_batches - 1:
            print(f"  - 현재까지 매칭된 쿼리 수: {matched_count}")

    # 결과 저장
    print("\n[3/4] 추천 결과를 저장합니다...")
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 출력 파일 크기 확인
    output_size = os.path.getsize(output_filename)
    print(f"- 출력 파일 크기: {output_size / 1024:.2f} KB")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\n[요약]")
    print(f"- 처리된 쿼리 수: {total_queries}")
    print(f"- 매칭된 쿼리 수: {matched_count}")
    print(f"- 평균 추천 개수: {sum(len(r['recommendations']) for r in results) / len(results) if results else 0:.2f}")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    print(f"- 저장 경로: {output_filename}")
    
    # 보고서 생성
    report = generate_report(
        total_queries, len(candidate_embeddings), matched_count,
        sum(len(r['recommendations']) for r in results) / len(results) if results else 0,
        {
            'query': query_npz.name if hasattr(query_npz, 'name') else query_npz,
            'candidate': candidate_npz.name if hasattr(candidate_npz, 'name') else candidate_npz
        },
        output_filename, input_sizes, output_size, elapsed_time,
        top_n, threshold, batch_size
    )
    
    return results, report