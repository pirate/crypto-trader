import os

API_TYPE = 'GEMINI'
API_VERSION = 1
API_URL = 'https://api.gemini.com'
API_WS_URL = 'wss://api.gemini.com'
STARTING_NONCE = 120

SYMBOL = 'ethusd'       # currency pair to trade
POLL_DELAY = 30         # runloop interval in seconds
USD_ORDER_AMT = 1.00    # amount to use when making new orders
MAX_GAIN_RATIO = 0.01   # maximum percentage gains before selling the order
MAX_LOSS_RATIO = -0.006 # maximum percentage losses before selling the order
MAX_ACTIVE_ORDERS = 3   # maximum number of active orders to track
OVERPAY_RATIO = 0.005   # percentage to pay over current price in order to guarantee orders closing quickly

USD_MAX_NET_GAINS = 100  # total maximum USD gains before quitting the program
USD_MAX_NET_LOSS = -20   # total maximum USD losses before quitting the program

DATA_DIR = f'./data/{SYMBOL}'  # where to store the state and logs

from secrets import *


try:
    os.makedirs(DATA_DIR)
except Exception:
    pass
