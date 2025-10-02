import pandas as pd
import requests
import urllib3
import random
import os
import csv
import time
from datetime import datetime

# InsecureRequestWarning 경고 숨기기
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_KEYS = [
]

def generate_report(
    df: pd.DataFrame,
    address_column: str,
    latitude_column: str,
    longitude_column: str,
    input_filename: str,
    output_filename: str,
    elapsed_time: float,
    total_addresses: int,
    successful_conversions: int,
    failed_conversions: int,
    cache_hits: int,
    validation_info: dict = None
) -> str:
    """
    주소-좌표 변환 작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - address_column (str): 주소 컬럼명
    - latitude_column (str): 위도 컬럼명
    - longitude_column (str): 경도 컬럼명
    - input_filename (str): 입력 파일 경로
    - output_filename (str): 출력 파일 경로
    - elapsed_time (float): 소요 시간 (초)
    - total_addresses (int): 총 처리된 주소 수
    - successful_conversions (int): 성공적으로 변환된 주소 수
    - failed_conversions (int): 변환 실패한 주소 수
    - cache_hits (int): 캐시에서 찾은 주소 수
    - validation_info (dict): 검증 정보 (경고 메시지 등)
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    report = f"""# 주소-좌표 변환 작업 보고서

## 1. 작업 개요
- **작업 유형**: 주소-좌표 변환
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **입력 파일**: {input_filename}
- **행 수**: {len(df):,}행
- **컬럼 수**: {len(df.columns)}개
- **컬럼 목록**: {', '.join(df.columns)}

## 3. 데이터 검증 결과
{f"- **경고**: {validation_info['warnings']}" if validation_info and validation_info.get('warnings') else ""}

## 4. 변환 설정
- **주소 컬럼**: {address_column}
- **위도 컬럼**: {latitude_column}
- **경도 컬럼**: {longitude_column}

## 5. 처리 결과
- **출력 파일**: {output_filename}
- **총 처리 주소**: {total_addresses:,}개
- **성공 변환**: {successful_conversions:,}개 ({successful_conversions/total_addresses*100:.1f}%)
- **실패 변환**: {failed_conversions:,}개 ({failed_conversions/total_addresses*100:.1f}%)
- **캐시 히트**: {cache_hits:,}개 ({cache_hits/total_addresses*100:.1f}%)

## 6. 성능 지표
- **처리 속도**: {total_addresses / elapsed_time:.2f} 주소/초
- **API 호출 수**: {successful_conversions - cache_hits:,}회

