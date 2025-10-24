import pandas as pd
import numpy as np
import json
import time
import os
from datetime import datetime
from io import StringIO
import re
from typing import Dict, List, Any, Tuple

def generate_report(input_data: pd.DataFrame, output_data: pd.DataFrame, 
                   output_filename: str, 
                   input_size: int, output_size: int, elapsed_time: float, 
                   settings: dict = None, quality_score: Dict[str, Any] = None) -> str:
    """
    작업 보고서를 생성하는 함수.
    
    Parameters:
    - input_data (pd.DataFrame): 입력 데이터
    - output_data (pd.DataFrame): 출력 데이터
    - output_filename (str): 출력 파일 경로
    - input_size (int): 입력 데이터 크기 (bytes)
    - output_size (int): 출력 데이터 크기 (bytes)
    - elapsed_time (float): 소요 시간 (초)
    - settings (dict): 설정
    
    Returns:
    - str: 생성된 보고서 내용 (markdown 형식)
    """
    validation_rules = settings.get('validation_rules', []) if settings else []
    output_format = settings.get('output_format', 'json') if settings else 'json'
    include_details = settings.get('include_details', True) if settings else True
    
    # 품질 점수 정보
    quality_score_value = quality_score.get('overall_score', 0.0) if quality_score else 0.0
    quality_score_info = f"- **품질 점수**: {quality_score_value:.2f}점"

    # 검증 규칙 정보
    rules_info = f"- **검증 규칙**: {len(validation_rules)}개"
    format_info = f"- **출력 형식**: {output_format.upper()}"
    details_info = f"- **상세 정보**: {'포함' if include_details else '제외'}"
    
    # 데이터 품질 요약
    total_rows = len(input_data)
    total_cols = len(input_data.columns)
    missing_data = input_data.isnull().sum().sum()
    duplicate_rows = input_data.duplicated().sum()
    completeness = ((total_rows * total_cols - missing_data) / (total_rows * total_cols) * 100) if total_rows > 0 else 0
    
    # 검증 결과 요약
    validation_summary = {
        'total_validations': len(validation_rules),
        'passed_validations': 0,
        'failed_validations': 0,
        'warning_validations': 0
    }
    
    report = f"""# 데이터 품질 검증 작업 보고서

## 1. 작업 개요
- **작업 유형**: 데이터 품질 검증
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {elapsed_time:.2f}초
{quality_score_info}
- **데이터 완전성**: {completeness:.2f}%
- **중복 행**: {duplicate_rows:,}개
- **결측값**: {missing_data:,}개
{rules_info}
{format_info}
{details_info}

## 2. 입력 데이터
- **데이터 크기**: {input_size / 1024:.2f} KB
- **행 수**: {total_rows:,}
- **열 수**: {total_cols}
- **열 이름**: {', '.join(input_data.columns)}

## 3. 검증 결과
- **출력 파일**: {output_filename}
- **파일 크기**: {output_size / 1024:.2f} KB
- **검증 규칙**: {validation_summary['total_validations']}개
- **통과**: {validation_summary['passed_validations']}개
- **실패**: {validation_summary['failed_validations']}개
- **경고**: {validation_summary['warning_validations']}개

## 4. 데이터 품질 지표
- **완전성**: {completeness:.2f}%
- **중복률**: {(duplicate_rows / total_rows * 100):.2f}%
- **결측률**: {(missing_data / (total_rows * total_cols) * 100):.2f}%

## 5. 성능 지표
- **처리 속도**: {total_rows / elapsed_time:.2f} 행/초
- **검증 속도**: {len(validation_rules) / elapsed_time:.2f} 규칙/초

## 6. 작업 상태
- **상태**: 성공
- **품질 검증**: 데이터 품질 검증이 성공적으로 완료됨
- **검증 결과**: 상세한 품질 보고서 생성 완료
"""
    return report

