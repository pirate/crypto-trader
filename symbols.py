from decimal import Decimal

class Currency:
    """Base class for currencies that have a decimal place limit"""
    icon: str
    symbol: str
    decimal_places: int

    def __init__(self, amt: Decimal) -> None:
        assert amt > 0
        self.amt = round(Decimal(amt), self.decimal_places)

    def __str__(self) -> str:
        return str(self.amt)

    def __repr__(self) -> str:
        return f'{self.icon}{self.amt}'

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
}


class Order:
    """Object representing a Gemini order"""
    # Spec: https://docs.gemini.com/rest-api/#order-status
    # {
    #   "order_id" : "44375901",
    #   "id" : "44375901",
    #   "symbol" : "btcusd",
    #   "exchange" : "gemini",
    #   "avg_execution_price" : "400.00",
    #   "side" : "buy",
    #   "type" : "exchange limit",
    #   "timestamp" : "1494870642",
    #   "timestampms" : 1494870642156,
    #   "is_live" : false,
    #   "is_cancelled" : false,
    #   "is_hidden" : false,
    #   "was_forced" : false,
    #   "executed_amount" : "3",
    #   "remaining_amount" : "0",
    #   "options" : [ ],
    #   "price" : "400.00",
    #   "original_amount" : "3"
    # }
    def __init__(self, json):
        if json.get('result') == 'error':
            print(json.get('message'))
            raise Exception(json.get('reason'))

        assert 'id' in json
        self.data = json

    def __getattr__(self, attr):
        return self.data[attr]

    def __repr__(self):
        finished = round((Decimal(self.executed_amount) / Decimal(self.original_amount)) * 100, 0)
        return (
            f'{self.side.upper()} {self.symbol.upper()} '
            f'{repr(self.buy_amt)} @ {repr(self.price_amt)} ({finished}% filled '
            f'for ${round(self.filled_amt, 2)})'
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
    def filled_amt(self) -> Decimal:
        return Decimal(self.price) * Decimal(self.executed_amount)
