FROM python:3.10-slim-buster 

# 기본 패키지 설치
RUN apt-get update && apt-get install -y \
    default-jdk \
    curl \
    && rm -rf /var/lib/apt/lists/*

# JAVA_HOME 환경 변수 설정
ENV JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64"
ENV PATH="$JAVA_HOME/bin:$PATH"

WORKDIR /usr/src/app 

COPY . . 

RUN pip install --no-cache-dir -r requirements.txt

ENV APP_ENV production

ENTRYPOINT [ "python3", "main.py" ]