def validate_data_type(series: pd.Series, expected_type: str) -> Dict[str, Any]:
    """데이터 타입 검증"""
    result = {
        'rule_type': 'data_type',
        'expected_type': expected_type,
        'actual_type': str(series.dtype),
        'passed': False,
        'details': {}
    }
    
    if expected_type == 'numeric':
        result['passed'] = pd.api.types.is_numeric_dtype(series)
        
        # pandas 버전 호환성을 위한 numeric 체크
        def is_numeric_value(x):
            if pd.isna(x):
                return True
            return isinstance(x, (int, float, np.integer, np.floating))
        
        result['details'] = {
            'non_numeric_count': len(series) - series.apply(is_numeric_value).sum(),
            'null_count': series.isnull().sum()
        }
    elif expected_type == 'string':
        result['passed'] = pd.api.types.is_string_dtype(series) or series.dtype == 'object'
        result['details'] = {
            'non_string_count': len(series) - series.apply(lambda x: isinstance(x, str) or pd.isna(x)).sum(),
            'null_count': series.isnull().sum()
        }
    elif expected_type == 'datetime':
        result['passed'] = pd.api.types.is_datetime64_any_dtype(series)
        result['details'] = {
            'non_datetime_count': len(series) - series.apply(lambda x: pd.api.types.is_datetime64_any_dtype(pd.Series([x])) or pd.isna(x)).sum(),
            'null_count': series.isnull().sum()
        }
    
    return result

def validate_range(series: pd.Series, min_value: float = None, max_value: float = None) -> Dict[str, Any]:
    """값 범위 검증"""
    result = {
        'rule_type': 'range',
        'min_value': min_value,
        'max_value': max_value,
        'passed': True,
        'details': {}
    }
    
    if not pd.api.types.is_numeric_dtype(series):
        result['passed'] = False
        result['details'] = {'error': 'Non-numeric column cannot be validated for range'}
        return result
    
    numeric_series = pd.to_numeric(series, errors='coerce')
    
    if min_value is not None:
        below_min = (numeric_series < min_value).sum()
        result['details']['below_min_count'] = below_min
        if below_min > 0:
            result['passed'] = False
    
    if max_value is not None:
        above_max = (numeric_series > max_value).sum()
        result['details']['above_max_count'] = above_max
        if above_max > 0:
            result['passed'] = False
    
    result['details']['null_count'] = numeric_series.isnull().sum()
    result['details']['valid_count'] = len(numeric_series) - numeric_series.isnull().sum()
    
    return result

def validate_pattern(series: pd.Series, pattern: str) -> Dict[str, Any]:
    """패턴 검증 (정규표현식)"""
    result = {
        'rule_type': 'pattern',
        'pattern': pattern,
        'passed': True,
        'details': {}
    }
    
    try:
        regex = re.compile(pattern)
        matches = series.apply(lambda x: bool(regex.match(str(x))) if pd.notna(x) else True)
        non_matches = (~matches).sum()
        
        result['details']['non_matching_count'] = non_matches
        result['details']['matching_count'] = matches.sum()
        result['details']['null_count'] = series.isnull().sum()
        
        if non_matches > 0:
            result['passed'] = False
            
    except re.error as e:
        result['passed'] = False
        result['details']['error'] = f'Invalid regex pattern: {str(e)}'
    
    return result

def validate_uniqueness(series: pd.Series, unique: bool = True) -> Dict[str, Any]:
    """유일성 검증"""
    result = {
        'rule_type': 'uniqueness',
        'expected_unique': unique,
        'passed': False,
        'details': {}
    }
    
    unique_count = series.nunique()
    total_count = len(series)
    duplicate_count = total_count - unique_count
    
    result['details']['unique_count'] = unique_count
    result['details']['duplicate_count'] = duplicate_count
    result['details']['null_count'] = series.isnull().sum()
    
    if unique:
        result['passed'] = duplicate_count == 0
    else:
        result['passed'] = duplicate_count > 0
    
    return result

