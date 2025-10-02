import os
import time
from datetime import datetime
from config.config import args
import pandas as pd

env = 'development' if not 'APP_ENV' in os.environ else os.environ['APP_ENV']
args = args[env]

def validate_input_columns(df: pd.DataFrame, input_cols: list) -> dict:
    """
    입력 컬럼들의 존재 여부를 검증하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 검증할 DataFrame
    - input_cols (list): 검증할 입력 컬럼 목록
    
    Returns:
    - dict: 검증 결과 정보
    """
    validation_result = {
        'is_valid': True,
        'errors': [],
        'missing_columns': [],
        'existing_columns': []
    }
    
    for col in input_cols:
        if col not in df.columns:
            validation_result['errors'].append(f"입력 컬럼 '{col}'이 존재하지 않습니다.")
            validation_result['missing_columns'].append(col)
            validation_result['is_valid'] = False
        else:
            validation_result['existing_columns'].append(col)
    
    return validation_result

def validate_output_columns(df: pd.DataFrame, input_cols: list, output_cols: list) -> dict:
    """
    출력 컬럼들의 유효성을 검증하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 검증할 DataFrame
    - input_cols (list): 입력 컬럼 목록
    - output_cols (list): 출력 컬럼 목록
    
    Returns:
    - dict: 검증 결과 정보
    """
    validation_result = {
        'is_valid': True,
        'errors': [],
        'warnings': [],
        'conflicting_columns': [],
        'duplicate_outputs': []
    }
    
    # 입력 컬럼과 출력 컬럼 개수 일치 확인
    if len(input_cols) != len(output_cols):
        validation_result['errors'].append(
            f"입력 컬럼 개수({len(input_cols)})와 출력 컬럼 개수({len(output_cols)})가 일치하지 않습니다."
        )
        validation_result['is_valid'] = False
        return validation_result
    
    # 출력 컬럼명 중복 확인
    if len(output_cols) != len(set(output_cols)):
        duplicates = [col for col in output_cols if output_cols.count(col) > 1]
        validation_result['errors'].append(f"출력 컬럼명에 중복이 있습니다: {set(duplicates)}")
        validation_result['duplicate_outputs'] = list(set(duplicates))
        validation_result['is_valid'] = False
    
    # 기존 컬럼과의 충돌 확인
    existing_columns = set(df.columns)
    input_columns_set = set(input_cols)
    
    for i, (input_col, output_col) in enumerate(zip(input_cols, output_cols)):
        # 출력 컬럼이 기존 컬럼과 충돌하는지 확인 (입력 컬럼 제외)
        if output_col in existing_columns and output_col != input_col:
            validation_result['errors'].append(
                f"출력 컬럼 '{output_col}'이 기존 컬럼과 충돌합니다. (입력 컬럼: '{input_col}')"
            )
            validation_result['conflicting_columns'].append({
                'input_col': input_col,
                'output_col': output_col,
                'index': i
            })
            validation_result['is_valid'] = False
        
        # 컬럼명 패턴 검증 (영문자, 숫자, 언더스코어만 허용)
        if not output_col.replace('_', '').replace(' ', '').isalnum() or output_col[0].isdigit():
            validation_result['errors'].append(
                f"출력 컬럼명 '{output_col}'이 유효하지 않습니다. 영문자, 숫자, 언더스코어만 허용되며 숫자로 시작할 수 없습니다."
            )
            validation_result['is_valid'] = False
    
    return validation_result

def validate_column_mapping(df: pd.DataFrame, input_cols: list, output_cols: list) -> dict:
    """
    컬럼 매핑의 전체적인 유효성을 검증하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 검증할 DataFrame
    - input_cols (list): 입력 컬럼 목록
    - output_cols (list): 출력 컬럼 목록
    
    Returns:
    - dict: 검증 결과 정보
    """
    validation_result = {
        'is_valid': True,
        'errors': [],
        'warnings': [],
        'input_validation': None,
        'output_validation': None
    }
    
    # 입력 컬럼 검증
    input_validation = validate_input_columns(df, input_cols)
    validation_result['input_validation'] = input_validation
    
    if not input_validation['is_valid']:
        validation_result['errors'].extend(input_validation['errors'])
        validation_result['is_valid'] = False
    
    # 출력 컬럼 검증
    output_validation = validate_output_columns(df, input_cols, output_cols)
    validation_result['output_validation'] = output_validation
    
    if not output_validation['is_valid']:
        validation_result['errors'].extend(output_validation['errors'])
        validation_result['is_valid'] = False
    
    # 경고사항 추가
    if output_validation['warnings']:
        validation_result['warnings'].extend(output_validation['warnings'])
    
    return validation_result

def generate_report(df: pd.DataFrame, input_cols: list, output_cols: list,
                  input_filename: str, output_filename: str, input_size: int, output_size: int,
                  elapsed_time: float, validation_info: dict = None) -> str:
    """
    작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - input_cols (list): 변경 전 컬럼 목록
    - output_cols (list): 변경 후 컬럼 목록
    - input_filename (str): 입력 파일 경로
    - output_filename (str): 출력 파일 경로
    - input_size (int): 입력 파일 크기 (bytes)
    - output_size (int): 출력 파일 크기 (bytes)
    - elapsed_time (float): 소요 시간 (초)
    - validation_info (dict): 데이터 검증 정보
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    report = f"""# CSV 컬럼 이름 변경 작업 보고서

## 1. 작업 개요
- **작업 유형**: CSV 컬럼 이름 변경
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **입력 파일**: {input_filename}
- **파일 크기**: {input_size / 1024:.2f} KB
- **행 수**: {len(df)}
- **기존 컬럼 수**: {len(df.columns)}
- **기존 컬럼**: {', '.join(df.columns)}

