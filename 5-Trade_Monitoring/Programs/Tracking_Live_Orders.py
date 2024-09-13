from datetime import datetime
import sqlite3
from time import time
import sys 
from os.path import exists


class order_Monitoring:
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
    
    # Gets the filename of the Orderbook
    def get_filename(self):
        # Getting file name based on environment
        date_and_time = (datetime.now())
        date = date_and_time.strftime("%y")
        if self.flag == 0: # Live
            file_name = f"4-Strategies/data_gathered/{self.trading_pair}_data/{str(date)}{self.exchange_name}{self.trading_pair}{self.db_name}.db"
        elif self.flag == 1: # Demo
            file_name = f"4-Strategies/data_gathered/{self.trading_pair}_data/{str(date)}{self.exchange_name}{self.trading_pair}{self.db_name}DEMO.db"

        return file_name
    
    # Gets the current price of the asset
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


    # Gets the details of the orderbook depending on what line is needed
    def get_orderbook(self, order_position):
        """
        None -> Orderbook is empty
        Ready -> A signal has been given and a new order has been submitted to the book
        Entered -> Depending on the Side (Long/Short) a position has been entered and is now being monitored 9Active
        Closed -> The position has been closed 
        """
        
        # Getting file name based on environment
        file_name = self.get_filename()        
        
        # Check to see if the orderbook exists | Return "None"
        if exists(file_name) == False:
            return None
        
        # Connecting to database
        connection = sqlite3.connect(file_name)
        cursor = connection.cursor()
        cursor.execute("Select * FROM trade_data")
        list_check = cursor.fetchall()

        connection.commit()
        connection.close() #Closing the database

        return list_check[order_position]



    def tracking_Order(self, order_position):
        # Setting Side for binance
        """ Since the origional side was LONG/SHORT the OCO side in the opposite direction needs to be SHORT/LONG"""
        if self.side == "LONG":
            side = "SELL"
        elif self.side == "SHORT":
            side = "BUY"
        # Getting order IDs
        specific_order = self.get_orderbook(order_position)
        TP_OrderID = specific_order[24]
        SL_OrderID = specific_order[25]

        OCO_OrderID_list = [TP_OrderID, SL_OrderID] 
        
        # OCO_OrderID_list = [28383468798, 28383468799, 28387387594] # DEMO
        for i in range(len(OCO_OrderID_list)):
            params = {
                "symbol": self.trading_pair,
                "isIsolated": "FALSE",
                "orderId": str(OCO_OrderID_list[i]),
                "timestamp": int(round(time() * 1000, 0))

            }
            """ Flag = 0 (Live) | Flag = 1 (Demo)"""
            if self.flag == 0: #0:
                sys.path.append("Misc/Programs")
                from Binance_Rest_Api import run
                
                method = "GET"
                url_path = "/sapi/v1/margin/order"
                r_type = 0 # Private request

                purchase_data = run(method, url_path, params, r_type)
                # LOOK FOR STATUS: FILLED
                OCO_status = purchase_data['status']
                
                if OCO_status == "FILLED":
                    C_funds_traded = float(purchase_data['executedQty'])
                    exit_time = purchase_data['updateTime']
                    exit_price = purchase_data['price']
                    exit_fee = C_funds_traded * (0.1/100)

                    return C_funds_traded, exit_time, exit_price, exit_fee

                else: # Do Nothing
                    pass




            elif self.flag == 1:
                # Monitoring the DEMO OCO
                current_price = self.get_current_price()
                
                # Price Monitoring for Buy Side
                if side == "BUY":
                    if current_price >= self.Stop_Loss: # When SL is Triggered for BUY Side
                        C_funds_traded = self.asset_equity
                        exit_time = int(round(time() * 1000, 0))
                        exit_price = self.Stop_Loss
                        exit_fee = C_funds_traded * (0.1/100)
                        return C_funds_traded, exit_time, exit_price, exit_fee
                    elif current_price <= self.TP: # When TP is Triggered for BUY Side
                        C_funds_traded = self.asset_equity
                        exit_time = int(round(time() * 1000, 0))
                        exit_price = self.TP
                        exit_fee = C_funds_traded * (0.1/100)
                        return C_funds_traded, exit_time, exit_price, exit_fee
                    else:
                        pass

                # Price Monitoring for Sell Side
                elif side == "SELL":
                    if current_price <= self.Stop_Loss: # When SL is Triggered for Sell Side
                        C_funds_traded = self.asset_equity
                        exit_time = int(round(time() * 1000, 0))
                        exit_price = self.Stop_Loss
                        exit_fee = C_funds_traded * (0.1/100)
                        return C_funds_traded, exit_time, exit_price, exit_fee
                    
                    elif current_price >= self.TP: # When TP is Triggered for BUY Side
                        C_funds_traded = self.asset_equity
                        exit_time = int(round(time() * 1000, 0))
                        exit_price = self.TP
                        exit_fee = C_funds_traded * (0.1/100)
                        return C_funds_traded, exit_time, exit_price, exit_fee
                    
                    else:
                        pass

    # Updates the orderbook for the market Order | Status: OCO_Placed
    def OCO_Placed_update_orderbook(self, orderbook_pos):
        order_data = self.tracking_Order(orderbook_pos) # Monitors OCO orders and returns the data
        if order_data == None: # Do Nothing
            return
        # Setting Up Variables to be added/ Ammended to orderbook
        C_funds_traded = float(order_data[0])
        exit_time = float(order_data[1])
        exit_price = float(order_data[2])
        exit_fee = float(order_data[3])
        status = "Closed"

        # Getting file name based on environment
        file_name = self.get_filename()

        # Connecting to database
        connection = sqlite3.connect(file_name)
        cursor = connection.cursor()
        cursor.execute("Select * FROM trade_data")
        list_check = cursor.fetchall()
        specific_order = list_check[orderbook_pos]
        update_ID = [specific_order[1], specific_order[3]] # These are specific to the order in the orderbook
        
        # Calculating the Percentage change
        buy_in_price = specific_order[14]
        if specific_order[3] == "LONG":
            change = ((exit_price-buy_in_price) - (specific_order[20]*buy_in_price + exit_fee*exit_price))
            perc_change = (change/buy_in_price) * 100
            perc_change = round(perc_change,2)

        elif specific_order[3] == "SHORT":
            change = ((buy_in_price-exit_price) - (specific_order[20]*buy_in_price + exit_fee*exit_price))
            perc_change = (change/buy_in_price) * 100
            perc_change = round(perc_change,2)
        

        # The specific order in the orderbook that gets updated
        update_statement = (f"""UPDATE trade_data SET Exit_Time={exit_time}, Exit_Price={exit_price}, C_Funds_Traded={C_funds_traded},
                            Percentage_Change={perc_change}, Exit_Fee={exit_fee}, Status="{status}"
                            WHERE (server_time = "{update_ID[0]}" AND trading_pair = "{self.trading_pair}") """)

        cursor.execute(update_statement)

        connection.commit() 
        connection.close()


        """ SENDING EMAIL NOTIFICATION"""
        sys.path.append("YY_Notifications/Programs") 
        from email_notification import email_alert 
        subject = f"Closing {self.trading_pair} Order Made at {update_ID[0]}"
        message = (f"The order was closed at {exit_price} USDT achieving a percentage change of {perc_change}")
        email_recipient = "aces.cryptotrading@gmail.com"
        # Send Email
        email_alert(subject, message, email_recipient)

                
'''        

""" TESTING """

# Variables
trading_pair = "BTCUSDT"
exchange_name = "Binance"
flag = 1
side = "LONG"
asset_equity = 0.26187 # Needs to be the BTC amount or ETH, for example, not USDT
chart_interval = "5m"
db_name = "Strategy2_Orders"
TP = 70000
Stop_Loss = 50000
Stop_limit = 49500

'''


"""# SHORT
trading_pair = "BTCUSDT"
exchange_name = "Binance"
flag = 1
side = "SHORT"
asset_equity = 0.00030 # Needs to be the BTC amount or ETH, for example, not USDT
chart_interval = "5m"
db_name = "Strategy2_Orders"
TP = 50000
Stop_Loss = 60000
Stop_limit = 60500"""



# Functions
#main = order_Monitoring(trading_pair, exchange_name, flag, side, asset_equity, chart_interval, db_name, TP, Stop_Loss, Stop_limit)

#(main.OCO_Placed_update_orderbook(2))