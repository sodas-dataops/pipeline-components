import pandas as pd
import pymysql
from sqlalchemy import create_engine
import logging
from datetime import datetime
from tabulate import tabulate
import gc

def create_connection_string(mysql_config):
    """MySQL 연결 문자열을 생성합니다."""
    charset = mysql_config.get('charset', 'utf8mb4')
    return f"mysql+pymysql://{mysql_config['username']}:{mysql_config['password']}@{mysql_config['host']}:{mysql_config['port']}/{mysql_config['database']}?charset={charset}"

def stream_sql_to_csv(mysql_config, sql_query, output_file_path, chunksize=10000):
    """MySQL에서 SQL 쿼리를 chunk 단위로 실행하고 결과를 CSV로 스트리밍 저장합니다."""
    connection_string = create_connection_string(mysql_config)
    engine = create_engine(connection_string)
    
    total_rows = 0
    total_nulls = None
    dtypes = None
    columns = None
    first_chunk = True
    sample_rows = []
    chunk_count = 0
    
    print(f"SQL 쿼리 실행 중: {sql_query}")
    print(f"Chunk 크기: {chunksize:,} 행")
    
    for chunk in pd.read_sql_query(sql_query, engine, chunksize=chunksize):
        chunk_count += 1
        chunk_rows = len(chunk)
        total_rows += chunk_rows
        
        # 진행률 표시
        print(f"Chunk {chunk_count}: {chunk_rows:,} 행 처리 중... (총 {total_rows:,} 행)")
        
        if first_chunk:
            chunk.to_csv(output_file_path, index=False, mode='w', encoding='utf-8')
            columns = list(chunk.columns)
            dtypes = chunk.dtypes
            # 샘플 데이터 저장 (최대 5개만)
            sample_rows = chunk.head(5).values.tolist()
            first_chunk = False
        else:
            chunk.to_csv(output_file_path, index=False, mode='a', header=False, encoding='utf-8')
            # 샘플 데이터가 5개 미만이면 추가 (메모리 절약)
            if len(sample_rows) < 5:
                remain = 5 - len(sample_rows)
                sample_rows.extend(chunk.head(remain).values.tolist())
        
        # 누적 null 통계 (메모리 효율적으로)
        nulls = chunk.isnull().sum()
        if total_nulls is None:
            total_nulls = nulls
        else:
            total_nulls += nulls
        
        # 메모리 정리 (chunk 처리 후 즉시 해제)
        del chunk
        gc.collect()
    
    print(f"처리 완료: 총 {chunk_count}개 chunk, {total_rows:,} 행")
    
    return {
        'total_rows': total_rows,
        'columns': columns,
        'dtypes': dtypes,
        'total_nulls': total_nulls,
        'sample_rows': sample_rows,
        'chunk_count': chunk_count
    }

def generate_report(stats, sql_query, execution_time):
    """실행 결과에 대한 보고서를 생성합니다."""
    columns = stats['columns']
    dtypes = stats['dtypes']
    total_rows = stats['total_rows']
    total_nulls = stats['total_nulls']
    sample_rows = stats['sample_rows']
    chunk_count = stats.get('chunk_count', 0)
    
    report = f"""# MySQL to CSV 실행 보고서

## 실행 정보
- 실행 시간: {execution_time}
- SQL 쿼리: {sql_query}
- 처리된 Chunk 수: {chunk_count}

## 결과 통계
- 총 행 수: {total_rows:,}
- 총 컬럼 수: {len(columns) if columns else 0}
- 컬럼 목록: {', '.join(columns) if columns else ''}

## 데이터 샘플
"""
    # 샘플 데이터
    if sample_rows and columns:
        report += "\n### 처음 5행 데이터\n"
        report += tabulate(sample_rows, headers=columns, tablefmt="github")
    # 데이터 타입 정보
    if dtypes is not None:
        report += "\n\n### 컬럼 데이터 타입\n"
        for col in columns:
            report += f"- {col}: {dtypes[col]}\n"
    # null 통계
    if total_nulls is not None:
        report += f"\n### 데이터 품질 정보 (null 값 통계)\n"
        for col in columns:
            null_count = total_nulls[col]
            null_percentage = (null_count / total_rows) * 100 if total_rows > 0 else 0
            report += f"- {col}: {null_count:,}개 null 값 ({null_percentage:.2f}%)\n"
    return report

def solution(mysql_config, sql_query, output_file_path, chunksize=10000):
    """메인 솔루션 함수 (chunk 단위 스트리밍 저장)"""
    start_time = datetime.now()
    try:
        stats = stream_sql_to_csv(mysql_config, sql_query, output_file_path, chunksize=chunksize)
        execution_time = datetime.now() - start_time
        report_content = generate_report(stats, sql_query, execution_time)
        return output_file_path, report_content
    except Exception as e:
        print(f"솔루션 실행 중 오류 발생: {e}")
        raise 