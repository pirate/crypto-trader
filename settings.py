API_TYPE = 'GEMINI'
API_VERSION = 1
API_URL = 'https://api.gemini.com'
API_WS_URL = 'wss://api.gemini.com'
STARTING_NONCE = 120


USD_ORDER_AMT = 1.00
MAX_LOSS_RATIO = -0.006
MAX_GAIN_RATIO = 0.01
MAX_ACTIVE_ORDERS = 3
OVERPAY_RATIO = 0.005

from secrets import *


def get_nonce(min_nonce: int=STARTING_NONCE) -> int:
    last = min_nonce
    try:
        with open('.last_nonce.txt', 'r') as f:
            last = int(f.read().strip())
    except Exception:
        pass

    last = last if last > min_nonce else min_nonce

    with open('.last_nonce.txt', 'w') as f:
        last += 1
        f.write(str(last))

    return last


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
