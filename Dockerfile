FROM alpine

RUN apk --quiet update && \
    apk --quiet add \
        --no-cache \
        gcc \
        libpq \
        musl-dev \
        postgresql-dev \
        py-virtualenv \
        python3-dev \
        python3 && \
    pyvenv /venv

ARG PYTHON_COMMONS_HOST
ARG PYTHON_COMMONS_SCHEME
ARG PYTHON_COMMONS_PORT

COPY requirements.txt /

RUN source /venv/bin/activate && \
    pip install --upgrade pip && \
    pip install \
        --no-cache-dir \
        --trusted-host ${PYTHON_COMMONS_HOST} \
        --extra-index-url ${PYTHON_COMMONS_SCHEME}${PYTHON_COMMONS_HOST}:${PYTHON_COMMONS_PORT} \
        --requirement /requirements.txt

ENV PYTHONPATH /usr/app/src
COPY run.py /
COPY leaderboard /usr/app/src/leaderboard

CMD ["/venv/bin/python", "-m", "run"]
