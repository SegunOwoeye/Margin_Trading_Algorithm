#General Use Imports
from datetime import datetime
import sqlite3
from os.path import exists
from sys import path
import time

class Monitor:
    # [1] Initialises Variables
    def __init__(self, trading_pair, exchange_name, flag, chart_interval, db_name):
        self.trading_pair = trading_pair
        self.exchange_name = exchange_name
        self.flag = flag
        self.db_name = db_name
        self.chart_interval = chart_interval


    # [2] Gets the order status and other orderbook information
    def get_status(self):
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
        
        # Getting a list of the order_status and their numbers in the orderbook
        orderbook_pos = []
        order_status = []    
        order_side = [] 
        order_equity = [] 
        open_funds_traded = []  
        take_profit = []
        stop_loss = []
        stop_limit = []
        TP_OrderID = []
        SL_OrderID = []
        entry_price = []
        for i in range(len(list_check)):
            orderbook_pos.append(i)
            order_status.append(list_check[i][23])
            order_side.append(list_check[i][3])
            order_equity.append(list_check[i][7])
            open_funds_traded.append(list_check[i][15])
            take_profit.append(list_check[i][9])
            stop_loss.append(list_check[i][10])
            stop_limit.append(list_check[i][11])
            TP_OrderID.append(list_check[i][24])
            SL_OrderID.append(list_check[i][25])
            entry_price.append(list_check[i][14])

        connection.commit()
        connection.close() #Closing the database

        return orderbook_pos, order_status, order_side, order_equity, open_funds_traded, take_profit, stop_loss, stop_limit, TP_OrderID, SL_OrderID, entry_price
    



    # [3] Based on the status of the Order, actions will be submitted to take place
    def order_action(self):
        """
        None -> Orderbook is empty
        Ready -> A signal has been given and a new order has been submitted to the book
        Entered -> Depending on the Side (Long/Short) a position has been entered and is now being monitored Active
        Initial_OCO_Placed -> Bot has entered the market and TP/SL orders have been sent to exchange
        Final_OCO_Placed -> Initial OCO has been canceled for a higher SL to guarantee profits
        Closed -> The position has been closed 
        """
        
        # [3.1] Importing orderbook_status_info
        orderbook_status_info = self.get_status()

        # [3.1.1] Checking to see if the orderbook is empty
        if orderbook_status_info == None: # Do nothing as there are no orders
            return 
        
        # [3.1.2] Getting orderbook data
        orderbook_pos = orderbook_status_info[0]
        order_status = orderbook_status_info[1]
        order_side = orderbook_status_info[2]
        order_equity = orderbook_status_info[3]
        open_funds_traded = orderbook_status_info[4]
        take_profit = orderbook_status_info[5]
        stop_loss = orderbook_status_info[6]
        stop_limit = orderbook_status_info[7]
        TP_OrderID = orderbook_status_info[8]
        SL_OrderID = orderbook_status_info[9]
        entry_price = orderbook_status_info[10]
        #print(order_equity)
        

        # [3.2] Submitting Actions to Database depending on Orderbook Status
        for i in range(len(orderbook_pos)):
            # Changing Path
            path.append("7-Placing_Orders/Programs") 

            # [3.2.1] Function for placing the market order and updating the orderbook using the current position number
            if order_status[i] == "Ready": # -> WORKING
                from Margin_Orders import order
                main = order(self.trading_pair, self.exchange_name, self.flag, order_side[i], order_equity[i], self.chart_interval, self.db_name)
                main.Ready_update_orderbook(i)

            # [3.2.2] Function for placing the OCO order and updating the orderbook using the position number
            elif order_status[i] == "Entered": # -> Working
                from OCO_Orders import order
                main = order(self.trading_pair, self.exchange_name, self.flag, order_side[i], open_funds_traded[i], self.chart_interval, self.db_name, 
                             take_profit[i], stop_loss[i], stop_limit[i])
                main.Entered_update_orderbook(i)
            
            # [3.2.3] Function for checking to see if OG OCo can be canceled and a new one added to gaurantee profits and updating the orderbook using the position number
            elif order_status[i] == "Initial_OCO_Placed": # -> Working
                from Cancel_OCO_Orders import order
                main = order(trading_pair=self.trading_pair, exchange_name=self.exchange_name, flag=self.flag, chart_interval=self.chart_interval, 
                             db_name=self.db_name, OrderID=[TP_OrderID[i], SL_OrderID[i]], TP=take_profit[i], Stop_Loss=stop_loss[i], Stop_Limit=stop_limit[i], 
                             side=order_side[i], asset_equity=open_funds_traded[i], entry_price=entry_price[i])
                main.ReEntered_update_orderbook(i)


            # [3.2.4] Do nothing and wait for OCO order on exchange to do something
            elif order_status[i] == "Final_OCO_Placed" or order_status[i] == "Initial_OCO_Placed": # WORKING
                # Changing Path
                path.append("5-Trade_Monitoring/Programs") 
                # Create a function to monitor if live on the exchange the OCO order has been executed or not
                from Tracking_Live_Orders import order_Monitoring
                main = order_Monitoring(self.trading_pair, self.exchange_name, self.flag, order_side[i], open_funds_traded[i], 
                                        self.chart_interval, self.db_name, take_profit[i], stop_loss[i], stop_limit[i])
                main.OCO_Placed_update_orderbook(i)

            
            # Do Nothing if the order has been closed
            elif order_status[i] == "Closed": # Do Nothing
                pass
        
        



def run(trading_pair, exchange_name, flag, chart_interval, db_name):
    while 1:
        time.sleep(5)
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
                main.order_action()
                time.sleep(1)
            
            # [3] Waits 1 seconds if the required filenames don't exist
            else:
                time.sleep(1)

        except Exception as e:
            # RECORDING ERROR
            program_name = f"5-Trade_Monitoring/Programs/{trading_pair}/Orderbook_Monitoring_{trading_pair}Interval={chart_interval}.py"
            path.append("00-Run_Log/Programs")
            from Log_Output import Record_Output
            Record_Output(trading_pair, exchange_name, e, program_name)

            # HANDLING NO DATA TABLE ERROR
            path.append("ZZ-General_Functions/Programs")
            from Error_handling import Handling_Error
            Handling_Error(e).No_Data_Table_Error()



"""        
# TESTING
#Variables
trading_pair = "BTCUSDT"
exchange_name = "Binance"
flag = 1
chart_interval = "5m"

db_name = "Strategy2_Orders"



run(trading_pair, exchange_name, flag, chart_interval, db_name)

"""


'''

""" TESTING """
#Variables
trading_pair = "BTCUSDT"
exchange_name = "Binance"
flag = 1
chart_interval = "5m"

db_name = "Strategy2_Orders"

# Functions


print(main.order_action())

'''
