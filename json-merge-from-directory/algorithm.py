import json
import time

def solution(input_data: list, output_path: str) -> list:
    """
    디렉토리에서 읽어온 JSON 데이터들을 하나로 병합하여 저장합니다.

    Parameters:
    - input_data: 병합할 JSON 데이터 리스트
    - output_path: 결과를 저장할 파일 경로

    Returns:
    - list: 병합된 JSON 데이터
    """
    start_time = time.time()
    print(f"\n[시작] JSON 병합 작업을 시작합니다.")
    print(f"- 입력 데이터 수: {len(input_data)}개")
    
    # 데이터 병합
    print("\n[1/2] JSON 데이터를 병합합니다...")
    merged_data = []
    total_items = 0
    last_progress = 0
    
    for i, data in enumerate(input_data, 1):
        current_progress = int((i / len(input_data)) * 100)
        if current_progress % 5 == 0 and current_progress != last_progress:
            print(f"- 진행률: {current_progress}% ({i}/{len(input_data)} 파일 처리됨)")
            last_progress = current_progress
            
        if isinstance(data, list):
            items_count = len(data)
            merged_data.extend(data)
        else:
            items_count = 1
            merged_data.append(data)
        total_items += items_count
    
    print(f"- 총 병합된 항목 수: {total_items}개")
    
    # 결과 저장
    print("\n[2/2] 병합된 데이터를 저장합니다...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\n[요약]")
    print(f"- 처리된 입력 파일 수: {len(input_data)}")
    print(f"- 병합된 총 항목 수: {total_items}")
    print(f"- 평균 항목 수/파일: {total_items/len(input_data):.1f}")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    print(f"- 저장 경로: {output_path}")
    
    return merged_data