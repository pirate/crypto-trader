import os
import json

from datetime import datetime
from decimal import Decimal

from symbols import Order, Currency
from gemini_api import order_status

### Logging & Persistence

def save_price(path: str, price: Currency) -> None:
    ts = round(datetime.now().timestamp())

    with open(os.path.join(path, 'price-history.csv'), 'a+', encoding='utf-8') as f:
        f.write(f'{ts},{price.amt}\n')


def save_order(path: str, order: Order) -> None:
    with open(os.path.join(path, 'order-history.json'), 'a+', encoding='utf-8') as f:
        f.write(f'{json.dumps(order.data)}\n')

def load_active_orders(path: str) -> dict:
    active_orders = {}
    with open(os.path.join(path, 'active-orders.json'), 'r', encoding='utf-8') as f:
        for line in f:
            order = Order(json.loads(line.strip()))
            active_orders[order.id] = order
            print(f' - {order.id}: {order}')
    return active_orders

def save_active_orders(path: str, orders: dict) -> None:
    with open(os.path.join(path, 'active-orders.json'), 'w', encoding='utf-8') as f:
        for order in orders.values():
            f.write(f'{json.dumps(order.data)}\n')


def load_closed_orders(path: str) -> dict:
    closed_orders = {}
    with open(os.path.join(path, 'closed-orders.json'), 'r', encoding='utf-8') as f:
        for line in f:
            buy_order_str, sell_order_str = line.strip().split('->', 1)
            buy_order = Order(json.loads(buy_order_str))
            sell_order = Order(json.loads(sell_order_str))
            closed_orders[buy_order.id] = {
                'buy': buy_order,
                'sell': sell_order,
            }
            print(f' - {sell_order.id}: {sell_order}')
    return closed_orders

def save_closed_orders(path: str, orders: dict) -> None:
    with open(os.path.join(path, 'closed-orders.json'), 'w', encoding='utf-8') as f:
        for buy_id, pair in orders.items():
            buy_order, sell_order = pair['buy'], pair['sell']
            f.write(f'{json.dumps(buy_order.data)}->{json.dumps(sell_order.data)}\n')
