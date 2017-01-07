FROM alpine

ARG PYTHON_COMMONS_HOST
ARG PYTHON_COMMONS_SCHEME
ARG PYTHON_COMMONS_PORT

RUN apk --quiet update && \
    apk --quiet add \
        --no-cache \
        gcc \
        git \
        libpq \
        libmagic \
        musl-dev \
        postgresql-dev \
        py-virtualenv \
        python3-dev \
        python3 && \
    pyvenv /venv && \
    mkdir -p /big_repos

COPY ./requirements.txt /
COPY ./run.py /

RUN source /venv/bin/activate && \
    pip --quiet install \
        --no-cache-dir \
        --trusted-host ${PYTHON_COMMONS_HOST} \
        --extra-index-url ${PYTHON_COMMONS_SCHEME}${PYTHON_COMMONS_HOST}:${PYTHON_COMMONS_PORT} \
        --requirement /requirements.txt

ENV PYTHONPATH /pylibs
CMD ["/venv/bin/python", "-m", "run"]
