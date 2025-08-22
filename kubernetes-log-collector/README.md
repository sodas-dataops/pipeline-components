# Kubernetes Log Collector

Kubernetes 클러스터의 특정 파드/컨테이너 로그를 수집하여 파일로 저장하고, Object Storage에 업로드하는 파이프라인 컴포넌트입니다.

## 기능
- kubeconfig 기반 클러스터 접근 (config.py/환경변수)
- 특정 네임스페이스/파드/컨테이너 로그 수집
- once 모드: 기존 로그 전체 일괄 저장
- follow 모드: 실시간 tail, 주기적 파일 분할 저장, duration 옵션 지원
- 로그 파일명에 타임스탬프 포함
- Object Storage(S3 호환)에 로그/리포트 업로드
- 컨테이너/파이프라인 환경에 최적화

## 프로젝트 구조
```
kubernetes-log-collector/
├── config/config.py          # 환경설정
├── algorithm.py              # 핵심 로직
├── main.py                   # 실행/통합
├── test.py                   # 로컬 테스트
├── requirements.txt          # 의존성
├── Dockerfile                # Docker 설정
├── .dockerignore             # Docker 제외 파일
├── README.md                 # 설명서
└── tmp/                      # 임시 파일 디렉토리
```

## 설정 예시 (config/config.py)
```python
'development': {
    'settings': {
        'kubeconfig': './config/kubeconfig.yaml',
        'namespace': 'default',
        'pod': 'my-pod',
        'container': 'my-container',
        'mode': 'once',  # 'once' or 'follow'
        'save_interval': 60,
        'duration': 300,
        'output_dir': './tmp/logs',
    },
    'output1': {
        'end_point': 'http://object-storage.rook.xxxx.xxx.xxx.xxx:xxxxx',
        'access_key': 'abc',
        'secret_key': 'abc',
        'bucket_name': 'bucket01',
        'object_path': 'dir/k8s_logs/',
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

## 사용법

### 로컬 실행
1. 의존성 설치
```bash
pip install -r requirements.txt
```
2. config/config.py에서 kubeconfig/네임스페이스/파드 등 설정
3. 테스트 실행
```bash
python test.py
```
4. 메인 실행
```bash
python main.py
```

### Docker 실행
1. Docker 이미지 빌드
```bash
docker build -t kubernetes-log-collector .
```
2. Docker 컨테이너 실행
```bash
docker run -e SETTINGS='{"kubeconfig":"/config/kubeconfig.yaml","namespace":"default","pod":"mypod","container":"mycontainer","mode":"once"}' \
           -e OUTPUT1='{"end_point":"http://object-storage.rook.xxxx.xxx.xxx.xxx:xxxxx","access_key":"abc","secret_key":"abc","bucket_name":"bucket01","object_path":"dir/k8s_logs/"}' \
           -e TASK_REPORT='{"end_point":"http://object-storage.rook.xxxx.xxx.xxx.xxx:xxxxx","access_key":"abc","secret_key":"abc","bucket_name":"bucket01","object_path":"dir/report.md"}' \
           -v /path/to/kubeconfig.yaml:/config/kubeconfig.yaml \
           kubernetes-log-collector
```

## 출력 파일
- **로그 파일**: once/follow 모드에 따라 1개 또는 여러 개 생성
- **보고서 파일**: 실행 정보, 샘플, 통계 포함 Markdown

## 주요 의존성
- `kubernetes`: K8s API 연동
- `boto3`: S3 업로드
- `tabulate`: 표 형태 리포트
- `psutil`: 메모리 모니터링

## 참고
- kubeconfig는 파일 또는 환경변수(JSON)로 전달 가능
- Object Storage는 S3 호환이면 모두 지원
- follow 모드에서 duration(초) 동안만 tail 후 자동 종료 