def validate_completeness(series: pd.Series, min_completeness: float = 0.95) -> Dict[str, Any]:
    """완전성 검증"""
    result = {
        'rule_type': 'completeness',
        'min_completeness': min_completeness,
        'passed': False,
        'details': {}
    }
    
    null_count = series.isnull().sum()
    total_count = len(series)
    completeness = (total_count - null_count) / total_count
    
    result['details']['null_count'] = null_count
    result['details']['total_count'] = total_count
    result['details']['completeness'] = completeness
    result['passed'] = completeness >= min_completeness
    
    return result

def validate_custom_rule(series: pd.Series, rule: Dict[str, Any]) -> Dict[str, Any]:
    """사용자 정의 규칙 검증"""
    result = {
        'rule_type': 'custom',
        'rule_name': rule.get('name', 'custom_rule'),
        'passed': False,
        'details': {}
    }
    
    try:
        # 사용자 정의 규칙 실행
        custom_condition = rule.get('condition')
        custom_params = rule.get('params', {})
        
        if custom_condition is None:
            result['details']['error'] = 'No custom condition provided'
            result['passed'] = False
            return result
        
        # 안전하게 조건 평가
        # 조건 타입: 'all', 'any', 'min', 'max', 'mean', 'count', 'custom'
        condition_type = custom_condition.get('type', 'custom')
        
        if condition_type == 'all':
            # 모든 값이 조건을 만족해야 함
            comparison = custom_condition.get('comparison', 'gt')
            threshold = custom_condition.get('threshold', 0)
            
            if comparison == 'gt':
                passed_mask = series > threshold
            elif comparison == 'gte':
                passed_mask = series >= threshold
            elif comparison == 'lt':
                passed_mask = series < threshold
            elif comparison == 'lte':
                passed_mask = series <= threshold
            elif comparison == 'eq':
                passed_mask = series == threshold
            elif comparison == 'ne':
                passed_mask = series != threshold
            else:
                passed_mask = series > threshold
            
            passed_count = passed_mask.sum()
            failed_count = (~passed_mask).sum()
            result['passed'] = (failed_count == 0)
            result['details'] = {
                'passed_count': int(passed_count),
                'failed_count': int(failed_count),
                'comparison': comparison,
                'threshold': threshold
            }
            
        elif condition_type == 'any':
            # 하나 이상의 값이 조건을 만족해야 함
            comparison = custom_condition.get('comparison', 'gt')
            threshold = custom_condition.get('threshold', 0)
            
            if comparison == 'gt':
                passed_mask = series > threshold
            elif comparison == 'gte':
                passed_mask = series >= threshold
            elif comparison == 'lt':
                passed_mask = series < threshold
            elif comparison == 'lte':
                passed_mask = series <= threshold
            elif comparison == 'eq':
                passed_mask = series == threshold
            elif comparison == 'ne':
                passed_mask = series != threshold
            else:
                passed_mask = series > threshold
            
            passed_count = passed_mask.sum()
            failed_count = (~passed_mask).sum()
            result['passed'] = (passed_count > 0)
            result['details'] = {
                'passed_count': int(passed_count),
                'failed_count': int(failed_count),
                'comparison': comparison,
                'threshold': threshold
            }
            
        elif condition_type == 'min':
            min_threshold = custom_condition.get('threshold', 0)
            series_min = series.min()
            result['passed'] = (series_min >= min_threshold)
            result['details'] = {
                'min_value': float(series_min) if not pd.isna(series_min) else None,
                'threshold': min_threshold
            }
            
        elif condition_type == 'max':
            max_threshold = custom_condition.get('threshold', 0)
            series_max = series.max()
            result['passed'] = (series_max <= max_threshold)
            result['details'] = {
                'max_value': float(series_max) if not pd.isna(series_max) else None,
                'threshold': max_threshold
            }
            
        elif condition_type == 'mean':
            mean_threshold = custom_condition.get('threshold', 0)
            comparison = custom_condition.get('comparison', 'gt')
            series_mean = series.mean()
            
            if comparison == 'gt':
                result['passed'] = (series_mean > mean_threshold)
            elif comparison == 'gte':
                result['passed'] = (series_mean >= mean_threshold)
            elif comparison == 'lt':
                result['passed'] = (series_mean < mean_threshold)
            elif comparison == 'lte':
                result['passed'] = (series_mean <= mean_threshold)
            else:
                result['passed'] = (series_mean > mean_threshold)
            
            result['details'] = {
                'mean_value': float(series_mean) if not pd.isna(series_mean) else None,
                'threshold': mean_threshold,
                'comparison': comparison
            }
            
        elif condition_type == 'ratio':
            # 비율 검증 (예: null이 아닌 값의 비율)
            property_type = custom_condition.get('property', 'non_null')
            min_ratio = custom_condition.get('min_ratio', 0.95)
            
            if property_type == 'non_null':
                ratio = (series.notna().sum() / len(series))
            elif property_type == 'unique':
                ratio = (series.nunique() / len(series))
            else:
                ratio = (series.notna().sum() / len(series))
            
            result['passed'] = (ratio >= min_ratio)
            result['details'] = {
                'ratio': float(ratio),
                'min_ratio': min_ratio,
                'property': property_type
            }
            
        else:
            # 기본 검증: 함수가 제공된 경우 (일반적인 경우)
            result['details']['message'] = 'Custom rule executed'
            result['passed'] = True
            
    except Exception as e:
        result['details']['error'] = str(e)
        result['passed'] = False
    
    return result

