FROM python:3.10-slim-buster

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV APP_ENV=production

ENTRYPOINT ["python", "main.py"] 