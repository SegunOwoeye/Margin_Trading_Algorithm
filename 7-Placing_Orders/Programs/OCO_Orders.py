from datetime import datetime
import sqlite3
from time import time
import sys
from random import randrange


class order:
    # Initialising variables
    def __init__(self, trading_pair, exchange_name, flag, side, asset_equity, chart_interval, db_name, TP, Stop_Loss, Stop_limit):
        self.trading_pair = trading_pair
        self.exchange_name = exchange_name
        self.flag = flag
        self.side = side
        self.asset_equity = asset_equity
        self.chart_interval = chart_interval
        self.db_name = db_name
        self.TP = TP
        self.Stop_Loss = Stop_Loss
        self.Stop_limit = Stop_limit
    
    
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
    
    def round_entry_exit(self):
        # Rounding entry and exit prices to the amount of significant figures determined by the asset precision
        if "BTC" in self.trading_pair:
            take_profit = round(self.TP,2)
            stop_loss = round(self.Stop_Loss,2)
            stop_limit = round(self.Stop_limit,2)

        values = {"TP": take_profit, "Stop_Loss": stop_loss, "Stop_Limit": stop_limit}
        return values

            
    
    
    # Places a market order
    def OCO_order(self):
        # Initialising values
        entry_exit_prices = self.round_entry_exit()
        take_profit = entry_exit_prices['TP']
        stop_loss = entry_exit_prices['Stop_Loss']
        stop_limit = entry_exit_prices['Stop_Limit']

        # Setting Side for binance
        """ Since the origional side was LONG/SHORT the OCO side in the opposite direction needs to be SHORT/LONG"""
        if self.side == "LONG":
            side = "SELL"
        elif self.side == "SHORT":
            side = "BUY"

        params = {
            "symbol": self.trading_pair,
            "isIsolated": "FALSE",
            "side": side,
            "quantity": self.asset_equity,
            "price": take_profit,
            "stopPrice": stop_loss,
            "stopLimitPrice": stop_limit,
            "sideEffectType": "MARGIN_BUY",
            "stopLimitTimeInForce": "GTC",
            "sideEffectType": "AUTO_REPAY",
            "timestamp": int(round(time() * 1000, 0))

        }


        """ Flag = 0 (Live) | Flag = 1 (Demo)"""
        if self.flag == 0:
            sys.path.append("Misc/Programs")
            from Binance_Rest_Api import run

            # print("Live Trade")
            method = "POST"
            path = "/sapi/v1/margin/order/oco"
            r_type = 0 # Private request

            purchase_data = run(method, path, params, r_type)
            orders = purchase_data['orders']
            SL_OrderID = orders[0]['orderId']
            TP_OrderID = orders[1]['orderId']

            return SL_OrderID, TP_OrderID # Returning Order ID of OCOs for tracking


        elif self.flag == 1:

            """
            {'orderListId': 121459910, 'contingencyType': 'OCO', 'listStatusType': 'EXEC_STARTED', 'listOrderStatus': 'EXECUTING', 
            'listClientOrderId': 'tc2EqLtURRGMbddoREFez4', 'transactionTime': 1720271144018, 'symbol': 'BTCUSDT', 'isIsolated': False, 
            'orders': [{'symbol': 'BTCUSDT', 'orderId': 28375793379, 'clientOrderId': 'dD4JpA4Xu4EoMKqmlGdjKM'}, 
                        {'symbol': 'BTCUSDT', 'orderId': 28375793380, 'clientOrderId': 'PSAhGBfaNt1lHEZ8XMFYKJ'}], 
            'orderReports': [{'symbol': 'BTCUSDT', 'orderId': 28375793379, 'orderListId': 121459910, 'clientOrderId': 'dD4JpA4Xu4EoMKqmlGdjKM',
                            'transactTime': 1720271144018, 'price': '60500.00000000', 'origQty': '0.00030000', 'executedQty': '0', 'cummulativeQuoteQty': '0', 
                            'status': 'NEW', 'timeInForce': 'GTC', 'type': 'STOP_LOSS_LIMIT', 'side': 'BUY', 'stopPrice': '60000.00000000', 'selfTradePreventionMode': 'EXPIRE_MAKER'}, 
                            {'symbol': 'BTCUSDT', 'orderId': 28375793380, 'orderListId': 121459910, 'clientOrderId': 'PSAhGBfaNt1lHEZ8XMFYKJ', 'transactTime': 1720271144018, 
                            'price': '50000.00000000', 'origQty': '0.00030000', 'executedQty': '0', 'cummulativeQuoteQty': '0', 'status': 'NEW', 'timeInForce': 'GTC', 
                            'type': 'LIMIT_MAKER', 'side': 'BUY', 'selfTradePreventionMode': 'EXPIRE_MAKER'}]}
            """
            
            
            SL_OrderID = randrange(10000000000, 99999999999)
            TP_OrderID = SL_OrderID + 1

            return SL_OrderID, TP_OrderID # Returning Order ID of OCOs for tracking
    
    # Updates the orderbook for the market Order | Status: Entered
    def Entered_update_orderbook(self, orderbook_pos):
        order_data = self.OCO_order() # Places a OCO order and returns the data
        # Setting Up Variables to be added/ Ammended to orderbook
        SL_OrderID = order_data[0]
        TP_OrderID = order_data[1] 
        status = "Initial_OCO_Placed"

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
        update_statement = (f"""UPDATE trade_data SET TP_Order_ID={SL_OrderID}, SL_Order_ID={TP_OrderID}, Status="{status}"
                            WHERE (server_time = "{update_ID[0]}" AND trading_pair = "{self.trading_pair}") """)

        cursor.execute(update_statement)

        connection.commit() 
        connection.close()

'''

""" TESTING """

# FOR SHORTING
# Variables
"""trading_pair = "BTCUSDT"
exchange_name = "Binance"
flag = 0
side = "LONG"
asset_equity = 0.00030 # Needs to be the BTC amount or ETH, for example, not USDT
chart_interval = "5m"
db_name = "Strategy2_Orders"
TP = 70000
Stop_Loss = 50000
Stop_limit = 49500"""

trading_pair = "BTCUSDT"
exchange_name = "Binance"
flag = 0
side = "SHORT"
asset_equity = 0.00030 # Needs to be the BTC amount or ETH, for example, not USDT
chart_interval = "5m"
db_name = "Strategy2_Orders"
TP = 50000
Stop_Loss = 60000
Stop_limit = 60500



# Functions
main = order(trading_pair, exchange_name, flag, side, asset_equity, chart_interval, db_name, TP, Stop_Loss, Stop_limit)

print(main.OCO_order())

#print(main.get_equity())

#main.Entered_update_orderbook(2)

'''