FROM python:3.10-alpine

COPY requirements.txt /app/requirements.txt

WORKDIR /app

RUN apk add --no-cache --virtual .build-deps git gcc musl-dev libffi-dev openssl-dev python3-dev cargo && \
    apk add --no-cache mariadb-dev && \
    pip3 install --no-cache-dir -r requirements.txt && \
    apk del .build-deps && \
    rm requirements.txt

COPY src /app

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "movies.wsgi:application"]
