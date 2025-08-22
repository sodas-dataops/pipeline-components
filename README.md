# SODASops: Containerized Pipeline Components

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)

## 📋 목차

- [소개](#소개)
- [주요 기능](#주요-기능)
- [시작하기](#시작하기)
- [설치 및 사용법](#설치-및-사용법)
- [컴포넌트 목록](#컴포넌트-목록)
- [구성 구조](#구성-구조)
- [API 문서](#api-문서)
- [기여하기](#기여하기)
- [라이선스](#라이선스)
- [문의 및 지원](#문의-및-지원)

## 🎯 소개

### 이 오픈소스 패키지는 무엇을 위한 것인가?

SODASops는 다양한 유형의 데이터를 대상으로 분석, 전처리, 시각화, 변환 작업을 수행하는 데이터 파이프라인 기술을 포함하며, 본 서브프로젝트는 개별 태스크 컴포넌트를 구현한 **컨테이너형 데이터 파이프라인 컴포넌트 컬렉션**입니다.
모든 태스크는 독립적인 Python 컨테이너로 구성되며, Argo Workflows, Kubernetes 기반 데이터 워크플로우 환경에서 컨테이너로 동작할 수 있도록 개발되었습니다.

### 주요 개발 대상

- **데이터 전처리 자동화**: CSV, JSON 데이터의 정제, 변환, 병합 작업
- **데이터베이스 연동**: PostgreSQL, MySQL, MongoDB 등 다양한 데이터베이스에서 데이터 추출
- **실시간 데이터 수집**: MQTT, Kubernetes 로그 등 실시간 데이터 스트림 처리
- **데이터 시각화**: 차트, 그래프, 워드클라우드 등 다양한 시각화 제공

### 설계 방향

- **모듈화된 설계**: 각 기능이 독립적인 컨테이너로 구성되어 재사용성과 확장성이 높음
- **표준화된 인터페이스**: 모든 컴포넌트가 일관된 입력/출력 형식을 사용
- **클라우드 네이티브**: Kubernetes 환경에서 즉시 실행 가능
- **메모리 최적화**: 대용량 데이터 처리 시 청킹과 스트리밍 방식으로 메모리 효율성 확보

### 대상 사용자

- **데이터 엔지니어**: ETL/ELT 파이프라인 구축
- **ML/AI 엔지니어**: 데이터 전처리 및 특성 엔지니어링
- **DevOps 엔지니어**: 데이터 파이프라인 자동화
- **연구원**: 데이터 분석 및 시각화 작업
- **시스템 관리자**: 로그 수집 및 모니터링

### 동작 방식

각 컴포넌트는 다음과 같은 구조로 작동합니다:

1. **설정 로드**: `config/config.py`에서 환경별 설정값 로드
2. **데이터 입력**: Object Storage 또는 로컬 파일에서 데이터 읽기
3. **처리 실행**: `algorithm.py`에서 정의된 로직으로 데이터 처리
4. **결과 출력**: 처리된 데이터를 CSV/JSON 형태로 Object Storage에 저장
5. **보고서 생성**: 실행 결과와 통계 정보를 포함한 보고서 생성

## 주요 기능

### 데이터 처리
- **CSV 연산**: 산술 연산, 컬럼 조작, 정렬, 필터링
- **JSON 처리**: 병합, 변환, 스키마 생성
- **데이터베이스 연동**: PostgreSQL, MySQL, MongoDB 데이터 추출
- **실시간 스트림**: MQTT 구독, Kubernetes 로그 수집

### 시각화
- **차트**: 막대차트, 파이차트, 히스토그램, 박스플롯
- **지도**: 지리적 데이터 시각화
- **워드클라우드**: 텍스트 데이터 시각화
- **상관관계 분석**: 페어플롯, 코사인 유사도

### 시스템 통합
- **Object Storage**: S3 호환 스토리지 지원
- **컨테이너화**: Docker 기반 배포
- **워크플로우**: Kubernetes/Argo Workflows 연동
- **모니터링**: 메모리 사용량, 실행 시간 추적

## 시작하기

### 전제조건

- **Python 3.10+**
- **Docker** (컨테이너 실행용)
- **Kubernetes** (선택사항, 워크플로우 실행용)
- **Object Storage** (S3 호환 스토리지)

### 빠른 시작

1. **저장소 클론**
   ```bash
   git clone https://github.com/sodas-dataops/pipeline-components.git
   cd pipeline-component

2. **설정 파일 수정**
   ```python
   # config/config.py
   development = {
        'input1': {...},
        'input_cols': ['col1'], 
        'is_asc': True,
        'output1': {...}
   }
   ```

3. **로컬에서 실행 예시**
    ```
    python main.py
    ```


3. **컨테이너 실행 예시**
   ```bash
   # CSV 정렬 컴포넌트 실행
   docker build -t csv-sort .
   docker run -e APP_ENV=production csv-sort
   ```

## 설치 및 사용법

### 로컬 설치

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는 venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

### Docker 설치

```bash
# 이미지 빌드
docker build -t sodasops-component .

# 컨테이너 실행
docker run -e APP_ENV=production sodasops-component
```

### Kubernetes 배포

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: csv-sort-pod
spec:
  containers:
  - name: csv-sort
    image: csv-sort:latest
    env:
    - name: APP_ENV
      value: "production"
    resources:
      limits:
        memory: "2Gi"
        cpu: "2"
      requests:
        memory: "1Gi"
        cpu: "1"
```

## 컴포넌트 목록

### CSV 기반 연산
- [`csv-arithmetic-operation`](./csv-arithmetic-operation/) - 산술 연산 수행
- [`csv-change-column-name`](./csv-change-column-name/) - 컬럼명 변경
- [`csv-column-concat`](./csv-column-concat/) - 컬럼 결합
- [`csv-cosine-similarity`](./csv-cosine-similarity/) - 코사인 유사도 계산
- [`csv-date-time-formatter`](./csv-date-time-formatter/) - 날짜/시간 포맷 변환
- [`csv-delete-missing-value`](./csv-delete-missing-value/) - 결측값 삭제
- [`csv-embedding`](./csv-embedding/) - 텍스트 임베딩 생성
- [`csv-from-parquet`](./csv-from-parquet/) - Parquet에서 CSV 변환
- [`csv-get-latlon`](./csv-get-latlon/) - 주소에서 위경도 추출
- [`csv-join`](./csv-join/) - CSV 파일 조인
- [`csv-merge`](./csv-merge/) - CSV 파일 병합
- [`csv-regex`](./csv-regex/) - 정규표현식 처리
- [`csv-sort`](./csv-sort/) - 데이터 정렬
- [`csv-statistic-summary`](./csv-statistic-summary/) - 통계 요약
- [`csv-tokenize`](./csv-tokenize/) - 텍스트 토큰화
- [`csv-transform`](./csv-transform/) - 데이터 변환
- [`csv-wordcount`](./csv-wordcount/) - 단어 빈도 계산

### CSV 기반 시각화
- [`csv-visualization-barchart`](./csv-visualization-barchart/) - 막대차트 생성
- [`csv-visualization-boxplot`](./csv-visualization-boxplot/) - 박스플롯 생성
- [`csv-visualization-histogram`](./csv-visualization-histogram/) - 히스토그램 생성
- [`csv-visualization-map`](./csv-visualization-map/) - 지도 시각화
- [`csv-visualization-pairplot`](./csv-visualization-pairplot/) - 페어플롯 생성
- [`csv-visualization-piechart`](./csv-visualization-piechart/) - 파이차트 생성
- [`csv-visualization-wordcloud`](./csv-visualization-wordcloud/) - 워드클라우드 생성

### JSON 처리
- [`json-merge`](./json-merge/) - JSON 파일 병합
- [`json-merge-from-directory`](./json-merge-from-directory/) - 디렉토리 내 JSON 병합
- [`json-to-csv`](./json-to-csv/) - JSON을 CSV로 변환
- [`json-upload`](./json-upload/) - JSON 파일 업로드

### 데이터베이스 연동
- [`postgresql-to-csv`](./postgresql-to-csv/) - PostgreSQL 데이터 추출
- [`mysql-to-csv`](./mysql-to-csv/) - MySQL 데이터 추출
- [`dump-mysql-to-csv`](./dump-mysql-to-csv/) - MySQL 전체 테이블 덤프
- [`dump-mongodb-to-json`](./dump-mongodb-to-json/) - MongoDB 컬렉션 덤프
- [`postgresql-to-csv`](./postgresql-to-csv/) - PostgreSQL 데이터 추출

### 실시간 데이터 수집
- [`mqtt-subscriber`](./mqtt-subscriber/) - MQTT 메시지 구독
- [`kubernetes-log-collector`](./kubernetes-log-collector/) - Kubernetes 로그 수집

### 기타 유틸리티
- [`csv-to-json`](./csv-to-json/) - CSV를 JSON으로 변환
- [`upload-object-file-to-restapi`](./upload-object-file-to-restapi/) - REST API 파일 업로드
- [`sodas-append-dataset-to-datasetseries`](./sodas-append-dataset-to-datasetseries/) - 데이터셋 시리즈 추가

## 구성 구조

각 컴포넌트는 다음 표준 구조를 따릅니다:

```
component/
├── config/
│   └── config.py          # 환경별 설정 정의
├── tmp/                   # 임시 파일 저장소
├── algorithm.py           # 핵심 처리 로직
├── main.py               # 프로그램 진입점
├── test.py               # 단위 테스트
├── requirements.txt      # Python 의존성
├── Dockerfile           # 컨테이너 빌드 정의
├── .dockerignore        # 빌드 제외 파일
└── README.md            # 컴포넌트별 문서
```

### 설정 파일 구조

```python
# config/config.py
settings = {
    'development': {
        'input': {...},
        'output1': {...},
        'settings': {...}
    },
    'production': {
        # 프로덕션 환경 설정...
    }
}
```

## 기여하기

### 기여 방법

1. **Fork** 저장소
2. **Feature branch** 생성 (`git checkout -b feature/newfeatrue`)
3. **Commit** 변경사항 (`git commit -m 'Add some newfeatrue'`)
4. **Push** 브랜치 (`git push origin feature/newfeatrue`)
5. **Pull Request** 생성

### 개발 환경 설정

```bash
# 개발 환경 설정
git clone https://github.com/sodas-dataops/pipeline-components.git
cd pipeline-component
cd csv-sort
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 테스트 실행
python test.py
```

### 코딩 스타일

- **Python**: PEP 8 준수
- **문서화**: docstring 사용
- **테스트**: 각 컴포넌트별 단위 테스트 작성
- **컨테이너**: Dockerfile 최적화

## 라이선스

이 프로젝트는 [GNU General Public License v3.0](LICENSE) 하에 배포됩니다.

### 라이선스 조건

- **소스코드 공개**: GPL v3.0 조건에 따라 수정된 소스코드 공개 의무
- **파생작품**: 이 프로젝트를 기반으로 한 파생작품도 동일한 라이선스 적용

## 문의 및 지원

### 담당자 정보

- **개발팀**: ETRI CybreBrain Section
- **담당자**: Siwoon Son
- **이메일**: siwoonson@etri.re.kr

### 지원 채널

- **이슈 리포트**: [GitHub Issues](https://github.com/sodas-dataops/pipeline-components/issues)
- **문서**: [Wiki](https://github.com/sodas-dataops/pipeline-components/wiki)
- **토론**: [GitHub Discussions](https://github.com/sodas-dataops/pipeline-components/discussions)

---