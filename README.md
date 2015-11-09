#Python Coinbase BTC<->USD trading bot
:moneybag: Bitcoin trading bot based on a simple exponential moving average (trading via Coinbase).

I'm trying to write a simple bot that sells bitcoin the moment it makes enough profit to pay for transaction fees, plus a small margin.
It will do this thousands of times per day, and hopefully profit in the long run as long as the market is volatile and trending upwards (i.e. as long as not too many people are running bots exactly like this one).

If everyone ran bots like this the market would be flat, and no one would profit because bots would quickly equalize any fluctuations, but based on the recent press and hubub around bitcoin, I think it's volatile enough to make a small profit using a simple algorithm like this one.

The algorithm works by making a set of small initial buys (~$10), then tracking the market price in relation to the purchased price.
If the price drops below the purchase price, it'll sell immediately to avoid any losses.
If the price rises back above the purchase price, it'll rebuy the same amount, and sell once it goes above the min profit margin amount + transaction fees.  This type of tight, risk-averse bot will only make small profits because it'll never wait for big upward trends to max out, it'll sell as soon as it goes in the green.

```python
def analyze(self):
    for idx, buy in enumerate(self.buys):
        if self.get_price() > buy['price'] + market_fees + min_profit_margin:
            self.buys.pop(idx)
            self.sell(buy['amount'])    # if price rises above buy price + market fees by a certain amount, sell early and reap the tiny profits
        elif self.get_price() < buy['price'] + market_fees:
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
```


The trading algorithm is nowhere near complete, it runs and works though, and will trade REAL MONEY, so beware if you run it.  

======
I'm not responsible for any money you lose due to my bad algorithm, bugs in the implementation of it, or fluctuations in the market.
