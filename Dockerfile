FROM python:3.10.6-alpine3.16

ARG REQUIREMENTS=requirements.txt

ENV PROJECT=movies
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY $REQUIREMENTS .

RUN apk add --no-cache --virtual .build-deps git gcc musl-dev libffi-dev openssl-dev python3-dev cargo && \
    apk add --no-cache mariadb-dev && \
    pip3 install --no-cache-dir -r $REQUIREMENTS && \
    apk del .build-deps && \
    rm $REQUIREMENTS

COPY entrypoint.sh .
COPY src .

EXPOSE 8000

CMD ["./entrypoint.sh"]
