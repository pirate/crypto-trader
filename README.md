# Python Coinbase trading bot (BTC<>USD)
:moneybag: Bitcoin trading bot based on a simple exponential moving average (trading via [Coinbase](https://www.coinbase.com/)).

I'm trying to write a simple bot that sells bitcoin the moment it makes enough profit to pay for transaction fees, plus a small margin.
It will do this thousands of times per day, and hopefully profit in the long run as long as the market is volatile and trending upwards (i.e. as long as not too many people are running bots exactly like this one).

If everyone ran bots like this the market would be flat, and no one would profit because bots would quickly equalize any fluctuations, but based on the recent press and hubub around bitcoin, I think it's volatile enough to make a small profit using a simple algorithm like this one.

The algorithm works by making a set of small initial buys (~$10), then tracking the market price in relation to the purchased price.
If the price drops below the purchase price, it'll sell immediately to avoid any losses.
If the price rises back above the purchase price, it'll rebuy the same amount, and sell once it goes above the min profit margin amount + transaction fees.  This type of tight, risk-averse bot will only make small profits because it'll never wait for big upward trends to max out, it'll sell as soon as it goes in the green.  This strategy is famous as the "quit while you're ahead" strategy,  and it simply [doesn't work](https://gist.github.com/pirate/eac582480aa34b5adda9e6adc1878190) in the long run.

```python
while bankroll > 0:
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

  
The `trader.py` file is intentionally broken to stop people from emailing me with "I ran your bot and lost all my money", to run it you need to read `analyze()` and adapt it to your own needs.  In an upwards-trending market the algorithm detailed above is unlikely to make any more than you would by holding the money and not trading at all (due to parasitic losses from fees).  It's on github to serve as a template for people who want to write their own bots that trade on coinbase.
   
======

TODOS:

* Implement better ties between buys and sells (instead of just `buys.pop(idx)`)
* Write the initial buy code that kicks off trading each day
* Implement a bankroll system so the bot is only ever trading with profits
* Write a meta-trader that spawns multiple traders with tweaked parameters to see which ones make the most money
* Switch to the Coinbase Exchange API instead of the general trading API

======
I'm not responsible for any money you lose due to my bad algorithm, bugs in the implementation of it, or fluctuations in the market.
