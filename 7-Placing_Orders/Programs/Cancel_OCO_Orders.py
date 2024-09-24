from datetime import datetime
import sqlite3
from time import time
import sys
from random import randrange


class order:
    # [1] Initialising variables
    def __init__(self, trading_pair: str, exchange_name: str, flag: int, chart_interval: str, db_name: str, OrderID: list, TP: float,
                 Stop_Loss: float, Stop_Limit: float, side: str, asset_equity: float):
        self.trading_pair = trading_pair
        self.exchange_name = exchange_name
        self.flag = flag
        self.OrderID = OrderID
        self.db_name = db_name
        self.chart_interval = chart_interval
        self.TP = TP
        self.Stop_Loss = Stop_Loss
        self.Stop_Limit = Stop_Limit
        self.side = side
        self.asset_equity = asset_equity
    
    
    
    # [2] Cancel OG OCO order
    def Cancel_OCO_order(self):


        """params = {
            "timestamp": int(round(time() * 1000, 0))

        }"""


        """ Flag = 0 (Live) | Flag = 1 (Demo)"""
        if self.flag == 0:
            sys.path.append("Misc/Programs")
            from Binance_Rest_Api import run
            
            for i in range(len(self.OrderID)):
                #print(self.OrderID[i])
                params = {
                        "symbol": self.trading_pair,
                        "isIsolated": "FALSE",
                        "orderId": self.OrderID[i],
                        "timestamp": int(round(time() * 1000, 0))

                    }
                method = "DELETE"
                path = "/sapi/v1/margin/order"
                r_type = 0 # Private request

                purchase_data = run(method, path, params, r_type)

                return purchase_data


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
            
            
            return
    
    
    # [3] Place a new OCO Order
    def new_OCO_Order(self):
        # Setting Side for binance
        """ Since the origional side was LONG/SHORT the OCO side in the opposite direction needs to be SHORT/LONG"""
        if self.side == "LONG":
            side = "SELL"
        elif self.side == "SHORT":
            side = "BUY"

        # [3.2] Setting Parameters
        params = {
            "symbol": self.trading_pair,
            "isIsolated": "FALSE",
            "side": side,
            "quantity": self.asset_equity,
            "price": self.TP,
            "stopPrice": self.Stop_Loss,
            "stopLimitPrice": self.Stop_Limit,
            "sideEffectType": "MARGIN_BUY",
            "stopLimitTimeInForce": "GTC",
            "sideEffectType": "AUTO_REPAY",
            "timestamp": int(round(time() * 1000, 0))

        }

        
        # [3.3] Completing OCO
        """ Flag = 0 (Live) | Flag = 1 (Demo)"""
        if self.flag == 0:
            sys.path.append("Misc/Programs")
            from Binance_Rest_Api import run

            # print("Live Trade")
            method = "POST"
            path = "/sapi/v1/margin/order/oco"
            r_type = 0 # Private request

            purchase_data = run(method, path, params, r_type)
            #print(purchase_data)
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
        


    # [4] Updates the orderbook for the market Order | Status: Entered
    def Entered_update_orderbook(self, orderbook_pos: int):
        # [4.1] Cancels previous OCO 
        self.Cancel_OCO_order() #######
        # [4.2] Places new OCO Order
        order_data = self.new_OCO_Order()

        # [4.3] Setting Up Variables to be added/ Ammended to orderbook
        SL_OrderID = order_data[0]
        TP_OrderID = order_data[1] 
        status = "OCO_Placed"

        # [4.4] Getting file name
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
        update_statement = (f"""UPDATE trade_data SET TP_Order_ID={SL_OrderID}, SL_Order_ID={TP_OrderID}, Status="{status}", Stop_Loss="{self.Stop_Loss}", Stop_Limit="{self.Stop_Limit}"
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
chart_interval = "5m"
db_name = "Strategy2_Orders"
OrderID = ["30676344472", "30676344473"]
TP = 65000
Stop_Loss = 61000
Stop_Limit = 60500
side = "LONG"
asset_equity = 0.00048



# Functions
main = order(trading_pair=trading_pair, exchange_name=exchange_name, flag=flag, chart_interval=chart_interval, db_name=db_name, OrderID=OrderID, TP=TP,
             Stop_Limit=Stop_Limit, Stop_Loss=Stop_Loss, side=side, asset_equity=asset_equity)

(main.Entered_update_orderbook(0))'''

#print(main.get_equity())

#main.Entered_update_orderbook(2)

