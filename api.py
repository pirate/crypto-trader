import requests
import base64
import hmac
import json
from time import sleep
from hashlib import sha384
from websocket import create_connection

from settings import (
    API_VERSION,
    API_URL,
    API_WS_URL,
    API_KEY,
    API_SECRET,
    get_nonce,
    retry_if_exception,
)

from symbols import Order, Currency, currency_by_symbol


class RateLimitExceeded(Exception):
    pass

### API Base Methods

def base_headers(url: str, request_json: dict=None) -> dict:
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

# @retry_if_exception
def request(url: str, request_json: dict=None, method='POST', public: bool=False) -> dict:
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

# @retry_if_exception
def websocket_request(url, request_json: dict=None):
    headers = base_headers(url, request_json)

    return create_connection(
        f'{API_WS_URL}/v{API_VERSION}{url}',
        headers=headers,
    )


### API REST Methods

def heartbeat() -> None: 
    response = request('/heartbeat')
    if not response['result']:
        raise Exception('Heartbeat request failed!')

def ticker(symbol: str) -> dict:
    return request(f'/pubticker/{symbol}', method='GET', public=True)

def new_order(side: str, symbol: str, amt: Currency, price: Currency) -> dict:
    return request('/order/new', {
        # "client_order_id": client_order_id,
        "symbol": symbol,
        "amount": str(amt),
        "price": str(price),
        "side": side,
        "type": "exchange limit",
    })

def order_status(order_id: str) -> dict: 
    # https://docs.gemini.com/rest-api/#order-status
    return request('/order/status', {'order_id': order_id})

### API WebSocket Methods

def order_events(order: Order):
    ws = websocket_request('/order/events', {'order_id': order.id})
    while True:
        yield json.loads(ws.recv())