## 3. 변경 설정
- **변경된 컬럼 수**: {len(input_cols)}
- **변경 내용**:
{chr(10).join([f"- {input_cols[i]} → {output_cols[i]}" for i in range(len(input_cols))])}

## 4. 처리 결과
- **출력 파일**: {output_filename}
- **파일 크기**: {output_size / 1024:.2f} KB
- **새 컬럼 수**: {len(df.columns)}
- **새 컬럼**: {', '.join(df.columns)}

## 5. 성능 지표
- **처리 속도**: {input_size / elapsed_time / 1024:.2f} KB/s
- **압축률**: {(1 - output_size / input_size) * 100:.2f}%
- **처리 효율**: {len(df) / elapsed_time:.2f} 행/초

## 6. 데이터 검증 결과
"""
    
    # 검증 정보가 있는 경우 추가
    if validation_info:
        report += f"- **입력 컬럼 검증**: {'성공' if validation_info.get('input_validation', {}).get('is_valid', True) else '실패'}\n"
        report += f"- **출력 컬럼 검증**: {'성공' if validation_info.get('output_validation', {}).get('is_valid', True) else '실패'}\n"
        
        # 누락된 컬럼 정보
        if validation_info.get('input_validation', {}).get('missing_columns'):
            report += "- **누락된 입력 컬럼**:\n"
            for col in validation_info['input_validation']['missing_columns']:
                report += f"  - {col}\n"
        
        # 충돌하는 컬럼 정보
        if validation_info.get('output_validation', {}).get('conflicting_columns'):
            report += "- **충돌하는 출력 컬럼**:\n"
            for conflict in validation_info['output_validation']['conflicting_columns']:
                report += f"  - {conflict['input_col']} → {conflict['output_col']}\n"
        
        # 중복된 출력 컬럼 정보
        if validation_info.get('output_validation', {}).get('duplicate_outputs'):
            report += "- **중복된 출력 컬럼**:\n"
            for col in validation_info['output_validation']['duplicate_outputs']:
                report += f"  - {col}\n"
        
        # 경고사항
        if validation_info.get('warnings'):
            report += "- **경고사항**:\n"
            for warning in validation_info['warnings']:
                report += f"  - {warning}\n"
    else:
        report += "- **데이터 검증**: 수행되지 않음\n"

    report += """
## 7. 작업 상태
- **상태**: 성공
- **처리 결과**: 컬럼 이름이 성공적으로 변경됨
"""
    return report

def solution(data, input_cols, output_cols, output_filename):
    """
    Samsung Brightics ML v3.9의 Change Column Name 함수를 파이썬으로 구현한 알고리즘

    Parameters:
        data (str): CSV 파일 경로. 알고리즘 내에서 pandas의 read_csv로 읽어와야 합니다.
        input_cols (list of str): 변경할 기존 컬럼 이름들의 리스트.
        output_cols (list of str): 변경할 새로운 컬럼 이름들의 리스트. 'input_cols' 파라미터와 순서가 일치해야 합니다.
        output_filename (str): 변경된 데이터프레임을 저장할 CSV 파일의 이름.

    Returns:
        tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] CSV 컬럼 이름 변경 작업을 시작합니다.")
    print(f"- 변경할 컬럼 수: {len(input_cols)}")
    print(f"- 변경 내용: {', '.join([f'{input_cols[i]} → {output_cols[i]}' for i in range(len(input_cols))])}")
    
    # CSV 파일 읽기
    print("\n[1/4] CSV 파일을 로드합니다...")
    df = pd.read_csv(data)
    print(f"- 총 {len(df)}개의 행이 로드되었습니다.")
    print(f"- 기존 컬럼: {', '.join(df.columns)}")
    
    # 입력 파일 크기 확인
    input_size = len(data.getvalue().encode('utf-8'))
    print(f"- 입력 파일 크기: {input_size / 1024:.2f} KB")
    
    # 컬럼 매핑 유효성 검증
    print("\n[2/4] 컬럼 매핑을 검증합니다...")
    validation_info = validate_column_mapping(df, input_cols, output_cols)
    
    if not validation_info['is_valid']:
        error_msg = "컬럼 매핑 검증 실패:\n" + "\n".join(validation_info['errors'])
        raise ValueError(error_msg)
    
    print("- 모든 컬럼 매핑이 유효합니다.")
    
    # 경고사항 출력
    if validation_info['warnings']:
        print("⚠️  경고사항:")
        for warning in validation_info['warnings']:
            print(f"  - {warning}")
    
    # 컬럼 이름 변경
    print("\n[3/4] 컬럼 이름을 변경합니다...")
    for input_col, output_col in zip(input_cols, output_cols):
        df.rename(columns={input_col: output_col}, inplace=True)
        print(f"- {input_col} → {output_col}")
    
    # 변경된 데이터프레임을 CSV 파일로 저장
    print("\n[4/4] 결과를 CSV로 저장합니다...")
    df.to_csv(output_filename, index=False)
    print(f"- CSV 저장 완료: {output_filename}")
    
    # 출력 파일 크기 확인
    output_size = os.path.getsize(output_filename)
    print(f"- 출력 파일 크기: {output_size / 1024:.2f} KB")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\n[요약]")
    print(f"- 처리된 행 수: {len(df)}")
    print(f"- 변경된 컬럼 수: {len(input_cols)}")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    print(f"- 저장 경로: {output_filename}")
    
    # 보고서 생성
    report = generate_report(df, input_cols, output_cols,
                           data.name if hasattr(data, 'name') else data,
                           output_filename, input_size, output_size,
                           elapsed_time, validation_info)
    
    return output_filename, report
