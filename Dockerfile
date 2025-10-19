FROM python:3.13-slim-bullseye AS builder

WORKDIR /app

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && pip install --upgrade pip uv \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

FROM python:3.13-slim-bullseye AS production

LABEL org.opencontainers.image.source="https://github.com/halon176/h-crypto-price-bot"

WORKDIR /code

ENV PYTHONUNBUFFERED=1 \
    PATH="/code/.venv/bin:$PATH"

COPY --from=builder /app/.venv /code/.venv
COPY ./src /code/src

RUN apt-get purge -y --auto-remove && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

CMD ["python", "-m", "src.main"]
