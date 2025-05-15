FROM python:3.10-slim-buster 

WORKDIR /usr/src/app 

# requirements.txt만 먼저 복사해서 pip 캐시 유도
COPY requirements.txt .

# 캐시 없이 pip 설치
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

# 이후 앱 코드와 model 디렉터리만 복사 (명시적으로 지정)
COPY . . 

ENV HF_HOME=/usr/src/app/model

ENV APP_ENV production

ENV PYTHONUNBUFFERED=1

ENTRYPOINT [ "python3", "-u", "main.py" ]