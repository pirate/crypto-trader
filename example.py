#!/usr/bin/env python3
"""
Usage:
    pip install -r requirements.txt
    ./example.py ethusd

Config:
    cp secrets_default.py secrets.py
    nano secrets.py   # edit API key
    nano settings.py  # tweak bot parameters

MyPy Type-Checing:
    env MYPYPATH=./stubs mypy example.py
"""

import os
import sys

from random import randint
from datetime import datetime
from time import sleep
from decimal import Decimal

from gemini_api import ticker, new_order, order_status, heartbeat
from symbols import Order, currency_pair_by_symbol, currency_art
from data import (
    save_price,
    save_order,
    load_active_orders,
    load_closed_orders,
    save_active_orders,
    save_closed_orders,
)
from settings import (
    POLL_DELAY,
    SYMBOL,
    USD_MIN_ORDER_AMT,
    USD_MAX_ORDER_AMT,
    MAX_LOSS_RATIO,
    MAX_GAIN_RATIO,
    MAX_ACTIVE_ORDERS,
    OVERPAY_RATIO,
    USD_MAX_NET_GAINS,
    USD_MAX_NET_LOSS,
    DATA_DIR,
)

### Main

add_percentage = lambda price, ratio: price + (price * ratio)

def runloop(symbol: str):
    """that's right, it's an 84 line function, read it and weep"""

    data_path = os.path.join(DATA_DIR, symbol)
    if not os.path.exists(data_path):
        os.makedirs(data_path)

    active_orders = load_active_orders(data_path)
    closed_orders = load_closed_orders(data_path)

    if active_orders:
        print(f'[i] Loaded {len(active_orders) + len(closed_orders)} orders from {DATA_DIR}')
    else:
        print(
            f'[+] Creating {MAX_ACTIVE_ORDERS} orders between '
            f'${USD_MIN_ORDER_AMT} and {USD_MAX_ORDER_AMT} each.'
        )

    print(currency_art[symbol])
    print(
        f'This bot buys random starting amounts, then sells if the price\n'
        f'raises by {round(MAX_GAIN_RATIO * 100, 2)}% or '
        f'lowers by {round(MAX_LOSS_RATIO * 100, 2)}%\n'
        '(you will probably not make any money by running this)'
    )

    A, B = currency_pair_by_symbol[symbol]  # 'ethusd' => (ETH, USD)

    while True:
        price = Decimal(ticker(symbol)['last'])
        save_price(data_path, price)
        print('=================================================================')
        print(f'Current Price: ${price} {symbol.upper()}')

        # Update the status of all the active orders
        for id, order in active_orders.items():
            if not order.is_filled:
                active_orders[id] = Order(order_status(order.id))

        # Perform the initial buys and add them to active orders
        while len(active_orders) < MAX_ACTIVE_ORDERS:
            rand_pct = Decimal(randint(0, 100)/100) * (USD_MAX_ORDER_AMT - USD_MIN_ORDER_AMT)
            order_amt = USD_MIN_ORDER_AMT + rand_pct

            buy_order = Order(new_order(
                side='buy',
                symbol=symbol,
                amt=A(order_amt / price),
                price=B(add_percentage(price, OVERPAY_RATIO)),
            ))
            active_orders[buy_order.id] = buy_order
            save_order(data_path, buy_order)

        # For each order, sell it if it's gained or lost enough to hit its limit
        for id, order in active_orders.items():
            if (price > add_percentage(price, MAX_GAIN_RATIO) or
                  price < add_percentage(price, MAX_LOSS_RATIO)):
                
                buy_order = active_orders.pop(id)
                sell_order = Order(new_order(
                    side='sell',
                    symbol=symbol,
                    amt=buy_order.amt,
                    price=B(add_percentage(price, -OVERPAY_RATIO)),
                ))

                closed_orders[id] = {
                    'buy': buy_order,
                    'sell': sell_order,
                    'net': sell_order.filled_amt - buy_order.filled_amt,
                }
                save_order(data_path, buy_order)

        save_active_orders(data_path, active_orders)
        save_closed_orders(data_path, closed_orders)

        # Print order table status
        net_gains = sum(order['net'] for order in closed_orders.values())
        print(f'Buys:')
        print('\n'.join(f'{id}: {order}' for id, order in active_orders.items()))
        print(f'Sells:')
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
    if len(sys.argv) > 1:
        symbol = sys.argv[1]
    else:
        symbol = SYMBOL
    try:
        runloop(SYMBOL)
    except (EOFError, KeyboardInterrupt):
        print(f'\n[√] Saved active orders to {DATA_DIR}/{symbol}')
