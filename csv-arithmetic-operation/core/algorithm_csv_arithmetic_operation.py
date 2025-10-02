import pandas as pd
import time
import os
import numpy as np
from datetime import datetime

def validate_operands_existence(df: pd.DataFrame, operands: list) -> dict:
    """
    피연산자 컬럼들의 존재 여부를 검증하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 검증할 DataFrame
    - operands (list): 검증할 피연산자 컬럼 목록
    
    Returns:
    - dict: 검증 결과 정보
    """
    validation_result = {
        'is_valid': True,
        'errors': [],
        'missing_columns': []
    }
    
    for operand in operands:
        if operand not in df.columns:
            validation_result['errors'].append(f"피연산자 컬럼 '{operand}'이 존재하지 않습니다.")
            validation_result['missing_columns'].append(operand)
            validation_result['is_valid'] = False
    
    return validation_result

def validate_column_name_conflict(df: pd.DataFrame, column_name: str) -> dict:
    """
    결과 컬럼명이 기존 컬럼과 중복되는지 검증하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 검증할 DataFrame
    - column_name (str): 검증할 컬럼명
    
    Returns:
    - dict: 검증 결과 정보
    """
    validation_result = {
        'is_valid': True,
        'error': None
    }
    
    if column_name in df.columns:
        validation_result['is_valid'] = False
        validation_result['error'] = f"결과 컬럼명 '{column_name}'이 이미 존재합니다. 다른 이름을 사용해주세요."
    
    return validation_result

def perform_arithmetic_operation_with_error_handling(df: pd.DataFrame, operands: list, operators: list, 
                                                   column_name: str, strict_mode: bool = True) -> dict:
    """
    산술 연산을 수행하면서 실패 시 처리하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 연산할 DataFrame
    - operands (list): 피연산자 컬럼 목록
    - operators (list): 연산자 목록
    - column_name (str): 결과 컬럼명
    - strict_mode (bool): 엄격 모드 여부
    
    Returns:
    - dict: 연산 결과 및 실패 정보
    """
    result_info = {
        'success': True,
        'result_series': None,
        'operation_failures': [],
        'total_operations': len(operators),
        'successful_operations': 0,
        'failed_operations': 0
    }
    
    try:
        # 첫 번째 피연산자로 시작
        result = df[operands[0]].copy()
        result_info['successful_operations'] = 1
        
        # 각 연산 수행
        for i, (operator, operand) in enumerate(zip(operators, operands[1:]), 1):
            try:
                # 연산 수행 전에 데이터 타입 검사
                left_series = result
                right_series = df[operand]
                
                # 숫자 타입이 아닌 값들이 있는지 확인
                left_numeric = pd.to_numeric(left_series, errors='coerce')
                right_numeric = pd.to_numeric(right_series, errors='coerce')
                
                # 숫자로 변환할 수 없는 값들이 있는지 확인
                left_non_numeric = left_series.isna() | left_numeric.isna()
                right_non_numeric = right_series.isna() | right_numeric.isna()
                
                if left_non_numeric.any() or right_non_numeric.any():
                    # 숫자가 아닌 값이 있으면 연산 실패로 처리
                    raise TypeError("숫자가 아닌 값으로 인한 연산 실패")
                
                # 연산 수행
                if operator == '+':
                    result = left_numeric + right_numeric
                elif operator == '-':
                    result = left_numeric - right_numeric
                elif operator == '*':
                    result = left_numeric * right_numeric
                elif operator == '/':
                    result = left_numeric / right_numeric
                elif operator == '//':
                    result = left_numeric // right_numeric
                elif operator == '%':
                    result = left_numeric % right_numeric
                elif operator == '**':
                    result = left_numeric ** right_numeric
                else:
                    raise ValueError(f"지원하지 않는 연산자: {operator}")
                
                result_info['successful_operations'] += 1
                
            except Exception as e:
                # 연산 실패 처리
                failure_info = {
                    'operation_index': i,
                    'operator': operator,
                    'operand': operand,
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'affected_rows': []
                }
                
                # 실패한 행들 찾기
                for idx in range(len(df)):
                    try:
                        left_val = result.iloc[idx]
                        right_val = df[operand].iloc[idx]
                        
                        # 숫자로 변환 시도
                        left_num = pd.to_numeric(left_val, errors='coerce')
                        right_num = pd.to_numeric(right_val, errors='coerce')
                        
                        # 숫자로 변환할 수 없는 경우 실패로 처리
                        if pd.isna(left_num) or pd.isna(right_num):
                            failure_info['affected_rows'].append({
                                'row_index': idx,
                                'left_value': left_val,
                                'right_value': right_val
                            })
                            continue
                        
                        # 연산 수행 시도
                        if operator == '+':
                            _ = left_num + right_num
                        elif operator == '-':
                            _ = left_num - right_num
                        elif operator == '*':
                            _ = left_num * right_num
                        elif operator == '/':
                            _ = left_num / right_num
                        elif operator == '//':
                            _ = left_num // right_num
                        elif operator == '%':
                            _ = left_num % right_num
                        elif operator == '**':
                            _ = left_num ** right_num
                    except Exception:
                        failure_info['affected_rows'].append({
                            'row_index': idx,
                            'left_value': result.iloc[idx] if idx < len(result) else None,
                            'right_value': df[operand].iloc[idx] if idx < len(df) else None
                        })
                
                result_info['operation_failures'].append(failure_info)
                result_info['failed_operations'] += 1
                
                if strict_mode:
                    # 엄격 모드: 오류 발생
                    error_msg = f"연산 실패: {operands[i-1]} {operator} {operand}\n"
                    error_msg += f"오류: {type(e).__name__}: {str(e)}\n"
                    error_msg += f"영향받은 행 수: {len(failure_info['affected_rows'])}"
                    raise ValueError(error_msg)
                else:
                    # 비엄격 모드: 빈 값으로 처리
                    print(f"⚠️  연산 실패: {operands[i-1]} {operator} {operand}")
                    print(f"   오류: {type(e).__name__}: {str(e)}")
                    print(f"   영향받은 행 수: {len(failure_info['affected_rows'])}")
                    
                    # 실패한 연산 결과를 NaN으로 설정
                    result = pd.Series([np.nan] * len(df), index=df.index)
                    break
        
        result_info['result_series'] = result
        
    except Exception as e:
        result_info['success'] = False
        if strict_mode:
            raise e
    
    return result_info