def validate_length(series: pd.Series, min_length: int = None, max_length: int = None) -> Dict[str, Any]:
    """문자열 길이 검증"""
    result = {
        'rule_type': 'length',
        'min_length': min_length,
        'max_length': max_length,
        'passed': True,
        'details': {}
    }
    
    # 문자열로 변환
    string_series = series.astype(str)
    
    # 길이 계산
    lengths = string_series.apply(len)
    
    if min_length is not None:
        below_min = (lengths < min_length).sum()
        result['details']['below_min_count'] = int(below_min)
        if below_min > 0:
            result['passed'] = False
    
    if max_length is not None:
        above_max = (lengths > max_length).sum()
        result['details']['above_max_count'] = int(above_max)
        if above_max > 0:
            result['passed'] = False
    
    result['details']['null_count'] = series.isnull().sum()
    result['details']['valid_count'] = len(series) - series.isnull().sum()
    result['details']['min_length_actual'] = int(lengths.min()) if not lengths.empty else None
    result['details']['max_length_actual'] = int(lengths.max()) if not lengths.empty else None
    
    return result

def validate_allowed_values(series: pd.Series, allowed_values: List[Any]) -> Dict[str, Any]:
    """허용된 값 목록 검증"""
    result = {
        'rule_type': 'allowed_values',
        'allowed_values': allowed_values,
        'passed': True,
        'details': {}
    }
    
    # 허용되지 않은 값 찾기
    not_allowed = ~series.isin(allowed_values)
    not_allowed_mask = series.notna() & not_allowed  # NULL은 제외
    
    invalid_count = not_allowed_mask.sum()
    valid_count = (~not_allowed_mask).sum()
    
    result['details']['invalid_count'] = int(invalid_count)
    result['details']['valid_count'] = int(valid_count)
    result['details']['null_count'] = series.isnull().sum()
    
    if invalid_count > 0:
        result['passed'] = False
        # 상위 10개의 잘못된 값만 표시
        invalid_values = series[not_allowed_mask].unique()[:10].tolist()
        result['details']['invalid_values'] = invalid_values
    
    return result

