FROM python:3.11.0-alpine3.16

ENV PROJECT=movies
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml .
COPY poetry.lock .

# Removing poetry manually because it doesn't work otherwise
RUN apk add --no-cache --virtual .build-deps git gcc musl-dev libffi-dev openssl-dev python3-dev cargo && \
    apk add --no-cache mariadb-dev && \
    pip3 install --no-cache-dir poetry==2.1.3 && \
    poetry config virtualenvs.create false --local && \
    poetry install --without dev --no-root && \
    apk del .build-deps && \
    rm -rf /usr/local/lib/python3.11/site-packages/poetry && \
    rm poetry.toml poetry.lock pyproject.toml

COPY entrypoint.sh .
COPY src .

EXPOSE 8000

CMD ["./entrypoint.sh"]
