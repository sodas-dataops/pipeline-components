import pandas as pd
import time
import os
from datetime import datetime

def validate_target_columns(df: pd.DataFrame, target_cols: list) -> dict:
    """
    대상 컬럼들의 존재 여부를 검증하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 검증할 DataFrame
    - target_cols (list): 검증할 대상 컬럼 목록
    
    Returns:
    - dict: 검증 결과 정보
    """
    validation_result = {
        'is_valid': True,
        'errors': [],
        'missing_columns': [],
        'existing_columns': []
    }
    
    if not target_cols:
        validation_result['errors'].append("대상 컬럼 목록이 비어있습니다.")
        validation_result['is_valid'] = False
        return validation_result
    
    for col in target_cols:
        if col not in df.columns:
            validation_result['errors'].append(f"대상 컬럼 '{col}'이 존재하지 않습니다.")
            validation_result['missing_columns'].append(col)
            validation_result['is_valid'] = False
        else:
            validation_result['existing_columns'].append(col)
    
    return validation_result

def validate_optional_columns(df: pd.DataFrame, optional_cols: list) -> dict:
    """
    선택적 컬럼들의 존재 여부를 검증하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 검증할 DataFrame
    - optional_cols (list): 검증할 선택적 컬럼 목록
    
    Returns:
    - dict: 검증 결과 정보
    """
    validation_result = {
        'is_valid': True,
        'errors': [],
        'warnings': [],
        'missing_columns': [],
        'existing_columns': []
    }
    
    if not optional_cols:
        return validation_result
    
    for col in optional_cols:
        if col not in df.columns:
            validation_result['warnings'].append(f"선택적 컬럼 '{col}'이 존재하지 않습니다. 건너뜁니다.")
            validation_result['missing_columns'].append(col)
        else:
            validation_result['existing_columns'].append(col)
    
    return validation_result

def validate_new_column_name(df: pd.DataFrame, new_col_name: str, target_cols: list, optional_cols: list) -> dict:
    """
    새 컬럼명의 유효성을 검증하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 검증할 DataFrame
    - new_col_name (str): 새 컬럼명
    - target_cols (list): 대상 컬럼 목록
    - optional_cols (list): 선택적 컬럼 목록
    
    Returns:
    - dict: 검증 결과 정보
    """
    validation_result = {
        'is_valid': True,
        'errors': [],
        'warnings': []
    }
    
    # 컬럼명이 비어있는지 확인
    if not new_col_name or not new_col_name.strip():
        validation_result['errors'].append("새 컬럼명이 비어있습니다.")
        validation_result['is_valid'] = False
        return validation_result
    
    new_col_name = new_col_name.strip()
    
    # 컬럼명 패턴 검증 (영문자, 숫자, 언더스코어만 허용)
    if not new_col_name.replace('_', '').isalnum() or new_col_name[0].isdigit():
        validation_result['errors'].append(
            f"새 컬럼명 '{new_col_name}'이 유효하지 않습니다. 영문자, 숫자, 언더스코어만 허용되며 숫자로 시작할 수 없습니다."
        )
        validation_result['is_valid'] = False
    
    # 기존 컬럼과의 충돌 확인
    if new_col_name in df.columns:
        validation_result['errors'].append(
            f"새 컬럼명 '{new_col_name}'이 기존 컬럼과 충돌합니다."
        )
        validation_result['is_valid'] = False
    
    # 대상 컬럼과의 중복 확인
    if new_col_name in target_cols:
        validation_result['warnings'].append(
            f"새 컬럼명 '{new_col_name}'이 대상 컬럼과 동일합니다."
        )
    
    # 선택적 컬럼과의 중복 확인
    if optional_cols and new_col_name in optional_cols:
        validation_result['warnings'].append(
            f"새 컬럼명 '{new_col_name}'이 선택적 컬럼과 동일합니다."
        )
    
    return validation_result

def validate_delimiter(delimiter: str) -> dict:
    """
    구분자의 유효성을 검증하는 함수.
    
    Parameters:
    - delimiter (str): 검증할 구분자
    
    Returns:
    - dict: 검증 결과 정보
    """
    validation_result = {
        'is_valid': True,
        'errors': [],
        'warnings': []
    }
    
    if delimiter is None:
        validation_result['errors'].append("구분자가 지정되지 않았습니다.")
        validation_result['is_valid'] = False
        return validation_result
    
    # 구분자가 너무 긴 경우 경고
    if len(delimiter) > 10:
        validation_result['warnings'].append("구분자가 너무 깁니다. 일반적으로 1-3자리 구분자를 사용합니다.")
    
    # 특수 문자 사용에 대한 경고
    special_chars = ['\n', '\r', '\t']
    if any(char in delimiter for char in special_chars):
        validation_result['warnings'].append("구분자에 특수 문자(개행, 탭 등)가 포함되어 있습니다.")
    
    return validation_result

