FROM python:3.10-slim-buster 

WORKDIR /usr/src/app 

COPY . . 

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