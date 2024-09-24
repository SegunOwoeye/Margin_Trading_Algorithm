#General Use Imports
from datetime import datetime
import sqlite3
from os.path import exists
from sys import path
from time import sleep
from math import floor, log10

### Implements a Trailing Stop 
class Monitor:
    # [1] Initialising Variables
    def __init__(self, trading_pair, exchange_name, flag, chart_interval, db_name):
        self.trading_pair = trading_pair
        self.exchange_name = exchange_name
        self.flag = flag
        self.db_name = db_name
        self.chart_interval = chart_interval

    # [2] Gets the current price of the asset
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

    
    # [3] Getting Entry Prices
    def get_orderbook_data(self):
        """
        None -> Orderbook is empty
        Ready -> A signal has been given and a new order has been submitted to the book
        Entered -> Depending on the Side (Long/Short) a position has been entered and is now being monitored 9Active
        Closed -> The position has been closed 
        """
        
        date_and_time = (datetime.now())
        date = date_and_time.strftime("%y")
        ###BELOW NEEDS TO BE EDITED
        if self.flag == 0: # Live
            file_name = f"4-Strategies/data_gathered/{self.trading_pair}_data/{str(date)}{self.exchange_name}{self.trading_pair}{self.db_name}.db"
        elif self.flag == 1: # Demo
            file_name = f"4-Strategies/data_gathered/{self.trading_pair}_data/{str(date)}{self.exchange_name}{self.trading_pair}{self.db_name}DEMO.db"
        
        
        # Check to see if the orderbook exists | Return "None"
        if exists(file_name) == False:
            return None
        
        # Connecting to database
        connection = sqlite3.connect(file_name)
        cursor = connection.cursor()
        cursor.execute("Select * FROM trade_data")
        list_check = cursor.fetchall()

        # If the orderbook is empty | Return "None"
        if not list_check:
            return None
        
        connection.commit()
        connection.close() #Closing the database
        return list_check
        # Getting a list of the order_status and their numbers in the orderbook
        orderbook_pos = []
        order_status = []    
        order_side = [] 
        order_equity = [] 
        open_funds_traded = []  
        take_profit = []
        stop_loss = []
        stop_limit = []
        entry_OrderID = []
        entry_price = []
        TP_OrderID = []
        SL_OrderID = []
        for i in range(len(list_check)):
            orderbook_pos.append(i)
            order_status.append(list_check[i][23])
            order_side.append(list_check[i][3])
            order_equity.append(list_check[i][7])
            open_funds_traded.append(list_check[i][15])
            take_profit.append(list_check[i][9])
            stop_loss.append(list_check[i][10])
            stop_limit.append(list_check[i][11]) # 14. 13
            entry_OrderID.append(list_check[i][13])
            entry_price.append(list_check[i][14])
            TP_OrderID.append(list_check[i][24])
            SL_OrderID.append(list_check[i][25])


        connection.commit()
        connection.close() #Closing the database

        return [orderbook_pos, order_status, order_side, order_equity, open_funds_traded, take_profit, 
                stop_loss, stop_limit, entry_OrderID, entry_price, TP_OrderID, SL_OrderID]
            
    # [4] Manage Trade
    def manage_trade(self):
        # [4.1] Importing Data
        data = self.get_orderbook_data()
        current_price = self.get_current_price()

        # [4.1.1] Getting a list of the order_status and their numbers in the orderbook
        orderbook_pos = []
        order_status = []    
        order_side = [] 
        order_equity = [] 
        open_funds_traded = []  
        take_profit = []
        S_loss = []
        S_limit = []
        entry_OrderID = []
        entry_price = []
        TP_OrderID = []
        SL_OrderID = []

        # [4.2] Filtering out Data if Closed
        for i in range(len(data)):
            if data[i][23] == "Closed": # Filtering Out Closed Positions
                pass
            else:
                orderbook_pos.append(i)
                order_status.append(data[i][23])
                order_side.append(data[i][3])
                order_equity.append(data[i][7])
                open_funds_traded.append(data[i][15])
                take_profit.append(data[i][9])
                S_loss.append(data[i][10])
                S_limit.append(data[i][11]) # 14. 13
                entry_OrderID.append(data[i][13])
                entry_price.append(data[i][14])
                TP_OrderID.append(data[i][24])
                SL_OrderID.append(data[i][25])



        # [4.2.1] If the length of the list is 0 return
        if len(order_status) == 0:
            return 0
        else: pass

        # [4.3] Running Calculations
        for i in range(len(order_status)):
            """# Trailing Percentage
            trailing_percentage = round((take_profit[i]-entry_price[i])/entry_price[i] * 2, 4)
            # [4.3.0] Getting Profit Percentage
            profit_percentage = (current_price - entry_price[i])/entry_price[i] * 100
            profit_percentage = round(profit_percentage,3)/100
            if order_side[i] == "SHORT":
                profit_percentage = -profit_percentage"""

            # [4.3.1] Trailing Stop Loss Logic
            if profit_percentage > 0:
                if order_side[i] == "LONG": # LONG
                    # new_stop_loss = entry_price + (current_price - entry_price) * (1 - trailing_percent)
                    new_stop_loss = entry_price[i] + (current_price - entry_price[i])*(1-trailing_percentage)
                    stop_loss = max(new_stop_loss, S_loss[i])
                else: # SHORT
                    # new_stop_loss = entry_price - (entry_price - current_price) * (1 - trailing_percent)
                    new_stop_loss = entry_price[i] - (entry_price[i] - current_price) * (1-trailing_percentage)
                    stop_loss = min(S_loss[i], new_stop_loss)
                
                stop_loss = round(stop_loss, -int(floor(log10(abs(stop_loss)))) + (8 - 2))

                # [4.3.2] Setting Stop Limit if Long or Short
                if order_side[i] == "LONG":
                    stop_limit = stop_loss * (1 - (1)/100)
                    stop_limit = round(stop_limit, -int(floor(log10(abs(stop_limit)))) + (8 - 2))
                elif order_side[i] == "SHORT":
                    stop_limit = stop_loss * (1 + (1)/100)
                    stop_limit = round(stop_limit, -int(floor(log10(abs(stop_limit)))) + (8 - 2))
                # TrialData
                #data[3][i] = 0.00048
                #data[5][i] = 65000

                # [4.3.3] Creating new OCO Order
                # 1 Cancel out of previous OCO ->
                # 2 Place a new OCO with the OG TP and the new SL
                # 3 Updates orderbook with new information
                path.append("7-Placing_Orders/Programs") 
                from Cancel_OCO_Orders import order
                main = order(trading_pair=self.trading_pair, exchange_name=self.exchange_name, flag=self.flag, side=order_side[i], asset_equity=order_equity[i], 
                            chart_interval=self.chart_interval, db_name=self.db_name, TP=take_profit[i], Stop_Loss=stop_loss, Stop_Limit=stop_limit,
                            OrderID=[TP_OrderID[i],SL_OrderID[i]])
                
                main.Entered_update_orderbook(i)

        return 1 # If all processes have been completed properly this should return 1