def validate_column_concat_parameters(df: pd.DataFrame, target_cols: list, optional_cols: list, 
                                    new_col_name: str, delimiter: str) -> dict:
    """
    컬럼 연결 파라미터의 전체적인 유효성을 검증하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 검증할 DataFrame
    - target_cols (list): 대상 컬럼 목록
    - optional_cols (list): 선택적 컬럼 목록
    - new_col_name (str): 새 컬럼명
    - delimiter (str): 구분자
    
    Returns:
    - dict: 검증 결과 정보
    """
    validation_result = {
        'is_valid': True,
        'errors': [],
        'warnings': [],
        'target_validation': None,
        'optional_validation': None,
        'new_col_validation': None,
        'delimiter_validation': None
    }
    
    # 대상 컬럼 검증
    target_validation = validate_target_columns(df, target_cols)
    validation_result['target_validation'] = target_validation
    
    if not target_validation['is_valid']:
        validation_result['errors'].extend(target_validation['errors'])
        validation_result['is_valid'] = False
    
    # 선택적 컬럼 검증
    optional_validation = validate_optional_columns(df, optional_cols or [])
    validation_result['optional_validation'] = optional_validation
    
    if optional_validation['warnings']:
        validation_result['warnings'].extend(optional_validation['warnings'])
    
    # 새 컬럼명 검증
    new_col_validation = validate_new_column_name(df, new_col_name, target_cols, optional_cols or [])
    validation_result['new_col_validation'] = new_col_validation
    
    if not new_col_validation['is_valid']:
        validation_result['errors'].extend(new_col_validation['errors'])
        validation_result['is_valid'] = False
    
    if new_col_validation['warnings']:
        validation_result['warnings'].extend(new_col_validation['warnings'])
    
    # 구분자 검증
    delimiter_validation = validate_delimiter(delimiter)
    validation_result['delimiter_validation'] = delimiter_validation
    
    if not delimiter_validation['is_valid']:
        validation_result['errors'].extend(delimiter_validation['errors'])
        validation_result['is_valid'] = False
    
    if delimiter_validation['warnings']:
        validation_result['warnings'].extend(delimiter_validation['warnings'])
    
    return validation_result

def generate_report(df: pd.DataFrame, target_cols: list, optional_cols: list, delimiter: str, 
                  new_col_name: str, input_filename: str, output_filename: str, 
                  input_size: int, output_size: int, elapsed_time: float, validation_info: dict = None) -> str:
    """
    작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - target_cols (list): 연결 대상 컬럼 목록
    - optional_cols (list): 선택적 컬럼 목록
    - delimiter (str): 구분자
    - new_col_name (str): 새 컬럼 이름
    - input_filename (str): 입력 파일 경로
    - output_filename (str): 출력 파일 경로
    - input_size (int): 입력 파일 크기 (bytes)
    - output_size (int): 출력 파일 크기 (bytes)
    - elapsed_time (float): 소요 시간 (초)
    - validation_info (dict): 데이터 검증 정보
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    report = f"""# CSV 컬럼 연결 작업 보고서

## 1. 작업 개요
- **작업 유형**: CSV 컬럼 연결
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **입력 파일**: {input_filename}
- **파일 크기**: {input_size / 1024:.2f} KB
- **행 수**: {len(df)}
- **기존 컬럼 수**: {len(df.columns)}
- **기존 컬럼**: {', '.join(df.columns)}

