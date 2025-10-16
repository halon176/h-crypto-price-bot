FROM python:3.13-slim-bullseye as builder

WORKDIR /tmp

RUN pip install --upgrade pip
RUN pip install uv

COPY pyproject.toml uv.lock* /tmp/

RUN uv sync

FROM python:3.13-slim-bullseye as production

LABEL org.opencontainers.image.source="https://github.com/halon176/h-crypto-price-bot"

WORKDIR /code
ENV PYTHONUNBUFFERED=1

COPY --from=builder /tmp/.venv /code/.venv
ENV PATH="/code/.venv/Scripts:$PATH"

COPY ./src /code/src

RUN rm -rf /tmp/* /var/tmp/*

CMD ["python", "-m", "src.main"]
