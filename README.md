# Full-Historical-of-Symbol-Kucoin
Get full historical candlestick data of a symbol from the Kocoin exchange



virtualenv -p python venv

source venv/bin/activate

pip install -r requirements.txt

python main.py -s "BTC-USDT" -i "1day" -key "<api_key>" -secret "<api_secret>" -passphrase "<api_passphrase>"
