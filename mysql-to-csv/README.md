# MySQL to CSV

MySQL(MariaDB) 데이터베이스에서 SQL 쿼리를 실행하고 결과를 CSV 파일로 저장하는 파이프라인 컴포넌트입니다.

## 기능

- MySQL/MariaDB 데이터베이스 연결
- 사용자 정의 SQL 쿼리 실행
- 쿼리 결과를 CSV 파일로 저장
- Object Storage에 결과 파일 업로드
- 실행 결과 보고서 생성
- 데이터 품질 정보 제공 (null 값 통계)

## 프로젝트 구조

```
mysql-to-csv/
├── config/
│   └── config.py          # 설정 파일
├── tmp/                   # 임시 파일 디렉토리
├── algorithm.py           # 핵심 알고리즘
├── main.py               # 메인 실행 파일
├── test.py               # 테스트 파일
├── requirements.txt      # Python 의존성
├── Dockerfile           # Docker 설정
├── .dockerignore        # Docker 제외 파일
└── README.md            # 프로젝트 설명
```

## 설정

### 개발 환경 설정 (config/config.py)

```python
'development': {
    'mysql': {
        'host': 'relational.fet.cvut.cz',
        'port': 3306,
        'database': 'IMDb',
        'username': 'guest',
        'password': 'ctu-relational',
        'charset': 'utf8mb4',
    },
    'sql_query': 'SELECT * FROM tenant LIMIT 100',
    'output1': {
        'end_point': 'http://object-storage.rook.xxxx.xxx.xxx.xxx:xxxxx',
        'access_key': 'abc',
        'secret_key': 'abc',
        'bucket_name': 'bucket01',
        'object_path': 'dir/mysql_result.csv',
    },
    'task_report': {
        'end_point': 'http://object-storage.rook.xxxx.xxx.xxx.xxx:xxxxx',
        'access_key': 'abc',
        'secret_key': 'abc',
        'bucket_name': 'bucket01',
        'object_path': 'dir/report.md',
    },
}
```

### 프로덕션 환경 변수

- `MYSQL`: MySQL 연결 정보 (JSON)
- `SQL_QUERY`: 실행할 SQL 쿼리
- `OUTPUT1`: 출력 파일 Object Storage 정보 (JSON)
- `TASK_REPORT`: 보고서 파일 Object Storage 정보 (JSON)

## 사용법

### 로컬 실행

1. 의존성 설치:
```bash
pip install -r requirements.txt
```

2. 설정 파일 수정:
   - `config/config.py`에서 MySQL 연결 정보와 SQL 쿼리를 수정

3. 테스트 실행:
```bash
python test.py
```

4. 메인 실행:
```bash
python main.py
```

### Docker 실행

1. Docker 이미지 빌드:
```bash
docker build -t mysql-to-csv .
```

2. Docker 컨테이너 실행:
```bash
docker run -e MYSQL='{"host":"localhost","port":3306,"database":"testdb","username":"root","password":"password","charset":"utf8mb4"}' \
           -e SQL_QUERY="SELECT * FROM users LIMIT 100" \
           -e OUTPUT1='{"end_point":"http://object-storage.rook.xxxx.xxx.xxx.xxx:xxxxx","access_key":"abc","secret_key":"abc","bucket_name":"bucket01","object_path":"dir/mysql_result.csv"}' \
           -e TASK_REPORT='{"end_point":"http://object-storage.rook.xxxx.xxx.xxx.xxx:xxxxx","access_key":"abc","secret_key":"abc","bucket_name":"bucket01","object_path":"dir/report.md"}' \
           mysql-to-csv
```

## 출력 파일

- **CSV 파일**: SQL 쿼리 결과가 저장된 CSV 파일
- **보고서 파일**: 실행 정보, 결과 통계, 데이터 샘플이 포함된 Markdown 파일

## 보고서 내용

실행 보고서에는 다음 정보가 포함됩니다:

- 실행 시간
- 실행된 SQL 쿼리
- 결과 행 수 및 컬럼 수
- 컬럼 목록
- 처음 5행 데이터 샘플
- 컬럼 데이터 타입
- 메모리 사용량
- **데이터 품질 정보** (null 값 개수 및 비율)

## MySQL vs PostgreSQL 차이점

### MySQL 특화 기능
- **문자셋 설정**: UTF-8 지원을 위한 charset 설정
- **PyMySQL 드라이버**: MySQL 전용 Python 드라이버 사용
- **데이터 품질 정보**: null 값 통계 제공
- **MariaDB 호환**: MariaDB와 완전 호환

### 연결 문자열 형식
```python
# MySQL
mysql+pymysql://username:password@host:port/database?charset=utf8mb4

# PostgreSQL (참고)
postgresql://username:password@host:port/database
```

## 의존성

- `pandas`: 데이터 처리
- `boto3`: AWS S3/Object Storage 연동
- `pymysql`: MySQL 연결 드라이버
- `sqlalchemy`: 데이터베이스 ORM
- `tabulate`: 테이블 형태 보고서 생성

## 주의사항

1. MySQL 서버에 대한 네트워크 접근 권한이 필요합니다.
2. Object Storage 접근 권한이 필요합니다.
3. 대용량 데이터 처리 시 메모리 사용량을 고려해야 합니다.
4. SQL 쿼리는 적절한 권한이 있는 사용자로 실행되어야 합니다.
5. MySQL의 문자셋 설정이 중요합니다 (한글 데이터 처리 시).
6. MariaDB와 완전 호환됩니다.

## PostgreSQL to CSV와의 차이점

| 기능 | PostgreSQL to CSV | MySQL to CSV |
|------|------------------|--------------|
| 데이터베이스 | PostgreSQL | MySQL/MariaDB |
| 드라이버 | psycopg2-binary | pymysql |
| 문자셋 | 기본 UTF-8 | 설정 가능 (utf8mb4) |
| 데이터 품질 | 기본 통계 | null 값 상세 통계 |
| 연결 문자열 | postgresql:// | mysql+pymysql:// | 