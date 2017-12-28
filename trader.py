#!/usr/bin/env python3
from datetime import datetime
from time import sleep

from symbols import Order, ETH, USD
from api import ticker, new_order, order_status
from settings import (
    USD_ORDER_AMT,
    MAX_LOSS_RATIO,
    MAX_GAIN_RATIO,
    MAX_ACTIVE_ORDERS,
    OVERPAY_RATIO,
)

adjust = lambda price, ratio: price + (price * ratio)


def save_price(price) -> None:
    ts = datetime.now().timestamp()
    symbol = 'ethusd'

    with open(f'{symbol}.prices.csv', 'a+', encoding='utf-8') as f:
        f.write(f'{symbol},{ts},{price}\n')

def save_order(order: Order) -> None:
    symbol = order.symbol
    ts = order.timestamp
    side = order.side
    amt = order.original_amount
    price = order.price
    
    with open(f'{symbol}.orders.csv', 'a+', encoding='utf-8') as f:
        f.write(f'{symbol},{ts},{side},{amt},{price}\n')


def price_stream(symbol: str):
    while True:
        price = ticker(symbol)
        yield float(price['last'])



def runloop():
    last_id = 0

    print(
        f'Creating {MAX_ACTIVE_ORDERS} orders of ${USD_ORDER_AMT} each, selling'
        f' if price rises by {MAX_GAIN_RATIO * 100}% or lowers by '
        f'{MAX_LOSS_RATIO * 100}%.'
    )

    active_orders = {}
    closed_orders = {}

    for price in price_stream('ethusd'):
        save_price(price)
        print('=============================================')
        print(f'Current Price: ${price}')

        for id, order in active_orders.items():
            active_orders[id] = Order(order_status(order.id))

        while len(active_orders) < max_active_orders:
            last_id += 1
            buy_order = Order(new_order('buy', 'ethusd', ETH(usd_amt / price), USD(adjust(price, overpay_ratio))))
            save_order(buy_order)
            active_orders[last_id] = buy_order

        for id, order in active_orders.items():
            price = float(order.price)
            if (price > adjust(price, max_gain_ratio) or
                  price < adjust(price, max_loss_ratio)):
                
                buy_order = active_orders.pop(id)
                sell_order = Order(new_order('sell', 'ethusd', buy_order.amt, USD(adjust(price, -overpay_ratio))))
                save_order(buy_order)

                closed_orders[id] = {
                    'buy': buy_order,
                    'sell': sell_order,
                    'net': ((float(sell_order.price) * float(sell_order.original_amount))
                            - (float(buy_order.price) * float(buy_order.original_amount))),
                }

        net_gains = sum(order['net'] for order in closed_orders.values())

        print(f'Active Orders:')
        print('\n'.join(f'{id}: {order}' for id, order in active_orders.items()))
        print(f'Closed Orders:')
        print('\n'.join(f'{id}: {order}' for id, order in closed_orders.items()))
        print(f'Net Gains: ${net_gains}')
        sleep(30)




if __name__ == '__main__':
    try:
        runloop()
    except (EOFError, KeyboardInterrupt):
        print('Stopped!')
