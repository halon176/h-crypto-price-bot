FROM python:3.12-slim-bullseye as requirements-stage

WORKDIR /tmp

RUN pip install --upgrade pip

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.12-slim-bullseye as production-stage

LABEL org.opencontainers.image.source="https://github.com/halon176/h-crypto-price-bot"

WORKDIR /code

ENV PYTHONUNBUFFERED=1

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

RUN apt update && apt dist-upgrade -y && apt install -y --no-install-recommends build-essential && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r /code/requirements.txt && \
    apt-get purge -y --auto-remove build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY ./src /code/src

RUN rm -rf /tmp/* /var/tmp/*

CMD ["python", "-m", "src.main"]