def generate_report(df: pd.DataFrame, operands: list, operators: list, column_name: str,
                  input_filename: str, output_filename: str, input_size: int, output_size: int,
                  elapsed_time: float, total_operations: int, validation_info: dict = None, 
                  operation_info: dict = None) -> str:
    """
    작업 보고서를 생성하는 함수.
    
    Parameters:
    - df (pd.DataFrame): 처리된 DataFrame
    - operands (list): 피연산자 목록
    - operators (list): 연산자 목록
    - column_name (str): 결과 컬럼 이름
    - input_filename (str): 입력 파일 경로
    - output_filename (str): 출력 파일 경로
    - input_size (int): 입력 파일 크기 (bytes)
    - output_size (int): 출력 파일 크기 (bytes)
    - elapsed_time (float): 소요 시간 (초)
    - total_operations (int): 수행된 연산 수
    - validation_info (dict): 데이터 검증 정보
    - operation_info (dict): 연산 수행 정보
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    report = f"""# CSV 산술 연산 작업 보고서

## 1. 작업 개요
- **작업 유형**: CSV 산술 연산
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초

## 2. 입력 데이터
- **입력 파일**: {input_filename}
- **파일 크기**: {input_size / 1024:.2f} KB
- **행 수**: {len(df)}
- **기존 컬럼 수**: {len(df.columns)}
- **기존 컬럼**: {', '.join(df.columns)}

## 3. 연산 설정
- **피연산자**: {', '.join(operands)}
- **연산자**: {', '.join(operators)}
- **연산식**: {' '.join([f'{operands[i]} {operators[i]}' if i < len(operators) else operands[i] for i in range(len(operands))])}
- **결과 컬럼**: '{column_name}'

## 4. 처리 결과
- **출력 파일**: {output_filename}
- **파일 크기**: {output_size / 1024:.2f} KB
- **새 컬럼 수**: {len(df.columns)}
- **새 컬럼**: {', '.join(df.columns)}

## 5. 성능 지표
- **처리 속도**: {input_size / elapsed_time / 1024:.2f} KB/s
- **압축률**: {(1 - output_size / input_size) * 100:.2f}%
- **처리 효율**: {len(df) / elapsed_time:.2f} 행/초
- **연산 효율**: {total_operations / elapsed_time:.2f} 연산/초

## 6. 데이터 검증 결과
"""
    
    # 검증 정보가 있는 경우 추가
    if validation_info:
        report += f"- **피연산자 존재 검증**: {'성공' if validation_info.get('operands_validation', {}).get('is_valid', True) else '실패'}\n"
        report += f"- **컬럼명 중복 검증**: {'성공' if validation_info.get('column_name_validation', {}).get('is_valid', True) else '실패'}\n"
        
        # 누락된 컬럼 정보
        if validation_info.get('operands_validation', {}).get('missing_columns'):
            report += "- **누락된 컬럼**:\n"
            for col in validation_info['operands_validation']['missing_columns']:
                report += f"  - {col}\n"
    else:
        report += "- **데이터 검증**: 수행되지 않음\n"
    
    # 연산 수행 정보가 있는 경우 추가
    if operation_info:
        report += f"- **연산 성공률**: {operation_info.get('successful_operations', 0)}/{operation_info.get('total_operations', 0)} ({operation_info.get('successful_operations', 0)/max(operation_info.get('total_operations', 1), 1)*100:.1f}%)\n"
        
        # 연산 실패 정보
        if operation_info.get('operation_failures'):
            report += "- **연산 실패 정보**:\n"
            for failure in operation_info['operation_failures']:
                report += f"  - 연산 {failure['operation_index']}: {failure['operator']} {failure['operand']}\n"
                report += f"    오류: {failure['error_type']}: {failure['error_message']}\n"
                report += f"    영향받은 행 수: {len(failure['affected_rows'])}\n"
                
                # 처음 5개 실패 행의 상세 정보
                if failure['affected_rows']:
                    report += f"    실패 행 예시 (최대 5개):\n"
                    for row_info in failure['affected_rows'][:5]:
                        report += f"      - 행 {row_info['row_index']}: {row_info['left_value']} {failure['operator']} {row_info['right_value']}\n"
    else:
        report += "- **연산 수행 정보**: 없음\n"

    report += """
