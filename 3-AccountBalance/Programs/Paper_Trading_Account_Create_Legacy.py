from datetime import datetime
from os.path import exists
from sys import path
import sqlite3
from time import sleep

""" [1] Creating And Managing the Paper Trading Account"""
class Paper_Trading:
    # [1.0] Initialising Class Variables
    def __init__(self, trading_pair, exchange_name, db_name, balance, strat_db_name, R_Trading_Pairs):
        self.trading_pair = trading_pair
        self.exchange_name = exchange_name
        self.db_name = db_name
        self.balance = balance
        self.strat_db_name = strat_db_name
        self.R_Trading_Pairs = R_Trading_Pairs

    # [1.1] CREATES A DATABASE FILE 
    def creating_db_file(self):    
        date_and_time = (datetime.now())
        date = date_and_time.strftime("%b%d%y")
        file_name = f"3-AccountBalance/data_gathered/{self.trading_pair}_data/{date}{self.exchange_name}{self.trading_pair}{self.db_name}_data.db"
        f = open(file_name, "x")
        
        #Defining Connection and cursor
        connection = sqlite3.connect(file_name)
        cursor = connection.cursor()

        #Creating Current exchange_tag balance table
        command1 = f"""CREATE TABLE IF NOT EXISTS
        account_balance(time TEXT, Balance FLOAT)"""

        cursor.execute(command1)
        connection.commit()

        #Closing the database
        connection.close()

    # [1.2] ADDS Paper ASSET TO ACCOUNT TO PAPER TRADE WITH
    def add_balance(self):
        date_and_time = (datetime.now())
        date = date_and_time.strftime("%b%d%y")
        file_name = f"3-AccountBalance/data_gathered/{self.trading_pair}_data/{date}{self.exchange_name}{self.trading_pair}{self.db_name}_data.db"
        
        connection = sqlite3.connect(file_name)
        cursor = connection.cursor()

        current_time = (datetime.now())
        formatted_time = str(current_time.strftime('"%H:%M:%S"'))
        cursor.execute(f"""INSERT INTO account_balance (time, Balance) VALUES ({formatted_time}, {float(self.balance)})""")

        connection.commit()
        connection.close() #Closing the database

    # [1.3] Creates paper trading account and adds a balance to it
    def create_account(self):
        self.creating_db_file()
        self.add_balance()

    # [1.4] Gets Orderbook Data
    def get_orderbook_data(self):
        # Getting file name
        date_and_time = (datetime.now())
        date = date_and_time.strftime("%y")
        file_name = f"4-Strategies/data_gathered/{self.R_Trading_Pairs}_data/{str(date)}{self.exchange_name}{self.R_Trading_Pairs}{self.strat_db_name}DEMO.db"
        
        # Getting All Data from DB file
        connection = sqlite3.connect(file_name)
        cursor = connection.cursor()
        cursor.execute("Select * FROM trade_data")
        data_list = cursor.fetchall()
        connection.close() #Closing the database

        # Seperating Trades into 2 Categories, LONG AND SHORTS
        long_orders = []
        short_orders = []
        for i in range(len(data_list)):
            
            if data_list[i][3] == "LONG": # Captures Long Orders
                long_orders.append(data_list[i])
            elif data_list[i][3] == "SHORT": # Captures Short Orders
                short_orders.append(data_list[i])
            else: # Do Nothing
                pass
        
        return long_orders, short_orders
    
    # [1.5.1] Long Paper Trading Balance
    def long_adjusting(self):
        long_orders = self.get_orderbook_data()[0]
        
        """ [A] CHECKING TO SEE IF ORDERBOOK STATUS IS CLOSED OR NOT"""
        # Initialising Variables
        long_exit_balance_list = []
        long_entry_balance_list = []
        for i in range(len(long_orders)):
            if (long_orders[i][23]) == "Closed":
                exit_balance = (long_orders[i][6] * ((long_orders[i][19]*long_orders[i][5]) + 100)/100)
                long_exit_balance_list.append(exit_balance)
                long_entry_balance_list.append(long_orders[i][6])

            else: 
                # Trade is still open, therefore there is no exit balance
                long_entry_balance_list.append(long_orders[i][6])

        # Getting totals of lists
        long_exit_balance = sum(long_exit_balance_list)
        long_entry_balance = sum(long_entry_balance_list)
        
        # Sum difference of all trades
        long_total_diff = (long_exit_balance-long_entry_balance)

        return long_total_diff

    # [1.5.2] Short Paper Trading Balance
    def short_adjusting(self):
        short_orders = self.get_orderbook_data()[1]
        
        """ [A] CHECKING TO SEE IF ORDERBOOK STATUS IS CLOSED OR NOT"""
        # Initialising Variables
        short_exit_balance_list = []
        short_entry_balance_list = []
        for i in range(len(short_orders)):
            if (short_orders[i][23]) == "Closed":
                # Balance Calculations
                exit_balance = (short_orders[i][6] * short_orders[i][14] * ((short_orders[i][19]*short_orders[i][5]) + 100)/100)
                entry_balance = short_orders[i][6] * short_orders[i][14]

                # Saving Data to a list
                short_exit_balance_list.append(exit_balance)
                short_entry_balance_list.append(entry_balance)
            else: 
                # Trade is still open, therefore there is no exit balance
                entry_balance = short_orders[i][6] * short_orders[i][14]
                short_entry_balance_list.append(entry_balance)

        # Getting totals of lists
        short_exit_balance = sum(short_exit_balance_list)
        short_entry_balance = sum(short_entry_balance_list)
        
        # Sum difference of all trades
        short_total_diff = (short_exit_balance-short_entry_balance)
        
        return short_total_diff


    # [1.5] Adjusts the paper trading Balance
    def adjusting_balance(self):
        # Getting Adjustment Data
        long_total_diff = self.long_adjusting()
        short_total_diff = self.short_adjusting()
        
        # Total difference
        total_diff = long_total_diff + short_total_diff


        # Setting Up Date
        date_and_time = (datetime.now())
        date = date_and_time.strftime("%b%d%y")
        
        """ [B] Accessing Account Details from DB file"""
        long_file_name = f"3-AccountBalance/data_gathered/{self.trading_pair}_data/{date}{self.exchange_name}{self.trading_pair}{self.db_name}_data.db"
        connection = sqlite3.connect(long_file_name)
        cursor = connection.cursor()
        cursor.execute("Select * FROM account_balance")
        balance_list = cursor.fetchall()
        recent_balance = balance_list[-1][1]
        

        """ [C] Checking to see if this is the first entry of account balance or Not. """
        if len(balance_list) == 1: # Adds new balance if it's the first entry
            new_balance = recent_balance + total_diff
            current_time = (datetime.now())
            formatted_time = str(current_time.strftime('"%H:%M:%S"'))
            cursor.execute(f"""INSERT INTO account_balance (time, Balance) VALUES ({formatted_time}, {float(new_balance)})""")
            connection.commit()
            connection.close() #Closing the database

        else: # For 1+ Entry
            penultimate_balance = balance_list[-2][1]
            # Checking to see whether there has been a change in the account balance
            if round((recent_balance-penultimate_balance),2) == round(total_diff,2): # There has been no change in account balance
                connection.close() #Closing the database
                pass
            else: # There is a change in accont balance
                new_balance = recent_balance + total_diff
                current_time = (datetime.now())
                formatted_time = str(current_time.strftime('"%H:%M:%S"'))
                cursor.execute(f"""INSERT INTO account_balance (time, Balance) VALUES ({formatted_time}, {float(new_balance)})""")
                connection.commit()
                connection.close() #Closing the database