## 7. 작업 상태
- **상태**: 성공
- **처리 결과**: 주소가 성공적으로 좌표로 변환됨
"""
    return report

def validate_columns(df: pd.DataFrame, address_column: str, latitude_column: str, longitude_column: str) -> dict:
    """
    컬럼들의 존재 여부를 검증하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 검증할 DataFrame
    - address_column (str): 주소 컬럼명
    - latitude_column (str): 위도 컬럼명
    - longitude_column (str): 경도 컬럼명
    
    Returns:
    - dict: 검증 결과 정보
    """
    validation_info = {
        'is_valid': True,
        'warnings': [],
        'missing_columns': []
    }
    
    # 주소 컬럼 존재 여부 확인
    if address_column not in df.columns:
        validation_info['is_valid'] = False
        validation_info['missing_columns'].append(address_column)
        warning_msg = f"주소 컬럼 '{address_column}'이 데이터에 존재하지 않습니다."
        validation_info['warnings'].append(warning_msg)
        print(f"⚠️  경고: {warning_msg}")
    
    # 위도/경도 컬럼이 이미 존재하는지 확인
    if latitude_column in df.columns:
        warning_msg = f"위도 컬럼 '{latitude_column}'이 이미 존재합니다. 기존 데이터가 덮어쓰여집니다."
        validation_info['warnings'].append(warning_msg)
        print(f"⚠️  경고: {warning_msg}")
    
    if longitude_column in df.columns:
        warning_msg = f"경도 컬럼 '{longitude_column}'이 이미 존재합니다. 기존 데이터가 덮어쓰여집니다."
        validation_info['warnings'].append(warning_msg)
        print(f"⚠️  경고: {warning_msg}")
    
    return validation_info

def get_coordinates_vworld(address):
    """
    VWorld API를 이용하여 주소로부터 경도와 위도를 얻는 함수.
    
    Parameters:
    - address: 도로명 주소 문자열
    - key: VWorld API 인증 키
    
    Returns:
    - x: 경도
    - y: 위도
    """
    global API_KEYS

    if not API_KEYS:
        print("No API keys available.")
        return None, None

    api_url = "http://api.vworld.kr/req/address?"

    key_index = random.randint(0, len(API_KEYS) - 1)

    while API_KEYS:
        if key_index >= len(API_KEYS):
            key_index = 0

        key = API_KEYS[key_index]
        params = {
            "service": "address",
            "request": "getcoord",
            "address": address,
            "format": "json",
            "type": "road",
            "key": key
        }
    
        try:
            response = requests.get(api_url, params=params, timeout=10)
            response.raise_for_status()  # HTTP 오류 발생 시 예외 처리
            data = response.json()

            status = data['response']['status']
        
            # API 응답 상태 확인 및 결과 처리
            if status == 'OK':
                point = data['response']['result']['point']
                return float(point['y']), float(point['x'])  # 위도(y), 경도(x)
            elif status == 'NOT_FOUND':
                print(f"Failed to retrieve coordinates for address: {address} - Status: {status}")
                return None, None
            else:
                print(f"호출 실패 - 다음 API 키로 전환")
                API_KEYS.remove(key)
                continue

        except requests.RequestException as e:
            print(f"Request failed for address: {address} - Error: {e}")
            return None, None

        key_index += 1

    print(f"[{address}] 사용 가능한 모든 API 키 실패")
    return None, None

def solution(data: object, address_column: str, latitude_column_name: str = 'latitude', longitude_column_name: str = 'longitude', output_file: str = 'output_with_coordinates.csv') -> tuple:
    """
    CSV 파일에서 한국 도로명 주소로부터 위도와 경도를 추출하여 새로운 컬럼에 저장하는 함수.

    Parameters:
    - data: CSV 파일 경로
    - address_column: 주소가 있는 컬럼명
    - latitude_column_name: 위도를 저장하는 컬럼명 (기본값 'latitude')
    - longitude_column_name: 경도를 저장하는 컬럼명 (기본값 'longitude')
    - output_file: 위도와 경도 정보를 포함한 CSV 파일의 저장 경로 (기본값 'output_with_coordinates.csv')
    
    Returns:
    - tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    
    # CSV 데이터 로드
    dataFile = pd.read_csv(data)
    print(f"데이터 로드 완료: {len(dataFile)}행, {len(dataFile.columns)}개 컬럼")
    print(f"컬럼 목록: {', '.join(dataFile.columns)}")

    # 컬럼 검증
    print("\n[1/4] 컬럼을 검증합니다...")
    validation_info = validate_columns(dataFile, address_column, latitude_column_name, longitude_column_name)
    
    # 주소 컬럼이 존재하지 않으면 에러 발생
    if not validation_info['is_valid']:
        raise ValueError(f"필수 컬럼이 존재하지 않습니다: {', '.join(validation_info['missing_columns'])}")

    # 위도와 경도 컬럼 추가
    print("\n[2/4] 위도와 경도 컬럼을 추가합니다...")
    dataFile[latitude_column_name] = None
    dataFile[longitude_column_name] = None

    # 캐시 파일 로드
    print("\n[3/4] 캐시 파일을 로드합니다...")
    cache_file = 'address_cache.csv'
    address_cache = {}
    if os.path.exists(cache_file):
        cache_df = pd.read_csv(cache_file)
        for _, row in cache_df.iterrows():
            address_cache[row['work_location']] = (row['latitude'], row['longitude'])
        print(f"캐시 파일 로드 완료: {len(address_cache)}개 주소")
    else:
        print("캐시 파일이 존재하지 않습니다. 새로 생성합니다.")

    # 통계 변수 초기화
    total_addresses = 0
    successful_conversions = 0
    failed_conversions = 0
    cache_hits = 0

    # 각 주소에 대해 위도와 경도 추출
    print("\n[4/4] 주소-좌표 변환을 수행합니다...")
    for idx, row in dataFile.iterrows():
        address = row[address_column]
        if not address or pd.isna(address):
            continue

        total_addresses += 1

        if address in address_cache:
            lat, lon = address_cache[address]
            cache_hits += 1
            successful_conversions += 1
        else:
            lat, lon = get_coordinates_vworld(address)
            if lat is not None and lon is not None:
                address_cache[address] = (lat, lon)
                successful_conversions += 1
                print(f"[API] {address} -> ({lat}, {lon})")
            else:
                failed_conversions += 1
                print(f"[FAIL] {address} -> None")

        dataFile.at[idx, latitude_column_name] = lat
        dataFile.at[idx, longitude_column_name] = lon

    # 결과를 CSV 파일로 저장
    dataFile.to_csv(output_file, index=False)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 보고서 생성
    report = generate_report(
        df=dataFile,
        address_column=address_column,
        latitude_column=latitude_column_name,
        longitude_column=longitude_column_name,
        input_filename=data.name if hasattr(data, 'name') else str(data),
        output_filename=output_file,
        elapsed_time=elapsed_time,
        total_addresses=total_addresses,
        successful_conversions=successful_conversions,
        failed_conversions=failed_conversions,
        cache_hits=cache_hits,
        validation_info=validation_info
    )
    
    return output_file, report