## 7. 작업 상태
- **상태**: 성공
- **처리 결과**: 산술 연산이 성공적으로 수행됨
"""
    return report

def solution(data: object, output_filename: str, operands, operators, column_name, 
             strict_mode: bool = True):
    """
    주어진 csv 데이터셋에서 다양한 산술 연산을 수행하는 알고리즘

    Parameters:
        data (str): CSV 파일 경로. 알고리즘 내에서 pandas의 read_csv로 읽어와야 합니다.
        operands (list of str): 산술 연산에 적용할 피연산자들의 리스트.
        operators (list of str): 산술 연산자들의 리스트.
        column_name (str): 산술 연산 결과가 기록될 컬럼의 이름.
        output_filename (str): 결과를 저장할 CSV 파일의 이름.
        strict_mode (bool): 엄격 모드 여부 (True: 오류 시 중단, False: 빈 값으로 처리)

    Returns:
        tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] 산술 연산 작업을 시작합니다.")
    print(f"- 연산식: {' '.join([f'{operands[i]} {operators[i]}' if i < len(operators) else operands[i] for i in range(len(operands))])}")
    print(f"- 결과 컬럼명: {column_name}")
    print(f"- 엄격 모드: {'활성화' if strict_mode else '비활성화'}")
    
    # CSV 파일 읽기
    print("\n[1/4] CSV 파일을 로드합니다...")
    df = pd.read_csv(data)
    print(f"- 총 {len(df)}개의 행이 로드되었습니다.")
    print(f"- 기존 컬럼: {', '.join(df.columns)}")
    
    # 입력 파일 크기 확인
    input_size = len(data.getvalue().encode('utf-8'))
    print(f"- 입력 파일 크기: {input_size / 1024:.2f} KB")
    
    # 피연산자와 연산자의 개수가 유효한지 검사
    print("\n[2/4] 연산자와 피연산자를 검증합니다...")
    if len(operands) != len(operators) + 1:
        raise ValueError("피연산자의 개수가 연산자의 개수보다 1개 더 많아야 합니다.")
    
    # 피연산자 컬럼 존재 여부 확인
    operands_validation = validate_operands_existence(df, operands)
    if not operands_validation['is_valid']:
        error_msg = "피연산자 컬럼 검증 실패:\n" + "\n".join(operands_validation['errors'])
        raise ValueError(error_msg)
    
    print("- 모든 피연산자 컬럼이 존재합니다.")
    
    # 결과 컬럼명 중복 검증
    print("\n[3/4] 결과 컬럼명을 검증합니다...")
    column_name_validation = validate_column_name_conflict(df, column_name)
    if not column_name_validation['is_valid']:
        if strict_mode:
            raise ValueError(column_name_validation['error'])
        else:
            print(f"⚠️  경고: {column_name_validation['error']}")
    
    # 검증 결과 저장
    validation_info = {
        'operands_validation': operands_validation,
        'column_name_validation': column_name_validation
    }
    
    # 산술 연산 수행
    print("\n[4/4] 산술 연산을 수행합니다...")
    operation_info = perform_arithmetic_operation_with_error_handling(
        df, operands, operators, column_name, strict_mode
    )
    
    # 결과를 새로운 컬럼에 저장
    print(f"\n[저장] 결과를 저장합니다...")
    df[column_name] = operation_info['result_series']
    print(f"- 새 컬럼 '{column_name}'이(가) 추가되었습니다.")
    
    # 연산 성공률 출력
    success_rate = operation_info['successful_operations'] / max(operation_info['total_operations'], 1) * 100
    print(f"- 연산 성공률: {operation_info['successful_operations']}/{operation_info['total_operations']} ({success_rate:.1f}%)")
    
    if operation_info['operation_failures']:
        print(f"- 연산 실패: {len(operation_info['operation_failures'])}개")
    
    # 결과를 CSV 파일로 저장
    df.to_csv(output_filename, index=False)
    
    # 출력 파일 크기 확인
    output_size = os.path.getsize(output_filename)
    print(f"- 출력 파일 크기: {output_size / 1024:.2f} KB")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\n[요약]")
    print(f"- 처리된 행 수: {len(df)}")
    print(f"- 수행된 연산 수: {operation_info['total_operations']}")
    print(f"- 성공한 연산 수: {operation_info['successful_operations']}")
    print(f"- 실패한 연산 수: {operation_info['failed_operations']}")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    print(f"- 저장 경로: {output_filename}")
    
    # 보고서 생성
    report = generate_report(df, operands, operators, column_name,
                           data.name if hasattr(data, 'name') else data,
                           output_filename, input_size, output_size,
                           elapsed_time, operation_info['total_operations'], 
                           validation_info, operation_info)
    
    return output_filename, report