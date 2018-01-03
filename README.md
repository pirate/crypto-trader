# Crypto Trading Bot Framework using the Gemini Exchange
:moneybag: Python bindings for trading Bitcoin, Ethereum, & USD on the Gemini.com Exchange API.

---
<img src="https://nicksweeting.com/crypto-trader.png" width="600px"/>

Example Usage:
```python
import gemini_api as api
from symbols import Order, ETH, USD

# REST API Functions https://docs.gemini.com/rest-api/#requests
last_price_info = api.ticker('ethusd')
last_price = USD(last_price_info['last'])
buy_order = Order(api.new_order('buy', 'ethusd', ETH(0.001), last_price))
updated_order = Order(api.order_status(buy_order.id))

# Realtime WebSocket Events  https://docs.gemini.com/websocket-api/#websocket-request
for event in order_events('2341241241'):
    print(event)
```

It also comes with an example bot strategy that makes some random initial buys and triggers sells once a certain threshold amount of money is made or lost.

**Usage:**
```bash
open https://exchange.gemini.com/settings/api  # Get an API key 
cp secrets_default.py secrets.py               # Save your API Key

pip3 install -r requirements.txt               # Install dependencies
nano settings.py                               # Confirm your bot parameters
python3 ./example.py ethusd                    # Run the example theshold bot
```

**Config:**
```bash
nano secrets.py   # edit API key
nano settings.py  # tweak bot parameters
```

**MyPy Type-Checing:**
```bash
env MYPYPATH=./stubs mypy example.py
```

## API Documentation

```python
import gemini_api as api
from symbols import Order, USD, BTC, ETH
```

**Supported Currency Types:**
 - `Currency`: Base type for all curencies, don't use it directly.
 - `USD`: US Dollar `USD(1.25)`
 - `BTC`: Bitcoin   `BTC(0.000001)`
 - `ETH`: Ethereum  `ETH(0.0001)`

**Order Type:**
All API functions that deal with order data like `new_order` or `order_status` return a raw json dict from Gemini with the schema below.  It can be converted to a type-checked python object by using `Order(order_json)`.
```json
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
order_id = buy_order.id
```

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

**`order_status(order_id: str) -> dict`:**
Get the updated order info json from Gemini for a given order_id, e.g.:
```python
buy_order = Order(api.order_status('44375901'))
print(buy_order.filled_amt)
```

## Strategy Information

`example.py` is a simple example bot that randomly creates some initial buys, then sells the moment it makes a certain threshold percentage of profit.

It might profit if the market is trending upwards, but generally this strategy [doesn't work](https://gist.github.com/pirate/eac582480aa34b5adda9e6adc1878190) if you want to make any real money.  This code serves as a boilerplate example upon which to build other, more advanced bots.

This type of tight, risk-averse bot will only make small profits because it never waits for big upward trends to max out, it sells as soon as it goes in the green.  The days where it starts in the red and stays there also end up sucking much of the profit away.

## TODOS:

* Write a meta-trader that spawns multiple traders with tweaked parameters to see which ones make the most money
* Add GDAX/Coinbase Exchange API bindings
* Add Bitfinex Exchange API bindings

## Disclaimer:

I'm not responsible for any money you lose from this code.  The code is MIT Licensed.
