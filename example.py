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

import gemini_api as api
from symbols import USD, Order, currency_pair_by_symbol, currency_art
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
net_profit = lambda pair: pair['sell'].filled_amt - pair['buy'].filled_amt

def runloop(symbol: str):
    """that's right, it's an 84 line function, read it and weep"""

    print(currency_art[symbol])
    print(
        f'This bot buys random starting amounts, then sells if the price\n'
        f'raises by {round(MAX_GAIN_RATIO * 100, 2)}% or '
        f'lowers by {round(MAX_LOSS_RATIO * 100, 2)}%\n'
        '(you will probably not make any money by running this)\n'
        '====================================================================='
    )

    data_dir = os.path.join(DATA_DIR, symbol)
    if os.path.exists(data_dir):
        print(f'[i] Loading order data from {data_dir}:')
        active_orders = load_active_orders(data_dir)
        closed_orders = load_closed_orders(data_dir)
        print(f'[√] Loaded {len(active_orders) + len(closed_orders)} orders from {data_dir} ({len(active_orders)} active orders).')
        print('=====================================================================')
    else:
        os.makedirs(data_dir)
        active_orders = {}
        closed_orders = {}

    A, B = currency_pair_by_symbol[symbol]  # 'ethusd' => (ETH, USD)
    net_gains = sum(net_profit(pair) for pair in closed_orders.values())

    while True:
        now = round(datetime.now().timestamp())
        ticker_status = api.ticker(symbol)
        price = B(Decimal(ticker_status['last']))
        volume = USD(Decimal(ticker_status['volume']['USD']))
        save_price(data_dir, price)
        print(f'{now}   Price: {repr(price)}   Volume: {repr(volume)}   Net Gains: {repr(net_gains)}')

        # Update the status of all the active orders
        for id, order in active_orders.items():
            if not order.is_filled:
                active_orders[id] = Order(api.order_status(order.id))

        # Perform the initial buys and add them to active orders
        while len(active_orders) < MAX_ACTIVE_ORDERS:
            rand_amt = Decimal(randint(0, 100)/100) * (USD_MAX_ORDER_AMT - USD_MIN_ORDER_AMT)
            order_amt = USD_MIN_ORDER_AMT + rand_amt

            buy_order = Order(api.new_order(
                side='buy',
                symbol=symbol,
                amt=A(order_amt / price.amt),
                price=add_percentage(price, OVERPAY_RATIO),
            ))
            active_orders[buy_order.id] = buy_order
            save_order(data_dir, buy_order)
            print(f'[>] Bought {repr(buy_order.buy_amt)} @ {repr(buy_order.price_amt)}')

        # For each order, sell it if it's gained or lost enough to hit its limit
        for id, order in active_orders.items():
            if (price > add_percentage(Decimal(order.price), MAX_GAIN_RATIO) or
                  price < add_percentage(Decimal(order.price), MAX_LOSS_RATIO)):
                
                buy_order = active_orders.pop(id)
                sell_price = add_percentage(price, -OVERPAY_RATIO)
                sell_order = Order(api.new_order(
                    side='sell',
                    symbol=symbol,
                    amt=buy_order.buy_amt,
                    price=sell_price,
                ))

                closed_orders[id] = {
                    'buy': buy_order,
                    'sell': sell_order,
                }
                save_order(data_dir, buy_order)
                direction = 'up' if sell_price > buy_order.price_amt else 'down'
                print(
                    f'[<] Sold {repr(buy_order.buy_amt)} @ {repr(sell_price)} {direction} '
                    f'from {repr(buy_order.price_amt)} for a net profit of: {repr(net_profit(closed_orders[id]))}'
                )
                break

        save_active_orders(data_dir, active_orders)
        save_closed_orders(data_dir, closed_orders)

        # print(f'Buys:')
        # print('\n'.join(f'{id}: {order}' for id, order in active_orders.items()))
        # print(f'Sells:')
        # print('\n'.join(f'{buy_id}: {pair["sell"]}' for buy_id, pair in closed_orders.items()))

        # Quit if total net gains or losses hit the limit
        net_gains = sum(net_profit(pair) for pair in closed_orders.values())
        if net_gains > USD_MAX_NET_GAINS:
            print('[√] Success! Stopping because net gains > USD_MAX_NET_GAINS')
            break
        elif net_gains < USD_MAX_NET_LOSS:
            print('[X] Failed! Stopping because net gains < USD_MAX_NET_LOSS')
            break

        # Sleep for the poll delay, optionally sending a heartbeat if it's long
        if POLL_DELAY > 15:
            sleep(15)
            api.heartbeat()
            sleep(POLL_DELAY - 15)
        else:
            sleep(POLL_DELAY)


if __name__ == '__main__':
    # e.g. ethusd, btcusd
    trading_pair_symbol = sys.argv[1] if len(sys.argv) > 1 else SYMBOL
    try:
        runloop(trading_pair_symbol)
    except (EOFError, KeyboardInterrupt):
        print(f'\n[√] Saved active orders to {DATA_DIR}/{trading_pair_symbol}')
