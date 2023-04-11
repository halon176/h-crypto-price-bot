## HCryptoPrice

HCryptoPrice is a Python-based bot that fetches real-time cryptocurrency prices from Coingecko and presents them in an easy-to-understand format on Telegram. It also offers historical price data, market cap rankings.

## Installation

### Manual

1) First, make sure you have Python 3.10 installed on your machine. You can check your Python version by opening a terminal and running the following command: 

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

5) Once you have created your bot, copy the bot token that BotFather gave you. With the following command create the .env file and insert the token inside it, making sure to replace **<telegram_bot_token>**
```
echo "TOKEN=<telegram_bot_token>" > .env
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

2) Enter into the project directory, and then launch the 'docker build' command to build your Docker image.

```
cd h-crypto-price-bot
docker build .
```
3) At the end of the process, you should get a result similar to this:
```
Successfully built 8924db6fccc3
```
This means that everything went smoothly. Now you can start your container by running:
```
docker run 8924db6fccc3
```

Of course, make sure to replace '8924db6fccc3' with the number of your image.

The bot is now up and running within the Docker container!

## Usage
The bot can receive requests using the command **/p** followed by the cryptocurrency symbol, for example:
```
/p btc
/p eth
/p cro
```

## Roadmap
- [ ] Create a method to select tokens with the same symbol (currently, the bot displays the one with the highest market capitalization).
- [ ] Create a function that aligns spaces to make text appear more uniform within the message with the data.
- [ ] Display a chart showing the price trend of a single coin in different selectable timeframes.
- [ ] Create the possibility to query other APIs such as Binance or CoinMarketCap.

## Contributing
Contributions are welcome! If you have any suggestions or bug reports, please open an issue on the GitHub repository.

## License
This project is licensed under the MIT License. See the LICENSE file for details.