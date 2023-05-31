# HCryptoPrice

[![build](https://github.com/halon176/h-crypto-price-bot/workflows/CI/badge.svg)](https://github.com/halon176/h-crypto-price-bot/actions/workflows/docker-image.yml)
[![license: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/halon176/h-crypto-price-bot/blob/master/LICENSE)



HCryptoPrice is a Python-based bot that fetches real-time cryptocurrency prices from Coingecko and presents them in an
easy-to-understand format on Telegram. It also offers historical price data, market cap rankings.

Here's a working version of the bot: [@h_crypto_price_bot](https://t.me/h_crypto_price_bot)

## Installation

### Manual

1) First, make sure you have Python 3.11 installed on your machine. You can check your Python version by opening a terminal and running the following command:

```
python --version
```

2) Next, clone the h-crypto-price-bot repository to your local machine. You can do this by running the following command in your terminal:

```
git clone https://github.com/halon176/h-crypto-price-bot.git
```

3) Change into the directory where the bot's code is located, then install the required Python packages by running the following commands:

```
cd h-crypto-price-bot
pip install -r requirements.txt
```

4) Create a new Telegram bot by following the instructions in the Telegram Bot API documentation: https://core.telegram.org/bots#6-botfather

5) After creating your bot, copy the token provided by BotFather. Then, set up an environment variable named TOKEN with
the bot token using the following command, replacing **<telegram_bot_token>** with your bot token:
```
export TELEGRAM_TOKEN=<telegram_bot_token>
```
To use the gas price feature, you must include an Etherscan API key.
```
export ETHSCAN_API_KEY=<etherscan_api_key>
```


6) Run the bot by running the following command:

```
python src/main.py
```


Your bot should now be up and running! You can add it to a Telegram group or start a chat with it to test it out.

### Docker

1) Clone the h-crypto-price-bot repository to your local machine. You can do this by running the following command in your terminal:

```
git clone https://github.com/halon176/h-crypto-price-bot.git
```

2) Launch the 'docker build' command to build your Docker image.

```
docker build -t h-crypto-price h-crypto-price-bot/.
```
3) Now you can start the container using the command, replacing **<telegram_bot_token>** with your bot token:

```
docker run -d -e TELEGRAM_TOKEN=<telegram_bot_token> --name h-crypto-price h-crypto-price
```

To use the gas price feature, you must include an Etherscan API key. ETHSCAN_API_KEY=<etherscan_api_key>

```
docker run -d -e TELEGRAM_TOKEN=<telegram_bot_token> -e ETHSCAN_API_KEY=<etherscan_api_key> --name h-crypto-price h-crypto-price
```


The bot is now up and running within the Docker container!

## Usage
The bot can receive requests using the command **/p** followed by the cryptocurrency symbol, for example:
```
/p btc
/p eth
/p cro
```
To display the list of all available commands, type `/help`



## Roadmap
- [ ] Display a chart showing the price trend of a single coin in different selectable timeframes.
- [ ] Create the possibility to query other APIs such as Binance or CoinMarketCap.

## Contributing
Contributions are welcome! If you have any suggestions or bug reports, please open an issue on the GitHub repository.

## License
This project is licensed under the MIT License. See the LICENSE file for details.