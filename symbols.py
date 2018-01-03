"""
Currency types as defined here:
    https://docs.gemini.com/rest-api/#symbols-and-minimums

Order object representing a Gemini order:
    https://docs.gemini.com/rest-api/#order-status
"""

from decimal import Decimal

class Currency:
    """Base class for currencies that have a decimal place limit"""
    amt: Decimal
    icon: str
    symbol: str
    decimal_places: int

    def __init__(self, amt: Decimal) -> None:
        self.amt = Decimal(round(Decimal(amt), self.decimal_places))

    def __str__(self) -> str:
        return str(self.amt)

    def __repr__(self) -> str:
        return f'{self.icon}{self.amt}'

    def __add__(self, other: object) -> 'Currency':
        if isinstance(other, self.__class__) and isinstance(other, Currency):
            return self.__class__(other.amt + self.amt)
        return NotImplemented

    def __radd__(self, other: object) -> 'Currency':
        if other == 0:
            return self  # needed for sum(n for n in (USD(1), USD(2)))
        if isinstance(other, self.__class__) and isinstance(other, Currency):
            return self.__class__(self.amt + other.amt)
        return NotImplemented

    def __sub__(self, other: object) -> 'Currency':
        if isinstance(other, self.__class__) and isinstance(other, Currency):
            return self.__class__(self.amt - other.amt)
        return NotImplemented

    def __rsub__(self, other: object) -> 'Currency':
        if isinstance(other, self.__class__) and isinstance(other, Currency):
            return self.__class__(other.amt - self.amt)
        return NotImplemented

    def __mul__(self, other: object) -> 'Currency':
        if isinstance(other, (int, Decimal)):
            return self.__class__(self.amt * other)
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (int, float, Decimal)):
            return self.amt == other
        if isinstance(other, self.__class__) and isinstance(other, Currency):
            return self.amt == other.amt
        return NotImplemented

    def __gt__(self, other: object) -> bool:
        if isinstance(other, (int, float, Decimal)):
            return self.amt > other
        if isinstance(other, self.__class__) and isinstance(other, Currency):
            return self.amt > other.amt
        return NotImplemented

    def __ge__(self, other: object) -> bool:
        if isinstance(other, (int, float, Decimal)):
            return self.amt >= other
        if isinstance(other, self.__class__) and isinstance(other, Currency):
            return self.amt >= other.amt
        return NotImplemented

    def __lt__(self, other: object) -> bool:
        if isinstance(other, (int, float, Decimal)):
            return self.amt < other
        if isinstance(other, self.__class__) and isinstance(other, Currency):
            return self.amt < other.amt
        return NotImplemented

    def __le__(self, other: object) -> bool:
        if isinstance(other, (int, float, Decimal)):
            return self.amt <= other
        if isinstance(other, self.__class__) and isinstance(other, Currency):
            return self.amt <= other.amt
        return NotImplemented

class USD(Currency):
    icon = '$'
    symbol = 'usd'
    decimal_places = 2

class BTC(Currency):
    icon = '𝔹'
    symbol = 'btc'
    decimal_places = 6

class ETH(Currency):
    icon = '𝔼'
    symbol = 'eth'
    decimal_places = 4

currency_by_symbol = {
    'usd': USD,
    'btc': BTC,
    'eth': ETH,
}

currency_pair_by_symbol = {
    'ethusd': (ETH, USD),
    'btcusd': (BTC, USD),
    'ethbtc': (ETH, BTC),
}


class Order:
    """Object representing a Gemini order"""
    # Spec: https://docs.gemini.com/rest-api/#order-status
    _schema = {
      "order_id": "44375901",
      "id": "44375901",
      "symbol": "btcusd",
      "exchange": "gemini",
      "avg_execution_price": "400.00",
      "side": "buy",
      "type": "exchange limit",
      "timestamp": "1494870642",
      "timestampms": 1494870642156,
      "is_live": False,
      "is_cancelled": False,
      "is_hidden": False,
      "was_forced": False,
      "executed_amount": "3",
      "remaining_amount": "0",
      "options": [],
      "price": "400.00",
      "original_amount": "3",
    }

    def __init__(self, json):
        if json.get('result') == 'error':
            print(json.get('message'))
            raise Exception(json.get('reason'))

        assert 'id' in json, 'Order json must have an id field.'
        self.data = json

    def __getattr__(self, attr):
        return self.data[attr]

    def __repr__(self):
        pct = round((Decimal(self.executed_amount) / Decimal(self.original_amount)) * 100)
        return (
            f'{self.side.upper()} {self.symbol.upper()} '
            f'{repr(self.buy_amt)} @ {repr(self.price_amt)} ({pct}% filled '
            f'for {repr(self.filled_amt)})'
        )

    @property
    def is_filled(self):
        return self.remaining_amount == "0"

    @property
    def buy_amt(self) -> Currency:
        return currency_by_symbol[self.symbol[:3]](Decimal(self.original_amount))

    @property
    def price_amt(self) -> Currency:
        return currency_by_symbol[self.symbol[3:]](Decimal(self.price))

    @property
    def filled_amt(self) -> Currency:
        return USD(Decimal(self.price) * Decimal(self.executed_amount))

currency_art = {
    'ethusd': '''
 _______ _________                   _______  ______  
(  ____ \\\__   __/|\     /||\     /|(  ____ \(  __  \ 
| (    \/   ) (   | )   ( || )   ( || (    \/| (  \  )
| (__       | |   | (___) || |   | || (_____ | |   ) |
|  __)      | |   |  ___  || |   | |(_____  )| |   | |
| (         | |   | (   ) || |   | |      ) || |   ) |
| (____/\   | |   | )   ( || (___) |/\____) || (__/  )
(_______/   )_(   |/     \|(_______)\_______)(______/ 
''',
    'btcusd': '''
______ _________ _______           _______  ______  
(  ___ \\\__   __/(  ____ \|\     /|(  ____ \(  __  \ 
| (   ) )  ) (   | (    \/| )   ( || (    \/| (  \  )
| (__/ /   | |   | |      | |   | || (_____ | |   ) |
|  __ (    | |   | |      | |   | |(_____  )| |   | |
| (  \ \   | |   | |      | |   | |      ) || |   ) |
| )___) )  | |   | (____/\| (___) |/\____) || (__/  )
|/ \___/   )_(   (_______/(_______)\_______)(______/ 
''',
    'ethbtc': '''
 _______ _________          ______ _________ _______ 
(  ____ \\\__   __/|\     /|(  ___ \\\__   __/(  ____ \
| (    \/   ) (   | )   ( || (   ) )  ) (   | (    \/
| (__       | |   | (___) || (__/ /   | |   | |      
|  __)      | |   |  ___  ||  __ (    | |   | |      
| (         | |   | (   ) || (  \ \   | |   | |      
| (____/\   | |   | )   ( || )___) )  | |   | (____/\
(_______/   )_(   |/     \||/ \___/   )_(   (_______/
                                                     
''',
}
