import threading
from coinbase.wallet.client import Client
from money import Money

from secrets import api_key, api_secret

market_fees = 0.15          # coinbase per-transaction fee in dollars
min_profit_margin = 2.0     # minimum price increase before we sell out

class Trader(threading.Thread):
    def __init__(self, api_key, api_secret, alpha=0.5):
        assert 0 < alpha <= 1.0  # smoothing factor for the exponential moving avg function
        super(threading.Thread, self).__init__()
        self.alpha = alpha
        self.client = Client(api_key, api_secret)
        self.user = self.client.get_current_user()
        self.buys = []
        self.sells = []
        print 'Trading As:         %s (%s)' % (self.user['name'], self.user['email'])
        print 'Starting Balance:   $%s (%s BTC @ $%s/BTC)' % (self.balance['USD'], self.balance['BTC'], self.get_price())

    @property
    def account(self):
        return [acct for acct in self.client.get_accounts()['data'] if acct['balance']['currency'] == 'BTC'][0]

    @property
    def balance(self):
        return {
            self.account['balance']['currency']:        float(self.account['balance']['amount']),
            self.account['native_balance']['currency']: float(self.account['native_balance']['amount']),
        }

    def get_price(self):
        return float(self.client.get_spot_price()['amount'])

    def buy(self, amount):
        buy_obj = self.account.buy(amount, 'USD')
        self.buys.append(buy_obj)

    def sell(self, amount):
        sell_obj = self.account.sell(amount, 'USD')
        self.sells.append(sell_obj)

    def analyze(self):
        for idx, buy in enumerate(self.buys):
            if self.get_price() > buy['price'] + market_fees + min_profit_margin:
                self.buys.pop(idx)
                self.sell(buy['amount'])    # if price rises above buy price + market fees by a certain amount, sell early and reap the tiny profits
            elif self.get_price() < buy['price']:
                self.buys.pop(idx)
                self.sell(buy['amount'])    # if price drops below the price it was bought at, sell immediately to minimize losses
            else:
                pass                        # do nothing until the price fluctuates enough to make more of a difference

        for idx, sell in enumerate(self.sells):
            if self.get_price() > sell['price']:
                self.sells.pop(idx)
                self.buy(sell['amount'])    # if price starts to rise above the amount we sold it for, rebuy the same amount
            else:
                # if market trends downwards we'll lose (number of transactions * (market fee per transaction + min profit margin))
                pass                        # price is below the amount we sold for, don't do anything until it's passing break-even again


    def run(self):
        self.keep_running = True
        while self.keep_running:
            self.analyze()

    # def avg(self):
    #     return sum(self.alpha**n.days * iq
    # ...     for n, iq in map(lambda (day, iq), today=max(days): (today-day, iq),
    # ...         sorted(zip(days, IQ), key=lambda p: p[0], reverse=True))

#if __name__ == '__main__':

t = Trader(api_key, api_secret)
