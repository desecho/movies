FROM python:3.9-alpine

ADD requirements.txt /app/requirements.txt

RUN apk add --no-cache --virtual .build-deps git gcc musl-dev libffi-dev openssl-dev python3-dev cargo && \
    apk add --no-cache mariadb-dev && \
    pip3 install --no-cache-dir -r /app/requirements.txt && \
    apk del .build-deps

ADD src /app
WORKDIR /app

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "movies.wsgi:application"]