### Runs the program in an Infinite Loop
def run(trading_pair: str, exchange_name: str, flag: int, chart_interval: str, db_name: str):
    strat_name = db_name.replace("_Orders", "") 
    while 1:
        try: 
            """ CHECKS TO SEE IF THE REQUIRED FILES ARE PRESENT, IF NOT IT WAITS"""
            # [1] Gets required filenames
            date_and_time = (datetime.now())
            orderbook_date = date_and_time.strftime("%y")

            if flag == 0: # Live
                orderbook_filename = f"4-Strategies/data_gathered/{trading_pair}_data/{str(orderbook_date)}{exchange_name}{trading_pair}{db_name}.db"
            elif flag == 1: # Demo
                orderbook_filename = f"4-Strategies/data_gathered/{trading_pair}_data/{str(orderbook_date)}{exchange_name}{trading_pair}{db_name}DEMO.db"

            # [2] Checks to see if required files exists
            if exists(orderbook_filename) == True:
                main = Monitor(trading_pair, exchange_name, flag, chart_interval, db_name)
                if main.manage_trade() == 1: # Successful Trailing SL
                    sleep(5)
                else:
                    sleep(5)
            else:
                sleep(5)
        except Exception as e:
            program_name = f"8-Risk_Managment/Programs/{strat_name}/Trailing_Stop_Loss_{trading_pair}{chart_interval}{strat_name}.py"
            path.append("00-Run_Log/Programs")
            from Log_Output import Record_Output
            Record_Output(trading_pair, "Binance", e, program_name)
            sleep(1)
           

'''

""" TESTING """

# FOR SHORTING
# Variables
trading_pair = "BTCUSDT"
exchange_name = "Binance"
flag = 0
chart_interval = "5m"
db_name = "Strategy2_Orders"


# RUN
#run(trading_pair, exchange_name, flag, chart_interval, db_name)
#main = Monitor(trading_pair, exchange_name, flag, chart_interval, db_name)
#(main.manage_trade())

'''