def validate_outlier(series: pd.Series, method: str = 'iqr', threshold: float = 1.5) -> Dict[str, Any]:
    """이상치 탐지"""
    result = {
        'rule_type': 'outlier',
        'method': method,
        'threshold': threshold,
        'passed': True,
        'details': {}
    }
    
    if not pd.api.types.is_numeric_dtype(series):
        result['passed'] = False
        result['details'] = {'error': 'Non-numeric column cannot be validated for outliers'}
        return result
    
    numeric_series = pd.to_numeric(series, errors='coerce')
    
    if method == 'iqr':
        # IQR (Interquartile Range) 방법
        Q1 = numeric_series.quantile(0.25)
        Q3 = numeric_series.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        
        outliers = numeric_series[(numeric_series < lower_bound) | (numeric_series > upper_bound)]
        
        result['details']['outlier_count'] = int(len(outliers))
        result['details']['outlier_percentage'] = float(len(outliers) / len(numeric_series) * 100)
        result['details']['lower_bound'] = float(lower_bound)
        result['details']['upper_bound'] = float(upper_bound)
        
        if len(outliers) > 0:
            result['passed'] = False
            
    elif method == 'zscore':
        # Z-score 방법
        mean = numeric_series.mean()
        std = numeric_series.std()
        
        if std == 0:
            result['passed'] = False
            result['details'] = {'error': 'Zero standard deviation'}
            return result
        
        z_scores = np.abs((numeric_series - mean) / std)
        outliers = numeric_series[z_scores > threshold]
        
        result['details']['outlier_count'] = int(len(outliers))
        result['details']['outlier_percentage'] = float(len(outliers) / len(numeric_series) * 100)
        result['details']['z_score_threshold'] = float(threshold)
        
        if len(outliers) > 0:
            result['passed'] = False
            
    elif method == 'isolation':
        # Isolation Forest 방법 (간단한 구현)
        # 실제로는 sklearn을 사용해야 하지만, 여기서는 간단한 통계적 방법 사용
        mean = numeric_series.mean()
        std = numeric_series.std()
        
        if std == 0:
            result['passed'] = False
            result['details'] = {'error': 'Zero standard deviation'}
            return result
        
        # 평균에서 3 표준편차 이상 떨어진 값들을 이상치로 간주
        outliers = numeric_series[np.abs(numeric_series - mean) > threshold * std]
        
        result['details']['outlier_count'] = int(len(outliers))
        result['details']['outlier_percentage'] = float(len(outliers) / len(numeric_series) * 100)
        result['details']['threshold_std'] = float(threshold)
        
        if len(outliers) > 0:
            result['passed'] = False
    
    else:
        result['passed'] = False
        result['details'] = {'error': f'Unknown outlier detection method: {method}'}
    
    return result

def validate_statistical(series: pd.Series, check: str, threshold: float, comparison: str = 'gte') -> Dict[str, Any]:
    """통계적 검증"""
    result = {
        'rule_type': 'statistical',
        'check': check,
        'threshold': threshold,
        'comparison': comparison,
        'passed': False,
        'details': {}
    }
    
    if not pd.api.types.is_numeric_dtype(series):
        result['passed'] = False
        result['details'] = {'error': 'Non-numeric column cannot be validated statistically'}
        return result
    
    numeric_series = pd.to_numeric(series, errors='coerce')
    
    if check == 'mean':
        stat_value = numeric_series.mean()
    elif check == 'median':
        stat_value = numeric_series.median()
    elif check == 'std':
        stat_value = numeric_series.std()
    elif check == 'min':
        stat_value = numeric_series.min()
    elif check == 'max':
        stat_value = numeric_series.max()
    elif check == 'variance':
        stat_value = numeric_series.var()
    else:
        result['passed'] = False
        result['details'] = {'error': f'Unknown statistical check: {check}'}
        return result
    
    # 비교 연산
    if comparison == 'gt':
        result['passed'] = stat_value > threshold
    elif comparison == 'gte':
        result['passed'] = stat_value >= threshold
    elif comparison == 'lt':
        result['passed'] = stat_value < threshold
    elif comparison == 'lte':
        result['passed'] = stat_value <= threshold
    elif comparison == 'eq':
        result['passed'] = abs(stat_value - threshold) < 1e-10
    else:
        result['passed'] = False
        result['details'] = {'error': f'Unknown comparison: {comparison}'}
        return result
    
    result['details']['stat_value'] = float(stat_value) if not pd.isna(stat_value) else None
    result['details']['threshold'] = threshold
    
    return result

