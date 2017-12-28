import os

API_TYPE = 'GEMINI'
API_VERSION = 1
API_URL = 'https://api.gemini.com'
API_WS_URL = 'wss://api.gemini.com'
STARTING_NONCE = 120

SYMBOL = 'ethusd'
POLL_DELAY = 30
USD_ORDER_AMT = 1.00
MAX_LOSS_RATIO = -0.006
MAX_GAIN_RATIO = 0.01
MAX_ACTIVE_ORDERS = 3
OVERPAY_RATIO = 0.005

USD_MAX_NET_GAINS = 100
USD_MAX_NET_LOSS = -20

DATA_DIR = f'./data/{SYMBOL}'

try:
    os.makedirs(DATA_DIR)
except Exception:
    pass

from secrets import *
