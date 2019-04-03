# Crypto Trading Bot Framework using the Gemini Exchange
:moneybag: Python bindings for trading Bitcoin, Ethereum, & USD on the Gemini.com Exchange API.

---
## ARCHIVED: Use https://github.com/ccxt/ccxt

## Quickstart

1. **Download & install**
```bash
git clone https://github.com/pirate/cryto-trader.git
cd crypto-trader
pip3 install -r requirements.txt
```

2. **Open https://exchange.gemini.com/settings/api and get an API key & secret**
```bash
cp secrets_default.py secrets.py
nano secrets.py  # add key & secret here
```

3. **Start hacking!**
```python
import gemini_api as api
from symbols import Order, ETH, USD

current_price = USD(api.ticker('ethusd')['last'])
if current_price > USD(950.00):
    buy_order = Order(api.new_order('buy', 'ethusd', ETH(0.001), current_price))

    for event in order_events(buy_order.id):
        print(event)
```

4. **(Optional) run the example bot**
```bash
nano settings.py                   # Confirm your bot parameters
python3 ./example.py ethusd        # Run the example theshold bot
```

## Configuration

 - **API Key Secrets:** `secrets.py`
 - **Bot Settings:** `settings.py`

## API Documentation

```python
import gemini_api as api
from symbols import Order, USD, BTC, ETH
```

### Data Types

**Currencies:**
 
 - `symbols.USD`: US Dollar `USD(1.25)`
 - `symbols.BTC`: Bitcoin   `BTC(0.000001)`
 - `symbols.ETH`: Ethereum  `ETH(0.0001)`

All currency symbols are based on the base type `symbols.Currency`.

**Order:**
All API functions that deal with order data like `new_order` or `order_status` return a raw json dict from Gemini with the schema below.  It can be converted to a type-checked python object by using `Order(order_json)`.
```python
order_json = {
    "order_id": "44375901",
    "id": "44375901",
    "symbol": "btcusd",
    "exchange": "gemini",
    "avg_execution_price": "400.00",
    "side": "buy",
    "type": "exchange limit",
    "timestamp": "1494870642",
    "timestampms": 1494870642156,
    "is_live": False,
    "is_cancelled": False,
    "is_hidden": False,
    "was_forced": False,
    "executed_amount": "3",
    "remaining_amount": "0",
    "options": [],
    "price": "400.00",
    "original_amount": "3",
}
buy_order = Order(order_json)
order_id = buy_order.id       # values can be accessed as properties
```

### REST API Functions
The Gemini REST API functions documentation can be found here:  
https://docs.gemini.com/rest-api/#requests

**`api.ticker(symbol: str) -> dict`:**  
Get the ticker price info for a given symbol, e.g.:
```python
ticker_info = api.ticker('ethusd')
# {'bid': '914.00', 'ask': '914.44', 'volume': {'ETH': '94530.56656129', 'USD': '83955829.9730076926', 'timestamp': 1515014100000}, 'last': '915.39'}
last_price = USD(ticker_info['last'])
```

**`api.new_order(side: str, symbol: str, amt: Currency, price: Currency) -> dict`:**  
Submit a new order to Gemini, e.g:
```python
buy_order = Order(api.new_order('buy', 'ethusd', ETH(0.01), USD(965)))
sell_order = Order(api.new_order('sell', 'ethusd', ETH(0.01), USD(965)))
```

**`api.order_status(order_id: str) -> dict`:**  
Get the updated order info json from Gemini for a given order_id, e.g.:
```python
buy_order = Order(api.order_status('44375901'))
print(buy_order.filled_amt)
```

### WebSocket API Functions
The Gemini WebSocket API functions documentation can be found here:  
https://docs.gemini.com/websocket-api/#websocket-request

**`api.order_events(order_id: str) -> Generator[dict]`:**  
Get a live-updating stream of order events via WebSocket e.g.:
```python
for event in api.order_events('44375901'):
    print(event)
```

## Example Bot

<img src="https://i.imgur.com/Hi3EYym.png" width="500px"/>

`example.py` is a simple example bot that randomly creates some initial buys, then sells the moment it makes a certain threshold percentage of profit.

It might profit if the market is trending upwards, but generally this strategy [doesn't work](https://gist.github.com/pirate/eac582480aa34b5adda9e6adc1878190) if you want to make any real money.  This code serves as a boilerplate example upon which to build other, more advanced bots.

This type of tight, risk-averse bot will only make small profits because it never waits for big upward trends to max out, it sells as soon as it goes in the green.  The days where it starts in the red and stays there also end up sucking much of the profit away.

## Roadmap

* Write a meta-trader that spawns multiple traders with tweaked parameters to see which ones make the most money
* Add GDAX/Coinbase Exchange API bindings
* Add Bitfinex Exchange API bindings

## Developer Info

This library is built on Python 3.6 and uses MyPy for type checking.

**Check MyPy types:**
```bash
env MYPYPATH=./stubs mypy example.py
```

## Disclaimer

I'm not responsible for any money you lose from this code.  The code is MIT Licensed.
