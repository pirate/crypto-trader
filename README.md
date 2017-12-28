# Crypto Trading Bot Framework using the Gemini Exchange
:moneybag: Python bindings for trading Bitcoin, Ethereum, & USD on the Gemini.com Exchange API.

---
<img src="https://nicksweeting.com/crypto-trader.png" width="600px"/>

Example Usage:
```python
from symbols import Order, ETH, USD
from gemini_api import ticker order_status, new_order

# REST API Functions
# https://docs.gemini.com/rest-api/#requests
price_info = ticker('ethusd')
result = Order(order_status('2341241241'))
result = Order(new_order('buy', 'ethusd', ETH(0.001), USD(760)))

# Realtime WebSocket Events
# https://docs.gemini.com/websocket-api/#websocket-request
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

## Bot Information

`example.py` is a simple bot that randomly creates some initial buys, then sells the moment it makes a certain threshold percentage of profit.

It might profit if the market is trending upwards, but generally this strategy [doesn't work](https://gist.github.com/pirate/eac582480aa34b5adda9e6adc1878190) if you want to make any real money.  This code serves as a boilerplate example upon which to build other, more advanced bots.

This type of tight, risk-averse bot will only make small profits because it never waits for big upward trends to max out, it sells as soon as it goes in the green.  The days where it starts in the red and stays there also end up sucking much of the profit away.

## TODOS:

* Write a meta-trader that spawns multiple traders with tweaked parameters to see which ones make the most money
* Add GDAX/Coinbase Exchange API bindings
* Add Bitfinex Exchange API bindings

## Disclaimer:

I'm not responsible for any money you lose from this code.  The code is MIT Licensed.
