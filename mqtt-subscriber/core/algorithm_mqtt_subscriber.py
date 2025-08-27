import os
import time
import json
import psutil
import paho.mqtt.client as mqtt
from datetime import datetime
from tabulate import tabulate

def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ MQTT 브로커 연결 성공!")
    else:
        print(f"❌ MQTT 연결 실패: {rc}")

def on_message(client, userdata, msg):
    message = msg.payload.decode('utf-8')
    record = {
        'topic': msg.topic,
        'payload': message,
        'timestamp': datetime.now().isoformat()
    }
    # 임시 파일에 append
    with open(userdata['tmp_file'], 'a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')
    # 샘플 메시지만 메모리에 유지
    if len(userdata['samples']) < 5:
        userdata['samples'].append(record)
    if userdata['msg_count'] % 10 == 0:
        print(f"  └─ {userdata['msg_count']}개 메시지 수신 (임시파일)")
    userdata['msg_count'] += 1

def save_tmp_to_json(tmp_file, output_dir):
    if not os.path.exists(tmp_file):
        return None, 0
    with open(tmp_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    if not lines:
        return None, 0
    msgs = [json.loads(line) for line in lines]
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_file = os.path.join(output_dir, f"mqtt_messages_{ts}.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(msgs, f, ensure_ascii=False, indent=2)
    print(f"[INFO] {len(msgs)}개 메시지 → {json_file} 저장 및 업로드 준비")
    # 임시 파일 비움
    open(tmp_file, 'w').close()
    return json_file, len(msgs)

def subscribe_and_collect(settings, upload_callback=None):
    output_dir = settings['output_dir']
    save_interval = settings.get('save_interval', 60)
    duration = settings.get('duration', -1)
    os.makedirs(output_dir, exist_ok=True)
    tmp_file = os.path.join(output_dir, 'mqtt_messages.tmp')
    samples = []
    userdata = {'tmp_file': tmp_file, 'samples': samples, 'msg_count': 1}
    client = mqtt.Client(client_id=settings['client_id'], userdata=userdata)
    if settings.get('username'):
        client.username_pw_set(settings['username'], settings['password'])
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(settings['mqtt_broker'], settings['mqtt_port'], settings['keepalive'])
    client.subscribe(settings['mqtt_topic'])
    client.loop_start()
    print(f"[INFO] {settings['mqtt_topic']} 구독 시작 (interval={save_interval}s, duration={duration})")
    start_time = time.time()
    last_save = time.time()
    saved_files = []
    total_msgs = 0
    try:
        while True:
            time.sleep(1)
            now = time.time()
            # 주기적 저장
            if now - last_save >= save_interval:
                json_file, count = save_tmp_to_json(tmp_file, output_dir)
                if json_file:
                    saved_files.append(json_file)
                    total_msgs += count
                    if upload_callback:
                        upload_callback(json_file)
                last_save = now
            # 종료 조건
            if duration is not None and duration > 0 and now - start_time >= duration:
                print(f"[INFO] 설정된 duration({duration}s) 경과로 종료")
                break
    except KeyboardInterrupt:
        print("[INFO] 수동 종료 신호 감지")
    finally:
        # 남은 메시지 저장
        json_file, count = save_tmp_to_json(tmp_file, output_dir)
        if json_file:
            saved_files.append(json_file)
            total_msgs += count
            if upload_callback:
                upload_callback(json_file)
        client.loop_stop()
        client.disconnect()
        print(f"[INFO] 구독 종료, 총 {total_msgs}개 메시지 수신")
    return saved_files, samples, total_msgs

def generate_report(saved_files, samples, total_msgs, settings, execution_time):
    report = f"""# MQTT Subscriber 실행 보고서\n\n## 실행 정보\n- 실행 시간: {execution_time}\n- 브로커: {settings['mqtt_broker']}\n- 토픽: {settings['mqtt_topic']}\n- 구독 시간: {settings['duration']}초\n- 저장 주기: {settings.get('save_interval', 60)}초\n- 메시지 파일 수: {len(saved_files)}\n- 총 메시지 수: {total_msgs}\n\n## 메시지 샘플\n"""
    if samples:
        table = [[m['timestamp'], m['topic'], m['payload']] for m in samples[:5]]
        report += tabulate(table, headers=['수신시각', '토픽', '내용'], tablefmt="github")
    else:
        report += "(샘플 없음)"
    return report

def solution(settings, upload_callback=None):
    """
    MQTT 브로커에서 메시지를 수신하고 저장하는 함수.

    Parameters:
    - settings (dict): 설정 정보
    - upload_callback (function): 메시지 파일 업로드 콜백 함수 (기본값: None)

    Returns:
    - tuple: (저장된 파일 경로 리스트, 보고서 내용)
    """
    start_time = datetime.now()
    print(f"* MQTT 구독 시작")
    print(f"- 브로커: {settings['mqtt_broker']}, 토픽: {settings['mqtt_topic']}")
    print(f"- 초기 메모리 사용량: {get_memory_usage():.1f} MB")
    saved_files, samples, total_msgs = subscribe_and_collect(settings, upload_callback=upload_callback)
    execution_time = datetime.now() - start_time
    report_content = generate_report(saved_files, samples, total_msgs, settings, execution_time)
    print(f"- 구독 및 저장 완료: {len(saved_files)}개 파일")
    print(f"-  실행 시간: {execution_time}")
    return saved_files, report_content 