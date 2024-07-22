from datetime import datetime
import sqlite3
from time import time
import sys


class order:
    # Initialising variables
    def __init__(self, trading_pair, exchange_name, flag, side, equity, chart_interval, db_name):
        self.trading_pair = trading_pair
        self.exchange_name = exchange_name
        self.flag = flag
        self.side = side
        self.equity = equity
        self.chart_interval = chart_interval
        self.db_name = db_name
    
    
    # Rounds the number to the amount of significant figures determined by the asset precision
    def round_sign_number(self, value: float):
        # This list we be expanded as more trading pairs get added
        if "BTC" in self.trading_pair:
            precision = 5
        elif "ETH" in self.trading_pair:
            precision = 4


        return round(value, precision)
    
    def get_current_price(self):
        #  Getting recent price data
        date_and_time = (datetime.now())
        date = date_and_time.strftime("%b%d%y%H")
        file_name = f"1-DataGathering/data_gathered/{self.trading_pair}_data/Live_Data/{str(date)}{self.exchange_name}{self.trading_pair}interval={str(self.chart_interval)}kline_data.db"
        #print(file_name)
        connection = sqlite3.connect(file_name)
        cursor = connection.cursor()
        cursor.execute("Select * FROM pair_price")
        list_check = cursor.fetchall()
        recent_log = list_check[-1] #Most Recent data gathered from file
        connection.commit()
        connection.close() #Closing the database
        
        # Close Price
        closeing_price = recent_log[4]
        return closeing_price

    # The amount of money that will be used to trade
    def get_equity(self):
        if self.side == "LONG":
            usdt_equity = self.equity

            closeing_price = self.get_current_price()
            asset_equity = usdt_equity/closeing_price

            return self.round_sign_number(asset_equity) 
        elif self.side == "SHORT":
            return self.round_sign_number(self.equity) 
    
    # Places a market order
    def market_order(self):
        # Setting Side for binance
        if self.side == "LONG":
            side = "BUY"
        elif self.side == "SHORT":
            side = "SELL"
        
        # Getting Asset Equity
        asset_equity = self.get_equity()

        params = {
            "symbol": self.trading_pair,
            "isIsolated": "FALSE",
            "side": side,
            "type": "MARKET",
            "quantity": asset_equity,
            "sideEffectType": "MARGIN_BUY",
            "timestamp": int(round(time() * 1000, 0))

        }


        """ Flag = 0 (Live) | Flag = 1 (Demo)"""
        if self.flag == 0:
            sys.path.append("Misc/Programs")
            from Binance_Rest_Api import run

            # print("Live Trade")
            
            method = "POST"
            path = "/sapi/v1/margin/order"
            r_type = 0 # Private request

            purchase_data = run(method, path, params, r_type)

            return purchase_data


        elif self.flag == 1:

            """
            {'symbol': 'BTCUSDT', 'orderId': 28362648641, 'clientOrderId': 't5ZfvMHcCdTGkKX47D6Vy0', 'transactTime': 1720223431557, 'price': '0', 
            'origQty': '0.00026', 'executedQty': '0.00026', 'cummulativeQuoteQty': '14.7472', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET', 
            'side': 'BUY', 'fills': [{'price': '56720', 'qty': '0.00026', 'commission': '0.00002221', 'commissionAsset': 'BNB', 
            'tradeId': 3667208294}], 'isIsolated': False, 'selfTradePreventionMode': 'EXPIRE_MAKER'}
            """
            
            purchase_data = {
                "symbol": self.trading_pair,
                "orderID": int(round(time() * 1000, 0)),
                "transactTime": int(round(time() * 1000, 0)),
                "executedQty": str(asset_equity),
                "fills": [{
                    "price": str(self.get_current_price()),
                    "commision": str(asset_equity * (0.1/100))
                    
                }]
            }

            return purchase_data
    
    # Updates the orderbook for the market Order | Status: Ready
    def Ready_update_orderbook(self, orderbook_pos):
        order_data = self.market_order() # Places a market order and returns the data
        # Setting Up Variables to be added/ Ammended to orderbook
        orderID = order_data["orderID"]
        Entry_Time = order_data['transactTime'] # In milliseconds
        Entry_Price = order_data['fills'][0]['price']
        Order_Funds_qty = order_data["executedQty"]
        Entry_Fee = order_data['fills'][0]['commision']
        status = "Entered"

        # Getting file name
        date_and_time = (datetime.now())
        date = date_and_time.strftime("%y")
        if self.flag == 0: # Live
            file_name = f"4-Strategies/data_gathered/{self.trading_pair}_data/{str(date)}{self.exchange_name}{self.trading_pair}{self.db_name}.db"
        elif self.flag == 1: # Demo
            file_name = f"4-Strategies/data_gathered/{self.trading_pair}_data/{str(date)}{self.exchange_name}{self.trading_pair}{self.db_name}DEMO.db"

        # Connecting to database
        connection = sqlite3.connect(file_name)
        cursor = connection.cursor()
        cursor.execute("Select * FROM trade_data")
        list_check = cursor.fetchall()

        specific_order = list_check[orderbook_pos]
        update_ID = [specific_order[1], specific_order[3]] # These arw specific to the order in the orderbook
        # The specific order in the orderbook that gets updated
        update_statement = (f"""UPDATE trade_data SET Entry_Time={Entry_Time}, Entry_Order_ID={orderID},
                            Entry_Price={Entry_Price}, O_Funds_Traded={Order_Funds_qty}, Entry_Fee={Entry_Fee}, Status="{status}"
                            WHERE (server_time = "{update_ID[0]}" AND trading_pair = "{self.trading_pair}") """)

        cursor.execute(update_statement)

        connection.commit() 
        connection.close()

        #print(update_ID)


'''
""" TESTING """
# Variables
trading_pair = "BTCUSDT"
exchange_name = "Binance"
flag = 1
side = "LONG"
equity = 15 #0.00203 # Needs to be the BTC amount or ETH, for example, not USDT
chart_interval = "5m"
db_name = "Strategy2_Orders"



# Functions
main = order(trading_pair, exchange_name, flag, side, equity, chart_interval, db_name)'''

#print(main.market_order())

#print(main.get_equity())

#main.Ready_update_orderbook(2)