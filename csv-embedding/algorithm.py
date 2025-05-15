import pandas as pd
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
import math
from datetime import datetime
import time

def generate_report(
    df: pd.DataFrame,
    target_column: str,
    idx_column: str,
    model_name: str,
    input_filename: str,
    output_filename: str,
    elapsed_time: float,
    total_embeddings: int,
    new_embeddings: int,
    skipped_count: int
) -> str:
    """
    임베딩 작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - target_column (str): 임베딩 대상 컬럼
    - idx_column (str): 인덱스 컬럼
    - model_name (str): 사용된 모델 이름
    - input_filename (str): 입력 파일 경로
    - output_filename (str): 출력 파일 경로
    - elapsed_time (float): 소요 시간 (초)
    - total_embeddings (int): 총 임베딩 수
    - new_embeddings (int): 새로 생성된 임베딩 수
    - skipped_count (int): 스킵된 임베딩 수
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    report = f"""# CSV 임베딩 작업 보고서

## 1. 작업 개요
- **작업 유형**: CSV 텍스트 임베딩
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **입력 파일**: {input_filename}
- **행 수**: {len(df):,}행
- **컬럼 수**: {len(df.columns)}개
- **컬럼 목록**: {', '.join(df.columns)}

## 3. 임베딩 설정
- **대상 컬럼**: {target_column}
- **인덱스 컬럼**: {idx_column if idx_column else '자동 생성'}
- **사용 모델**: {model_name}

## 4. 처리 결과
- **출력 파일**: {output_filename}
- **총 임베딩 수**: {total_embeddings:,}개
- **새로 생성된 임베딩**: {new_embeddings:,}개
- **스킵된 임베딩**: {skipped_count:,}개

## 5. 성능 지표
- **처리 속도**: {total_embeddings / elapsed_time:.2f} 임베딩/초
- **새 임베딩 생성 속도**: {new_embeddings / elapsed_time:.2f} 임베딩/초

## 6. 작업 상태
- **상태**: 성공
- **처리 결과**: 임베딩이 성공적으로 생성됨
"""
    return report

def solution(
    data: object,
    output_filename: str,
    target_column: str,
    idx_column: str,
    model_name: str,
    existing_embeddings: dict = None
) -> tuple:
    """
    CSV 파일에서 지정된 컬럼의 텍스트를 임베딩하고, 결과를 npz 파일로 저장합니다.
    기존 임베딩 결과가 있는 경우 중복 임베딩을 방지합니다.

    Parameters:
    - data (object): pandas에서 읽을 수 있는 객체 (파일 핸들 또는 경로)
    - output_filename (str): 저장할 임베딩 결과 파일 경로 (.npz)
    - target_column (str): 임베딩을 생성할 대상 컬럼 이름
    - idx_column (str): 임베딩 결과와 매칭할 인덱스용 컬럼 이름
    - model_name (str): SentenceTransformer에서 사용할 모델 이름
    - existing_embeddings (dict): 기존 임베딩 결과 {'idxs': [...], 'embeddings': [...]}

    Returns:
    - tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    
    # CSV 데이터 로드
    df = pd.read_csv(data)

    # 대상 컬럼 확인
    if target_column not in df.columns:
        raise ValueError(f"'{target_column}' 컬럼이 존재하지 않습니다.")

    # 인덱스 컬럼 처리
    if idx_column not in df.columns:
        print(f"'{idx_column}' 컬럼이 없어 인덱스 번호를 사용합니다.")
        idxs = np.arange(len(df)).astype(str)
    else:
        idxs = df[idx_column].fillna('').astype(str).values

    # 임베딩 대상 텍스트 준비
    texts = df[target_column].fillna('').astype(str).tolist()

    # 기존 임베딩 결과 처리
    existing_idxs = set()
    existing_embeddings_list = None
    if existing_embeddings is not None and 'idxs' in existing_embeddings and 'embeddings' in existing_embeddings:
        existing_idxs = set(existing_embeddings['idxs'])
        existing_embeddings_list = existing_embeddings['embeddings']

    # 모델 로드 (transformers + torch)
    model_path = "./model"
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    model = AutoModel.from_pretrained(model_path, local_files_only=True)
    model.eval()

    # 임베딩 생성
    embeddings = []
    new_idxs = []
    total = len(texts)
    next_percent = 1
    skipped_count = 0

    for idx, (text, idx_val) in enumerate(zip(texts, idxs), 1):
        # 기존 임베딩이 있는 경우 스킵
        if idx_val in existing_idxs:
            skipped_count += 1
            continue

        with torch.no_grad():
            inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
            outputs = model(**inputs)
            last_hidden_state = outputs.last_hidden_state
            sentence_embedding = last_hidden_state.mean(dim=1).squeeze().cpu().numpy()
            embeddings.append(sentence_embedding)
            new_idxs.append(idx_val)

        # 진행률 출력
        percent_complete = math.floor((idx / total) * 100)
        if percent_complete >= next_percent:
            print(f"Progress: {percent_complete}% (Skipped: {skipped_count})")
            next_percent = percent_complete + 1

    # 새로운 임베딩과 기존 임베딩 병합
    if embeddings:
        new_embeddings = np.vstack(embeddings)
        if existing_embeddings_list is not None and len(existing_embeddings_list) > 0:
            final_embeddings = np.vstack([existing_embeddings_list, new_embeddings])
            final_idxs = np.concatenate([existing_embeddings['idxs'], new_idxs])
        else:
            final_embeddings = new_embeddings
            final_idxs = np.array(new_idxs)
    else:
        final_embeddings = existing_embeddings_list if existing_embeddings_list is not None else np.array([])
        final_idxs = existing_embeddings['idxs'] if existing_embeddings is not None else np.array([])

    # 임베딩과 인덱스를 .npz로 저장
    np.savez_compressed(output_filename, embeddings=final_embeddings, idxs=final_idxs)

    print(f"임베딩 완료: {output_filename}, 총 {len(final_idxs)}개 (새로 임베딩: {len(new_idxs)}, 스킵: {skipped_count})")

    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 보고서 생성
    report = generate_report(
        df=df,
        target_column=target_column,
        idx_column=idx_column,
        model_name=model_name,
        input_filename=data.name if hasattr(data, 'name') else str(data),
        output_filename=output_filename,
        elapsed_time=elapsed_time,
        total_embeddings=len(final_idxs),
        new_embeddings=len(new_idxs),
        skipped_count=skipped_count
    )
    
    return output_filename, report