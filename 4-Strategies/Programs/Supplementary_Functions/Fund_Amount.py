import sqlite3
from datetime import datetime
from sys import path

# TO DELETE

class Fund:
    # Initiaalising variables for the Class
    def __init__(self, trading_pair, exchange_name, chart_interval, USDT_Amount, side):
        self.trading_pair = trading_pair
        self.USDT_Amount = USDT_Amount
        self.exchange_name = exchange_name
        self.chart_interval = chart_interval
        self.side = side

    
    # Function for getting the current Closing Price of an asset - WORKING
    def get_current_data(self):
        path.append("ZZ-General_Functions/Programs")
        from get_current_data import current_data
        return current_data(self.trading_pair, self.exchange_name, self.chart_interval)
        

    # Determines the available USDT amount and asset amount
    def amount(self):
        """ NOTES:
        When going long, the USDT amount is the total amount of crypto available to trade.
        When going short, the USDT amount is the total amount of USDT available to trade.
        e.g. IF short with a leverage of 3x and 10,000 USDT, 20,000 USDT equivalent in bitcoin is available to short
        Additionally Balances Such as BTC balance or USDT balance should always be temporary. The base asset for all trading is USDT
        """
        # Do Nothing and return USDT_Amount
        if side == "LONG":
            return self.USDT_Amount
        # Calculate the asset equivalent 
        elif side == "SHORT":
            closing_price = self.get_current_data()[4]
            Asset_to_buy = self.USDT_Amount/closing_price
            print(Asset_to_buy)
        



""" TESTING """
'''
# Variables
trading_pair = "BTCUSDT"
USDT_Amount = 10000
exchange_name = "Binance"
chart_interval = "5m"
side = "SHORT"#"LONG"

main = Fund(trading_pair, exchange_name, chart_interval, USDT_Amount, side)

#print(main.get_current_data())

main.amount()

'''