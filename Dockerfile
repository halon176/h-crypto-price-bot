FROM python:3.10

RUN mkdir /crypto_price_bot

WORKDIR crypto_price_bot

COPY requirements.txt .

ENV TOKEN=<telegram_bot_token>

RUN echo "TOKEN=${TOKEN}" > /app/.env

RUN pip install -r requirements.txt

COPY . .

CMD python src/main.py
