FROM python:3.10-slim-buster 

WORKDIR /usr/src/app 

# 기존 패키지 제거 (호환성 문제 방지)
RUN pip uninstall numpy pandas scikit-learn -y || true

# 호환되는 버전으로 명시적 설치
RUN pip install --no-cache-dir \
    numpy==1.24.3 \
    pandas==2.0.3 \
    scikit-learn==1.3.0

COPY . . 

# 나머지 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

ENV APP_ENV production

ENTRYPOINT [ "python3", "main.py" ]