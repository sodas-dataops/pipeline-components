# MQTT Subscriber

MQTT 브로커로부터 메시지를 구독하여 파일로 저장하고, Object Storage에 업로드하는 파이프라인 컴포넌트입니다.

## 기능
- MQTT 브로커 구독 및 메시지 수신
- 메시지 파일(JSONL)로 저장
- 구독/저장 통계 및 샘플 리포트 생성
- Object Storage(S3 호환)에 메시지/리포트 업로드
- 컨테이너/파이프라인 환경에 최적화

## 프로젝트 구조
```
mqtt-subscriber/
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
        'mqtt_broker': 'broker.hivemq.com',
        'mqtt_port': 1883,
        'mqtt_topic': 'test/topic',
        'client_id': 'mqtt-subscriber-dev',
        'username': '',
        'password': '',
        'keepalive': 60,
        'output_file': './tmp/mqtt_messages.txt',
        'duration': 60,
    },
    'output1': {
        'end_point': 'http://object-storage.rook.xxxx.xxx.xxx.xxx:xxxxx',
        'access_key': 'abc',
        'secret_key': 'abc',
        'bucket_name': 'bucket01',
        'object_path': 'dir/mqtt_messages.txt',
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
2. config/config.py에서 MQTT 브로커/토픽 등 설정
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
docker build -t mqtt-subscriber .
```
2. Docker 컨테이너 실행
```bash
docker run -e SETTINGS='{"mqtt_broker":"broker.hivemq.com","mqtt_port":1883,"mqtt_topic":"test/topic","client_id":"mqtt-subscriber-prod","duration":60}' \
           -e OUTPUT1='{"end_point":"http://object-storage.rook.xxxx.xxx.xxx.xxx:xxxxx","access_key":"abc","secret_key":"abc","bucket_name":"bucket01","object_path":"dir/mqtt_messages.txt"}' \
           -e TASK_REPORT='{"end_point":"http://object-storage.rook.xxxx.xxx.xxx.xxx:xxxxx","access_key":"abc","secret_key":"abc","bucket_name":"bucket01","object_path":"dir/report.md"}' \
           mqtt-subscriber
```

## 출력 파일
- **메시지 파일**: 수신 메시지 전체(JSONL)
- **보고서 파일**: 실행 정보, 샘플, 통계 포함 Markdown

## 주요 의존성
- `paho-mqtt`: MQTT 클라이언트
- `boto3`: S3 업로드
- `tabulate`: 표 형태 리포트
- `psutil`: 메모리 모니터링

## 참고
- MQTT 브로커/토픽/인증 등은 환경설정에서 자유롭게 변경 가능
- Object Storage는 S3 호환이면 모두 지원
- duration(초) 동안만 구독 후 자동 종료 