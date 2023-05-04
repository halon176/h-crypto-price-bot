FROM python:3.11.3

LABEL org.opencontainers.image.source="https://github.com/halon176/h-crypto-price-bot"

RUN mkdir /crypto_price_bot

WORKDIR crypto_price_bot

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD python src/main.py