## 3. 연결 설정
- **대상 컬럼**: {', '.join(target_cols)}
- **선택적 컬럼**: {', '.join(optional_cols)}
- **구분자**: '{delimiter}'
- **새 컬럼 이름**: '{new_col_name}'

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
        report += f"- **대상 컬럼 검증**: {'성공' if validation_info.get('target_validation', {}).get('is_valid', True) else '실패'}\n"
        report += f"- **선택적 컬럼 검증**: {'성공' if validation_info.get('optional_validation', {}).get('is_valid', True) else '실패'}\n"
        report += f"- **새 컬럼명 검증**: {'성공' if validation_info.get('new_col_validation', {}).get('is_valid', True) else '실패'}\n"
        report += f"- **구분자 검증**: {'성공' if validation_info.get('delimiter_validation', {}).get('is_valid', True) else '실패'}\n"
        
        # 누락된 대상 컬럼 정보
        if validation_info.get('target_validation', {}).get('missing_columns'):
            report += "- **누락된 대상 컬럼**:\n"
            for col in validation_info['target_validation']['missing_columns']:
                report += f"  - {col}\n"
        
        # 누락된 선택적 컬럼 정보
        if validation_info.get('optional_validation', {}).get('missing_columns'):
            report += "- **누락된 선택적 컬럼**:\n"
            for col in validation_info['optional_validation']['missing_columns']:
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
- **처리 결과**: 컬럼이 성공적으로 연결됨
"""
    return report

def solution(input_filename: str, output_filename: str, target_cols: list, optional_cols: list = None, 
            delimiter: str = ',', new_col_name: str = 'concatenated'):
    """
    CSV 파일의 지정된 컬럼들을 연결하여 새로운 컬럼을 만드는 함수.
    
    Parameters:
    - input_filename (str): 입력 CSV 파일 경로
    - output_filename (str): 출력 CSV 파일 경로
    - target_cols (list): 연결할 필수 컬럼 목록
    - optional_cols (list): 연결할 선택적 컬럼 목록 (기본값: None)
    - delimiter (str): 컬럼 연결 시 사용할 구분자 (기본값: ',')
    - new_col_name (str): 새로 생성할 컬럼의 이름 (기본값: 'concatenated')
    
    Returns:
    - tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] CSV 컬럼 연결 작업을 시작합니다.")
    print(f"- 대상 컬럼: {', '.join(target_cols)}")
    print(f"- 선택적 컬럼: {', '.join(optional_cols) if optional_cols else '없음'}")
    print(f"- 구분자: '{delimiter}'")
    print(f"- 새 컬럼명: '{new_col_name}'")
    
    # CSV 파일 로드
    print("\n[1/4] CSV 파일을 로드합니다...")
    try:
        df = pd.read_csv(input_filename)
        print(f"- CSV 데이터 로드 완료: {len(df)}행 x {len(df.columns)}열")
        print(f"- 기존 컬럼: {', '.join(df.columns)}")
    except (FileNotFoundError, PermissionError, UnicodeDecodeError, pd.errors.EmptyDataError) as e:
        raise ValueError(f"CSV 파일 로드 실패: {str(e)}")
    
    # 입력 파일 크기 확인
    input_size = os.path.getsize(input_filename)
    print(f"- 입력 파일 크기: {input_size / 1024:.2f} KB")
    
    # 파라미터 유효성 검증
    print("\n[2/4] 파라미터를 검증합니다...")
    validation_info = validate_column_concat_parameters(df, target_cols, optional_cols, new_col_name, delimiter)
    
    if not validation_info['is_valid']:
        error_msg = "파라미터 검증 실패:\n" + "\n".join(validation_info['errors'])
        raise ValueError(error_msg)
    
    print("- 모든 파라미터가 유효합니다.")
    
    # 경고사항 출력
    if validation_info['warnings']:
        print("⚠️  경고사항:")
        for warning in validation_info['warnings']:
            print(f"  - {warning}")
    
    # 컬럼 연결
    print("\n[3/4] 컬럼을 연결합니다...")
    
    # 실제 연결할 컬럼 목록 구성
    final_target_cols = target_cols.copy()
    if optional_cols:
        available_optional_cols = [col for col in optional_cols if col in df.columns]
        if available_optional_cols:
            print(f"- 사용 가능한 선택적 컬럼: {', '.join(available_optional_cols)}")
            final_target_cols.extend(available_optional_cols)
    
    print(f"- 연결할 컬럼: {', '.join(final_target_cols)}")
    df[new_col_name] = df[final_target_cols].astype(str).agg(delimiter.join, axis=1)
    print(f"- 새 컬럼 '{new_col_name}' 생성 완료")
    
    # CSV로 저장
    print("\n[4/4] 결과를 CSV로 저장합니다...")
    try:
        df.to_csv(output_filename, index=False)
        print(f"- CSV 저장 완료: {output_filename}")
    except (PermissionError, OSError, UnicodeEncodeError) as e:
        raise IOError(f"CSV 저장 실패: {str(e)}")
    
    # 출력 파일 크기 확인
    output_size = os.path.getsize(output_filename)
    print(f"- 출력 파일 크기: {output_size / 1024:.2f} KB")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\n[요약]")
    print(f"- 입력 파일: {input_filename}")
    print(f"- 출력 파일: {output_filename}")
    print(f"- 처리된 행 수: {len(df)}")
    print(f"- 연결된 컬럼 수: {len(final_target_cols)}")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    
    # 보고서 생성
    report = generate_report(df, final_target_cols, optional_cols or [], delimiter, new_col_name,
                           input_filename, output_filename, input_size, output_size, elapsed_time, validation_info)
    
    return output_filename, report