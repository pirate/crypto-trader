class Currency:
    icon: str
    symbol: str
    decimal_places: int

    def __init__(self, amt: float) -> None:
        amt = round(amt, self.decimal_places)
        assert amt > 0
        self.amt = amt

    def __str__(self) -> str:
        return str(round(self.amt, self.decimal_places))

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


class Order:
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
        finished = round((float(self.executed_amount) / float(self.original_amount)) * 100, 0)
        return (
            f'#{self.id} {self.side.upper()} {repr(self.buy_amt)} @ '
            f'{repr(self.price_amt)} {self.symbol.upper()} ({finished}% filled)'
        )

    @property
    def is_finished(self):
        return self.remaining_amount == "0"

    @property
    def buy_amt(self) -> Currency:
        return currency_by_symbol[self.symbol[:3]](float(self.original_amount))

    @property
    def price_amt(self) -> Currency:
        return currency_by_symbol[self.symbol[3:]](float(self.price))
