FROM python:3.10

RUN mkdir /crypto_price_bot

WORKDIR crypto_price_bot

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD python src/main.py