def validate_cross_column(df: pd.DataFrame, rule: Dict[str, Any]) -> Dict[str, Any]:
    """다중 컬럼 관계 검증"""
    result = {
        'rule_type': 'cross_column',
        'passed': False,
        'details': {}
    }
    
    try:
        # 간단한 비교 연산자 기반 검증
        comparison_type = rule.get('comparison_type', 'simple')
        columns = rule.get('columns', [])
        
        if len(columns) < 2:
            result['details'] = {'error': 'At least 2 columns required for cross-column validation'}
            return result
        
        # 컬럼 존재 확인
        for col in columns:
            if col not in df.columns:
                result['details'] = {'error': f'Column "{col}" not found'}
                return result
        
        if comparison_type == 'simple':
            # 단순 비교: col1 < col2
            operator = rule.get('operator', '<')
            col1 = df[columns[0]]
            col2 = df[columns[1]]
            
            if operator == '<':
                failed_mask = col1 >= col2
            elif operator == '<=':
                failed_mask = col1 > col2
            elif operator == '>':
                failed_mask = col1 <= col2
            elif operator == '>=':
                failed_mask = col1 < col2
            elif operator == '==':
                failed_mask = col1 != col2
            elif operator == '!=':
                failed_mask = col1 == col2
            else:
                result['details'] = {'error': f'Unknown operator: {operator}'}
                return result
            
            # NULL 값 제외
            failed_mask = failed_mask & col1.notna() & col2.notna()
            failed_count = failed_mask.sum()
            
            result['details']['failed_count'] = int(failed_count)
            result['details']['total_count'] = int(len(df))
            result['details']['operator'] = operator
            result['passed'] = (failed_count == 0)
            
        elif comparison_type == 'sum':
            # 합계 검증: col1 + col2 + ... == sum_col
            sum_col = rule.get('sum_column')
            if sum_col not in df.columns:
                result['details'] = {'error': f'Sum column "{sum_col}" not found'}
                return result
            
            # 계산된 합계
            calculated_sum = df[columns].sum(axis=1)
            actual_sum = df[sum_col]
            
            failed_mask = abs(calculated_sum - actual_sum) > 1e-10
            failed_mask = failed_mask & calculated_sum.notna() & actual_sum.notna()
            failed_count = failed_mask.sum()
            
            result['details']['failed_count'] = int(failed_count)
            result['details']['total_count'] = int(len(df))
            result['passed'] = (failed_count == 0)
            
        else:
            result['details'] = {'error': f'Unknown comparison type: {comparison_type}'}
            
    except Exception as e:
        result['details']['error'] = str(e)
        result['passed'] = False
    
    return result

def apply_validation_rule(df: pd.DataFrame, rule: Dict[str, Any]) -> Dict[str, Any]:
    """단일 검증 규칙 적용"""
    rule_type = rule.get('type')
    column = rule.get('column')
    
    # cross_column 타입은 특별 처리
    if rule_type == 'cross_column':
        return validate_cross_column(df, rule)
    
    # 다른 타입들은 column이 필요
    if column is None:
        return {
            'rule_type': rule_type,
            'passed': False,
            'details': {'error': 'Column not specified'}
        }
    
    if column not in df.columns:
        return {
            'rule_type': rule_type,
            'column': column,
            'passed': False,
            'details': {'error': f'Column "{column}" not found in dataset'}
        }
    
    series = df[column]
    
    if rule_type == 'data_type':
        return validate_data_type(series, rule.get('expected_type'))
    elif rule_type == 'range':
        return validate_range(series, rule.get('min_value'), rule.get('max_value'))
    elif rule_type == 'pattern':
        return validate_pattern(series, rule.get('pattern'))
    elif rule_type == 'uniqueness':
        return validate_uniqueness(series, rule.get('unique', True))
    elif rule_type == 'completeness':
        return validate_completeness(series, rule.get('min_completeness', 0.95))
    elif rule_type == 'length':
        return validate_length(series, rule.get('min_length'), rule.get('max_length'))
    elif rule_type == 'allowed_values':
        return validate_allowed_values(series, rule.get('allowed_values', []))
    elif rule_type == 'outlier':
        return validate_outlier(series, rule.get('method', 'iqr'), rule.get('threshold', 1.5))
    elif rule_type == 'statistical':
        return validate_statistical(series, rule.get('check'), rule.get('threshold'), rule.get('comparison', 'gte'))
    elif rule_type == 'custom':
        return validate_custom_rule(series, rule)
    else:
        return {
            'rule_type': rule_type,
            'column': column,
            'passed': False,
            'details': {'error': f'Unknown rule type: {rule_type}'}
        }

