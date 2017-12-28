"""
Gemini API Bindings

    REST API: https://docs.gemini.com/rest-api/#requests
        public:
            /ticker
        private:
            /heartbeat
            /order/new
            /order/status

    WebSocket API: https://docs.gemini.com/websocket-api/#websocket-request
        private:
            /order/events
"""

import os
import base64
import hmac
import json
import requests

from time import sleep
from hashlib import sha384

from symbols import Order, Currency, currency_by_symbol
from settings import (
    API_VERSION,
    API_URL,
    API_WS_URL,
    API_KEY,
    API_SECRET,
    STARTING_NONCE,
    DATA_DIR,
)


class RateLimitExceeded(Exception):
    pass


def retry_if_exception(func):
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RateLimitExceeded:
            print(f'Rate limit exceeded! Retrying in 10 seconds...')
            sleep(10)
            return func(*args, **kwargs)
        except Exception as e:
            print(f'{func} raised {e}! Retrying one more time in 2 seconds...')
            sleep(2)
            return func(*args, **kwargs)
    return wrapped

def get_nonce(min_nonce: int=STARTING_NONCE) -> int:
    """nonce must always monotonically increase, so we track it in a file"""
    last = min_nonce
    try:
        with open(os.path.join(DATA_DIR, '.last_nonce.txt'), 'r') as f:
            last = int(f.read().strip())
    except Exception:
        pass

    last = last if last > min_nonce else min_nonce

    with open(os.path.join(DATA_DIR, '.last_nonce.txt'), 'w') as f:
        last += 1
        f.write(str(last))

    return last


### API Base Methods

def base_headers(url: str, request_json: dict=None) -> dict:
    """basic auth & content headers shared by the REST and WS API"""
    request_json = request_json or {}
    request_json['request'] = f'/v{API_VERSION}{url}'
    request_json['nonce'] = get_nonce()
    
    base_64 = base64.b64encode(json.dumps(request_json).encode())
    signature = hmac.new(API_SECRET.encode(), base_64, sha384).hexdigest()

    return {
        'X-GEMINI-APIKEY': API_KEY,
        'X-GEMINI-PAYLOAD': base_64,
        'X-GEMINI-SIGNATURE': signature,
    }

@retry_if_exception
def request(url: str, request_json: dict=None, method='POST', public: bool=False) -> dict:
    """Make an HTTP request to the Gemini API, public=True disables auth headers"""

    http_headers = {
        'Content-Type': "text/plain",
        'Content-Length': "0",
        'Cache-Control': "no-cache",
    }

    response = requests.request(
        method,
        f'{API_URL}/v{API_VERSION}{url}',
        headers={
            **http_headers,
            **({} if public else base_headers(url, request_json)),
        },
    )

    if response.status_code == 429:
        raise RateLimitExceeded

    return json.loads(response.text)

@retry_if_exception
def websocket_request(url, request_json: dict=None):
    """Subscribe to websocket messages from a Gemini API endpoint"""

    try:
        from websocket import create_connection
    except ImportError:
        print('The package websocket-client is required to use the WS api:')
        print('    pip install websocket-client')
        raise SystemExit(1)

    headers = base_headers(url, request_json)

    return create_connection(
        f'{API_WS_URL}/v{API_VERSION}{url}',
        headers=headers,
    )


### API REST Methods

def heartbeat() -> None:
    """send a keep-alive heartbeat ping to the Gemini API"""

    response = request('/heartbeat')
    if not response['result']:
        raise Exception('Heartbeat request failed!')

def ticker(symbol: str) -> dict:
    """fetch the current price and volume for a given symbol"""
    return request(f'/pubticker/{symbol}', method='GET', public=True)

def new_order(side: str, symbol: str, amt: Currency, price: Currency) -> dict:
    """create a new buy or sell order for a given symbol, amt, and price"""

    return request('/order/new', {
        # "client_order_id": client_order_id,
        "symbol": symbol,
        "amount": str(amt),
        "price": str(price),
        "side": side,
        "type": "exchange limit",
    })

def order_status(order_id: str) -> dict:
    """fetch the up-to-date order object for a given order id"""
    # https://docs.gemini.com/rest-api/#order-status
    return request('/order/status', {'order_id': order_id})


### API WebSocket Methods

def order_events(order_id: str):
    """subscibe to event updates for a given order id"""
    ws = websocket_request('/order/events', {'order_id': order_id})
    while True:
        yield json.loads(ws.recv())
