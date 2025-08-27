import pandas as pd
import time
import os
from datetime import datetime

def generate_report(df: pd.DataFrame, operands: list, operators: list, column_name: str,
                  input_filename: str, output_filename: str, input_size: int, output_size: int,
                  elapsed_time: float, total_operations: int) -> str:
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

## 6. 작업 상태
- **상태**: 성공
- **처리 결과**: 산술 연산이 성공적으로 수행됨
"""
    return report

def solution(data: object, output_filename: str, operands, operators, column_name):
    """
    주어진 csv 데이터셋에서 numeric 필드에 다양한 산술 연산을 수행하는 알고리즘

    Parameters:
        data (str): CSV 파일 경로. 알고리즘 내에서 pandas의 read_csv로 읽어와야 합니다.
        operands (list of str): 산술 연산에 적용할 피연산자들의 리스트.
        operators (list of str): 산술 연산자들의 리스트.
        column_name (str): 산술 연산 결과가 기록될 컬럼의 이름.
        output_filename (str): 결과를 저장할 CSV 파일의 이름.

    Returns:
        tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] 산술 연산 작업을 시작합니다.")
    print(f"- 연산식: {' '.join([f'{operands[i]} {operators[i]}' if i < len(operators) else operands[i] for i in range(len(operands))])}")
    print(f"- 결과 컬럼명: {column_name}")
    
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
    missing_operands = [op for op in operands if op not in df.columns]
    if missing_operands:
        raise ValueError(f"다음 피연산자 컬럼이 존재하지 않습니다: {missing_operands}")
    
    print("- 모든 피연산자 컬럼이 존재합니다.")
    
    # 산술 연산 수행
    print("\n[3/4] 산술 연산을 수행합니다...")
    result = df[operands[0]]
    total_operations = len(operators)
    
    for i, (operator, operand) in enumerate(zip(operators, operands[1:]), 1):
        print(f"- {i}/{total_operations}번째 연산: {result.name} {operator} {operand}")
        
        if operator == '+':
            result = result + df[operand]
        elif operator == '-':
            result = result - df[operand]
        elif operator == '*':
            result = result * df[operand]
        elif operator == '/':
            result = result / df[operand]
        elif operator == '//':
            result = result // df[operand]
        elif operator == '%':
            result = result % df[operand]
        elif operator == '**':
            result = result ** df[operand]
        else:
            raise ValueError(f"잘못된 연산자: {operator}. 허용되는 연산자: +, -, *, /, //, %, **")
    
    # 결과를 새로운 컬럼에 저장
    print(f"\n[4/4] 결과를 저장합니다...")
    df[column_name] = result
    print(f"- 새 컬럼 '{column_name}'이(가) 추가되었습니다.")
    
    # 결과를 CSV 파일로 저장
    df.to_csv(output_filename, index=False)
    
    # 출력 파일 크기 확인
    output_size = os.path.getsize(output_filename)
    print(f"- 출력 파일 크기: {output_size / 1024:.2f} KB")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\n[요약]")
    print(f"- 처리된 행 수: {len(df)}")
    print(f"- 수행된 연산 수: {total_operations}")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    print(f"- 저장 경로: {output_filename}")
    
    # 보고서 생성
    report = generate_report(df, operands, operators, column_name,
                           data.name if hasattr(data, 'name') else data,
                           output_filename, input_size, output_size,
                           elapsed_time, total_operations)
    
    return output_filename, report