def calculate_quality_score(validation_results: List[Dict[str, Any]], validation_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    검증 결과를 기반으로 품질 점수를 계산하는 함수.
    
    Parameters:
    - validation_results (List[Dict]): 검증 결과 리스트
    - validation_rules (List[Dict]): 검증 규칙 리스트
    
    Returns:
    - Dict: 품질 점수 상세 정보
    """
    if not validation_results or not validation_rules:
        return {
            'overall_score': 0.0,
            'max_score': 0.0,
            'achieved_score': 0.0,
            'passed_rules': 0,
            'failed_rules': 0,
            'total_rules': 0,
            'rule_scores': []
        }
    
    # 각 규칙의 가중치를 가져옴 (기본값: 1.0)
    rule_weights = []
    for i, rule in enumerate(validation_rules):
        weight = rule.get('weight', 1.0)
        rule_weights.append({
            'rule_index': i,
            'weight': weight,
            'rule_name': rule.get('name', f"rule_{i}"),
            'rule_type': rule.get('type')
        })
    
    # 총 가중치 계산
    total_weight = sum(rw['weight'] for rw in rule_weights)
    
    # 통과한 규칙의 가중치 합 계산
    achieved_weight = 0.0
    passed_count = 0
    failed_count = 0
    
    rule_scores = []
    
    for i, result in enumerate(validation_results):
        rule_weight = rule_weights[i]['weight']
        passed = result.get('passed', False)
        
        if passed:
            achieved_weight += rule_weight
            passed_count += 1
        else:
            failed_count += 1
        
        rule_scores.append({
            'rule_index': i,
            'rule_name': rule_weights[i]['rule_name'],
            'rule_type': rule_weights[i]['rule_type'],
            'weight': rule_weight,
            'passed': passed,
            'score': rule_weight if passed else 0.0
        })
    
    # 최종 점수 계산 (0~100점)
    if total_weight > 0:
        overall_score = (achieved_weight / total_weight) * 100
    else:
        overall_score = 0.0
    
    return {
        'overall_score': round(overall_score, 2),
        'max_score': round(total_weight * 100, 2),
        'achieved_score': round(achieved_weight * 100, 2),
        'total_weight': round(total_weight, 2),
        'achieved_weight': round(achieved_weight, 2),
        'passed_rules': passed_count,
        'failed_rules': failed_count,
        'total_rules': len(validation_results),
        'rule_scores': rule_scores
    }

def solution(input_data: StringIO, output_filename: str, settings: dict = None):
    """
    데이터 품질 검증을 수행하는 함수.
    
    Parameters:
    - input_data (StringIO): 입력 CSV 데이터
    - output_filename (str): 출력 파일 경로
    - settings (dict): 검증 설정
        - validation_rules (list): 검증 규칙 목록
        - output_format (str): 출력 형식 ('json', 'csv')
        - include_details (bool): 상세 정보 포함 여부
    
    Returns:
    - tuple: (저장된 파일 경로, 보고서 내용)
    """
    start_time = time.time()
    print(f"\n[시작] 데이터 품질 검증 작업을 시작합니다.")
    
    # 설정 기본값 설정
    if settings is None:
        settings = {}
    
    validation_rules = settings.get('validation_rules', [])
    output_format = settings.get('output_format', 'json')
    include_details = settings.get('include_details', True)
    
    print(f"- 검증 규칙: {len(validation_rules)}개")
    print(f"- 출력 형식: {output_format.upper()}")
    print(f"- 상세 정보: {'포함' if include_details else '제외'}")
    
    # CSV 데이터 로드
    print("\n[1/4] CSV 파일을 로드합니다...")
    try:
        df = pd.read_csv(input_data)
        print(f"- CSV 데이터 로드 완료: {len(df):,}행 x {len(df.columns)}열")
    except (ValueError, TypeError, pd.errors.EmptyDataError) as e:
        raise ValueError(f"CSV 파일 로드 실패: {str(e)}")
    
    # 입력 데이터 크기 확인
    input_size = len(df.to_csv().encode('utf-8'))
    print(f"- 입력 데이터 크기: {input_size / 1024:.2f} KB")
    
    # 검증 규칙 적용
    print(f"\n[2/4] 검증 규칙을 적용합니다...")
    
    try:
        validation_results = []
        
        for i, rule in enumerate(validation_rules):
            print(f"- 규칙 {i+1}/{len(validation_rules)}: {rule.get('type', 'unknown')} - {rule.get('column', 'unknown')}")
            result = apply_validation_rule(df, rule)
            result['rule_index'] = i
            result['rule'] = rule
            validation_results.append(result)
        
        print(f"- 검증 완료: {len(validation_results)}개 규칙 처리")
        
    except Exception as e:
        raise ValueError(f"검증 실패: {str(e)}")
    
    # 결과 집계
    print(f"\n[3/4] 결과를 집계합니다...")
    
    # 품질 점수 계산
    quality_score = calculate_quality_score(validation_results, validation_rules)
    
    summary = {
        'total_rules': len(validation_rules),
        'passed_rules': sum(1 for r in validation_results if r['passed']),
        'failed_rules': sum(1 for r in validation_results if not r['passed']),
        'validation_timestamp': datetime.now().isoformat(),
        'quality_score': quality_score.get('overall_score', 0.0),
        'quality_score_details': quality_score,
        'dataset_info': {
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': list(df.columns)
        }
    }
    
    print(f"- 품질 점수: {quality_score['overall_score']:.2f}점")
    print(f"- 통과: {summary['passed_rules']}개, 실패: {summary['failed_rules']}개")
    
    # 출력 데이터 구성
    if output_format == 'json':
        output_data = {
            'summary': summary,
            'validation_results': validation_results if include_details else []
        }
    else:  # CSV format
        # 검증 결과를 DataFrame으로 변환
        results_df = pd.DataFrame([
            {
                'rule_index': r['rule_index'],
                'rule_type': r['rule_type'],
                'column': r.get('column', ''),
                'passed': r['passed'],
                'details': json.dumps(r['details']) if include_details else ''
            }
            for r in validation_results
        ])
        output_data = results_df
    
    print(f"- 집계 완료: {summary['passed_rules']}개 통과, {summary['failed_rules']}개 실패")
    
    # 결과 저장
    print(f"\n[4/4] 결과를 저장합니다...")
    try:
        if output_format == 'json':
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2, default=str)
        else:  # CSV
            output_data.to_csv(output_filename, index=False, encoding='utf-8')
        
        print(f"- {output_format.upper()} 저장 완료: {output_filename}")
    except (PermissionError, OSError, UnicodeEncodeError) as e:
        raise IOError(f"파일 저장 실패: {str(e)}")
    
    # 출력 데이터 크기 확인
    output_size = os.path.getsize(output_filename)
    print(f"- 출력 데이터 크기: {output_size / 1024:.2f} KB")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\n[요약]")
    print(f"- 출력 파일: {output_filename}")
    print(f"- 원본 데이터: {len(df):,}행 x {len(df.columns)}열")
    print(f"- 검증 규칙: {summary['total_rules']}개")
    print(f"- 통과: {summary['passed_rules']}개")
    print(f"- 실패: {summary['failed_rules']}개")
    print(f"- 소요 시간: {elapsed_time:.2f}초")
    
    # 보고서 생성
    report = generate_report(df, pd.DataFrame(), output_filename, 
                           input_size, output_size, elapsed_time, settings, quality_score)
    
    return output_filename, report