def run(trading_pair, exchange_name, db_name, balance, strat_db_name, R_Trading_Pairs):
    
    while 1:
        try: 
            date_and_time = (datetime.now())
            date = date_and_time.strftime("%b%d%y")
            file_name = file_name = f"3-AccountBalance/data_gathered/{trading_pair}_data/" + str(date) + exchange_name + trading_pair + str(db_name) + "_data.db"  
            
            # Creating a new instance of the class
            main = Paper_Trading(trading_pair, exchange_name, db_name, balance, strat_db_name, R_Trading_Pairs)

            # Checks to see if the db file exists
            if exists(file_name) == True: # Check and Alter Account Balance based on positions made
                main.adjusting_balance()
            else: #Create New paper Trading Account
                main.create_account()
            sleep(1)
        except Exception as e: # ERROR HANDLING
            program_name = f"3-AccountBalance/Programs/{trading_pair}/Paper_Trading_Account_create_{trading_pair}.py"
            # RECORDING ERROR
            path.append("00-Run_Log/Programs")
            from Log_Output import Record_Output
            Record_Output(trading_pair, exchange_name, e, program_name)
            
            # HANDLING NO DATA TABLE ERROR 
            path.append("ZZ-General_Functions/Programs")
            from Error_handling import Handling_Error
            Handling_Error(e).No_Data_Table_Error()
    

'''
""" TESTING """
# Variables
trading_pair = "USDT"
exchange_name = "Binance"
db_name = "Demo_Balance"
balance = 40000
strat_db_name = "Strategy2_Orders"
R_Trading_Pairs = "BTCUSDT"

### Creating a new instance of the class ###
#main = Paper_Trading(trading_pair, exchange_name, db_name, balance, strat_db_name, R_Trading_Pairs)

# main.creating_db_file() -> WORKING
# main.add_balance() -> WORKING
# main.create_account() #-> WORKING
# print(main.get_orderbook_data()) -> WORKING
# main.long_adjusting() -> WORKING
# main.short_adjusting() -> WORKIN

#main.adjusting_balance()


run(trading_pair, exchange_name, db_name, balance, strat_db_name, R_Trading_Pairs)

'''