FROM python:3.10-alpine

WORKDIR /app

ENV PROJECT=movies

COPY requirements.txt ./requirements.txt

RUN apk add --no-cache --virtual .build-deps git gcc musl-dev libffi-dev openssl-dev python3-dev cargo && \
    apk add --no-cache mariadb-dev && \
    pip3 install --no-cache-dir -r requirements.txt && \
    apk del .build-deps && \
    rm requirements.txt

COPY entrypoint.sh .
COPY src .

EXPOSE 8000

CMD ["./entrypoint.sh"]
