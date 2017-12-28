#!/usr/bin/env python3
import os

from datetime import datetime
from time import sleep

from api import ticker, new_order, order_status, heartbeat
from symbols import Order, currency_pair_by_symbol
from settings import (
    POLL_DELAY,
    SYMBOL,
    USD_ORDER_AMT,
    MAX_LOSS_RATIO,
    MAX_GAIN_RATIO,
    MAX_ACTIVE_ORDERS,
    OVERPAY_RATIO,
    USD_MAX_NET_GAINS,
    USD_MAX_NET_LOSS,
    DATA_DIR,
)


### Logging & Persistence

def save_price(price) -> None:
    ts = datetime.now().timestamp()

    with open(os.path.join(DATA_DIR, 'price-history.csv'), 'a+', encoding='utf-8') as f:
        f.write(f'{ts},{SYMBOL},{price}\n')

def save_order(order: Order) -> None:
    with open(os.path.join(DATA_DIR, 'order-history.csv'), 'a+', encoding='utf-8') as f:
        f.write(f'{order.timestamp},{order.id},{order.side},{order.symbol},{order.original_amount},{order.price}\n')

def load_active_orders() -> dict:
    active_orders = {}
    try:
        with open(os.path.join(DATA_DIR, 'active-orders.csv'), 'r', encoding='utf-8') as f:
            for line in f:
                order = Order(order_status(line.split(',')[1]))
                active_orders[order.id] = order
    except Exception as e:
        pass
    return active_orders

def save_active_orders(orders: dict) -> None:
    with open(os.path.join(DATA_DIR, 'active-orders.csv'), 'w', encoding='utf-8') as f:
        for order in orders.values():
            f.write(f'{order.timestamp},{order.id},{order.side},{order.symbol},{order.original_amount},{order.price}\n')

def load_closed_orders() -> dict:
    closed_orders = {}
    try:
        with open(os.path.join(DATA_DIR, 'closed-orders.csv'), 'r', encoding='utf-8') as f:
            for line in f:
                order = Order(order_status(line.split(',')[1]))
                closed_orders[order.id] = order
    except Exception as e:
        pass
    return closed_orders

def save_closed_orders(orders: dict) -> None:
    with open(os.path.join(DATA_DIR, 'closed-orders.csv'), 'w', encoding='utf-8') as f:
        for order in orders.values():
            f.write(f'{order.timestamp},{order.id},{order.side},{order.symbol},{order.original_amount},{order.price}\n')


### Main

adjust = lambda price, ratio: price + (price * ratio)

def price_stream(symbol: str):
    while True:
        yield float(ticker(symbol)['last'])

def runloop(symbol: str):
    active_orders = load_active_orders()
    closed_orders = load_closed_orders()

    if active_orders:
        print(f'Loaded {len(active_orders)} active orders.')
    else:
        print(f'Creating {MAX_ACTIVE_ORDERS} orders of ${USD_ORDER_AMT} each.')

    print(
        f'Selling if price rises by {MAX_GAIN_RATIO * 100}% or lowers by '
        f'{MAX_LOSS_RATIO * 100}%.'
    )

    A, B = currency_pair_by_symbol[symbol]

    for price in price_stream(symbol):
        save_price(price)
        print('=============================================')
        print(f'Current Price: ${price}')

        # Update the status of all the active orders
        for id, order in active_orders.items():
            if not order.is_finished:
                active_orders[id] = Order(order_status(order.id))

        # Perform the initial buys and add them to active orders
        while len(active_orders) < MAX_ACTIVE_ORDERS:
            buy_order = Order(new_order(
                side='buy',
                symbol=symbol,
                amt=A(USD_ORDER_AMT / price),
                price=B(adjust(price, OVERPAY_RATIO)),
            ))
            active_orders[buy_order.id] = buy_order
            save_order(buy_order)

        # For each order, sell it if it's gained or lost enough to hit its limit
        for id, order in active_orders.items():
            if (price > adjust(price, MAX_GAIN_RATIO) or
                  price < adjust(price, MAX_LOSS_RATIO)):
                
                buy_order = active_orders.pop(id)
                sell_order = Order(new_order(
                    side='sell',
                    symbol=symbol,
                    amt=buy_order.amt,
                    price=B(adjust(price, -OVERPAY_RATIO)),
                ))

                closed_orders[id] = {
                    'buy': buy_order,
                    'sell': sell_order,
                    'net': sell_order.usd_amt - buy_order.usd_amt,
                }
                save_order(buy_order)

        save_active_orders(active_orders)
        save_closed_orders(closed_orders)

        # Print order table status
        net_gains = sum(order['net'] for order in closed_orders.values())
        print(f'Active Orders:')
        print('\n'.join(f'{id}: {order}' for id, order in active_orders.items()))
        print(f'Closed Orders:')
        print('\n'.join(f'{id}: {order}' for id, order in closed_orders.items()))
        print(f'Net Gains: ${net_gains}')

        # Quit if total net gains or losses hit the limit
        if net_gains > USD_MAX_NET_GAINS:
            print('Success! Stopping because net gains > USD_MAX_NET_GAINS')
            break
        elif net_gains < USD_MAX_NET_LOSS:
            print('Failed! Stopping because net gains < USD_MAX_NET_LOSS')
            break

        # Sleep for the poll delay, optionally sending a heartbeat if it's long
        if POLL_DELAY > 15:
            sleep(15)
            heartbeat()
            sleep(POLL_DELAY - 15)
        else:
            sleep(POLL_DELAY)


if __name__ == '__main__':
    try:
        runloop(SYMBOL)
    except (EOFError, KeyboardInterrupt):
        print('Stopped!')
