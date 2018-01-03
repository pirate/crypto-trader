import os
from datetime import datetime
from decimal import Decimal

from symbols import Order
from gemini_api import order_status

### Logging & Persistence

def save_price(path: str, price: Decimal) -> None:
    ts = datetime.now().timestamp()

    with open(os.path.join(path, 'price-history.csv'), 'a+', encoding='utf-8') as f:
        f.write(f'{ts},{price}\n')

def save_order(path: str, order: Order) -> None:
    with open(os.path.join(path, 'order-history.csv'), 'a+', encoding='utf-8') as f:
        f.write(f'{order.timestamp},{order.id},{order.side},{order.symbol},{order.original_amount},{order.price}\n')

def load_active_orders(path: str) -> dict:
    active_orders = {}
    try:
        with open(os.path.join(path, 'active-orders.csv'), 'r', encoding='utf-8') as f:
            for line in f:
                order = Order(order_status(line.split(',')[1]))
                active_orders[order.id] = order
    except Exception as e:
        print(e)
    return active_orders

def save_active_orders(path: str, orders: dict) -> None:
    with open(os.path.join(path, 'active-orders.csv'), 'w', encoding='utf-8') as f:
        for order in orders.values():
            f.write(f'{order.timestamp},{order.id},{order.side},{order.symbol},{order.original_amount},{order.price}\n')

def load_closed_orders(path: str) -> dict:
    closed_orders = {}
    try:
        with open(os.path.join(path, 'closed-orders.csv'), 'r', encoding='utf-8') as f:
            for line in f:
                buy_order = Order(order_status(line.split(',')[1]))
                sell_order = Order(order_status(line.split(',')[2]))
                closed_orders[buy_order.id] = {
                    'buy': buy_order,
                    'sell': sell_order,
                }
    except Exception as e:
        print(e)
    return closed_orders

def save_closed_orders(path: str, orders: dict) -> None:
    with open(os.path.join(path, 'closed-orders.csv'), 'w', encoding='utf-8') as f:
        for buy_id, obj in orders.items():
            sell_order = obj['sell']
            f.write(f'{sell_order.timestamp},{buy_id},{sell_order.id},{sell_order.side},{sell_order.symbol},{sell_order.original_amount},{sell_order.price}\n')
