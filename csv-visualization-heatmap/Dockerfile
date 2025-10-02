FROM python:3.10-slim-buster 

WORKDIR /usr/src/app 

COPY . . 

RUN set -eux; \
    echo 'deb http://archive.debian.org/debian buster main' > /etc/apt/sources.list; \
    echo 'deb http://archive.debian.org/debian buster-updates main' >> /etc/apt/sources.list; \
    echo 'deb http://archive.debian.org/debian-security buster/updates main' >> /etc/apt/sources.list; \
    apt-get -o Acquire::Check-Valid-Until=false update; \
    apt-get install -y --no-install-recommends fonts-nanum; \
    rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies and fonts-nanum
RUN apt-get update && apt-get install -y \
    fonts-nanum \
    --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt

ENV APP_ENV production

ENTRYPOINT [ "python3", "main.py" ]