FROM python:3.10-slim-buster 

WORKDIR /usr/src/app 

COPY . . 

RUN pip install -r requirements.txt

ENV APP_ENV production

ENTRYPOINT [ "python3", "main.py" ]