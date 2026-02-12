# HCryptoPrice

[![build](https://github.com/halon176/h-crypto-price-bot/workflows/CI/badge.svg)](https://github.com/halon176/h-crypto-price-bot/actions/workflows/docker-image.yml)
[![tests](https://github.com/halon176/h-crypto-price-bot/workflows/Run%20Unit%20Test%20via%20Pytest/badge.svg)](https://github.com/halon176/h-crypto-price-bot/actions/workflows/run_tests.yml)
[![coverage](https://img.shields.io/badge/coverage-97%25-brightgreen)](https://github.com/halon176/h-crypto-price-bot/tree/master/tests)
[![license: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/halon176/h-crypto-price-bot/blob/master/LICENSE)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)

A Python-based Telegram bot for fetching real-time cryptocurrency prices from CoinGecko. Provides price data, historical charts, market cap rankings, and Ethereum gas prices.

**Live bot**: [@h_crypto_price_bot](https://t.me/h_crypto_price_bot)

For advanced features like rate limits and usage tracking, check out the [hcpb-api](https://github.com/halon176/hcpb-api) repository (work in progress).

## Installation

### Manual

1. Make sure you have Python 3.13 installed:

   ```bash
   python --version
   ```

2. Clone the repository:

   ```bash
   git clone https://github.com/halon176/h-crypto-price-bot.git
   cd h-crypto-price-bot
   ```

3. Install dependencies using [uv](https://docs.astral.sh/uv/):

   ```bash
   uv sync
   ```

4. Create a Telegram bot via [BotFather](https://core.telegram.org/bots#6-botfather) and copy the token.

5. Set up environment variables:

   ```bash
   export TELEGRAM_TOKEN=<your_telegram_bot_token>
   export ETHSCAN_API_KEY=<your_etherscan_api_key>  # Required for gas prices
   export CMC_API_KEY=<your_coinmarketcap_api_key>  # Optional
   export API_URL=<api_url>  # Optional
   ```

6. Run the bot:

   ```bash
   uv run python src/main.py
   ```

### Docker

1. Clone the repository:

   ```bash
   git clone https://github.com/halon176/h-crypto-price-bot.git
   ```

2. Build the Docker image:

   ```bash
   docker build -t h-crypto-price h-crypto-price-bot/.
   ```

3. Run the container:

   ```bash
   # Basic setup
   docker run -d \
     -e TELEGRAM_TOKEN=<your_telegram_bot_token> \
     --name h-crypto-price \
     h-crypto-price

   # With optional API keys
   docker run -d \
     -e TELEGRAM_TOKEN=<your_telegram_bot_token> \
     -e ETHSCAN_API_KEY=<your_etherscan_api_key> \
     -e CMC_API_KEY=<your_coinmarketcap_api_key> \
     --name h-crypto-price \
     h-crypto-price
   ```

## Usage

Get cryptocurrency prices using `/p` followed by the symbol:

```
/p btc
/p eth
/p sol
```

Type `/help` for a full list of available commands.

## Contributing

Contributions are welcome! If you have any suggestions or bug reports, please open an issue on the GitHub repository.

## License

This project is licensed under the MIT License. See the LICENSE file for details.