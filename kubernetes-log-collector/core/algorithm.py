import os
import time
import json
import psutil
import threading
from kubernetes import client, config
from datetime import datetime
from tabulate import tabulate

def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def load_kube_config(kubeconfig_path):
    config.load_kube_config(config_file=kubeconfig_path)

def collect_once(settings, kubeconfig_path):
    load_kube_config(kubeconfig_path)
    v1 = client.CoreV1Api()
    logs = v1.read_namespaced_pod_log(
        name=settings['pod'],
        namespace=settings['namespace'],
        container=settings['container'],
        follow=False,
        _preload_content=True
    )
    os.makedirs(settings['output_dir'], exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_path = os.path.join(settings['output_dir'], f"k8s_log_once_{ts}.log")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(logs)
    print(f"[INFO] once 로그 {len(logs)}자 저장 → {file_path}")
    lines = logs.splitlines()
    samples = lines[:5]
    return [file_path], samples, len(lines)

def collect_follow(settings, kubeconfig_path, upload_callback=None):
    load_kube_config(kubeconfig_path)
    v1 = client.CoreV1Api()
    os.makedirs(settings['output_dir'], exist_ok=True)
    save_interval = settings.get('save_interval', 60)
    duration = settings.get('duration', None)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    tmp_file = os.path.join(settings['output_dir'], f"k8s_log_follow_{ts}.tmp")
    saved_files = []
    samples = []
    total_lines = 0
    start_time = time.time()
    last_save = time.time()
    f_tmp = open(tmp_file, 'a', encoding='utf-8')
    
    # duration 체크를 위한 이벤트
    stop_event = threading.Event()
    
    def duration_checker():
        if duration:
            time.sleep(duration)
            print(f"[INFO] duration({duration}s) 경과로 종료")
            stop_event.set()
    
    def stream():
        nonlocal f_tmp, saved_files, samples, total_lines, last_save
        try:
            # duration 체크 스레드 시작
            if duration:
                duration_thread = threading.Thread(target=duration_checker)
                duration_thread.daemon = True
                duration_thread.start()
            
            while not stop_event.is_set():
                try:
                    # 짧은 timeout으로 로그 스트림 체크
                    for line in v1.read_namespaced_pod_log(
                        name=settings['pod'],
                        namespace=settings['namespace'],
                        container=settings['container'],
                        follow=True,
                        _preload_content=False,
                        _return_http_data_only=True,
                        _request_timeout=5,  # 5초 timeout
                        timestamps=True
                    ):
                        if stop_event.is_set():
                            break
                        
                        line = line.decode('utf-8').rstrip('\n')
                        f_tmp.write(line + '\n')
                        total_lines += 1
                        if len(samples) < 5:
                            samples.append(line)
                        
                        # save_interval 체크
                        now = time.time()
                        if now - last_save >= save_interval:
                            f_tmp.flush()
                            f_tmp.close()
                            ts2 = datetime.now().strftime('%Y%m%d_%H%M%S')
                            out_file = os.path.join(settings['output_dir'], f"k8s_log_follow_{ts2}.log")
                            os.rename(tmp_file, out_file)
                            saved_files.append(out_file)
                            print(f"[INFO] follow 로그 {out_file} 저장 및 업로드 준비")
                            if upload_callback:
                                upload_callback(out_file)
                            f_tmp = open(tmp_file, 'a', encoding='utf-8')
                            last_save = now
                
                except Exception as e:
                    if "read timed out" in str(e).lower():
                        print(f"[INFO] 5초간 로그 데이터가 없으나 계속 대기")
                        continue
                    else:
                        print(f"[ERROR] 로그 스트림 중 오류: {e}")
                        break
                        
        except Exception as e:
            print(f"[ERROR] 로그 스트림 중 오류: {e}")
        finally:
            # 마지막 남은 로그 저장
            f_tmp.flush()
            f_tmp.close()
            if os.path.getsize(tmp_file) > 0:
                ts2 = datetime.now().strftime('%Y%m%d_%H%M%S')
                out_file = os.path.join(settings['output_dir'], f"k8s_log_follow_{ts2}.log")
                os.rename(tmp_file, out_file)
                saved_files.append(out_file)
                print(f"[INFO] follow 로그 {out_file} 저장 및 업로드 준비")
                if upload_callback:
                    upload_callback(out_file)
    
    stream()
    return saved_files, samples, total_lines

def generate_report(saved_files, samples, total_lines, settings, execution_time):
    report = f"""# Kubernetes Log Collector 실행 보고서\n\n## 실행 정보\n- 실행 시간: {execution_time}\n- 네임스페이스: {settings['namespace']}\n- 파드: {settings['pod']}\n- 컨테이너: {settings['container']}\n- 모드: {settings['mode']}\n- 저장 파일 수: {len(saved_files)}\n- 총 로그 라인 수: {total_lines}\n\n## 로그 샘플\n"""
    if samples:
        table = [[i+1, s[:120]] for i, s in enumerate(samples)]
        report += tabulate(table, headers=['라인', '내용'], tablefmt="github")
    else:
        report += "(샘플 없음)"
    return report

def solution(settings, kubeconfig_path, upload_callback=None):
    """
    Kubernetes 로그를 수집하고 저장하는 함수.

    Parameters:
    - settings (dict): 설정 정보
    - kubeconfig_path (str): kubeconfig 파일 경로
    - upload_callback (function): 로그 파일 업로드 콜백 함수 (기본값: None)

    Returns:
    - tuple: (저장된 파일 경로 리스트, 보고서 내용)
    """
    start_time = datetime.now()
    print(f"* Kubernetes 로그 수집 시작")
    print(f"- 네임스페이스: {settings['namespace']}, 파드: {settings['pod']}, 컨테이너: {settings['container']}")
    print(f"- 모드: {settings['mode']}")
    print(f"- 초기 메모리 사용량: {get_memory_usage():.1f} MB")
    if settings['mode'] == 'once':
        saved_files, samples, total_lines = collect_once(settings, kubeconfig_path)
        if upload_callback:
            for f in saved_files:
                upload_callback(f)
    else:
        saved_files, samples, total_lines = collect_follow(settings, kubeconfig_path, upload_callback=upload_callback)
    execution_time = datetime.now() - start_time
    report_content = generate_report(saved_files, samples, total_lines, settings, execution_time)
    print(f"- 로그 수집 및 저장 완료: {len(saved_files)}개 파일")
    print(f"-  실행 시간: {execution_time}")
    return saved_files, report_content 