from datetime import datetime
from os.path import exists
import sqlite3
from time import time, sleep
from sys import path

""" [1] Getting the Live Margin Account Balance """
class Live_Balance:
    #Initialises variables for use through the class
    def __init__(self, trading_pair, exchange_name, db_name):
        self.trading_pair = trading_pair
        self.exchange_name = exchange_name
        self.db_name = db_name

    # CREATES A DATABASE FILE 
    def creating_db_file(self):    
        date_and_time = (datetime.now())
        date = date_and_time.strftime("%b%d%y")
        ###BELOW NEEDS TO BE EDITED
        file_name = f"3-AccountBalance/data_gathered/{self.trading_pair}_data/{date}{self.exchange_name}{self.trading_pair}{self.db_name}_data.db"
        f = open(file_name, "x")
        
        #Defining Connection and cursor
        connection = sqlite3.connect(file_name)
        cursor = connection.cursor()

        #Creating Current exchange_tag balance table
        command1 = f"""CREATE TABLE IF NOT EXISTS
        account_balance(time TEXT, Balance FLOAT, Locked FLOAT, Borrowed FLOAT, Interest FLOAT, NetAsset FLOAT)"""

        cursor.execute(command1)
        connection.commit()

        #Closing the database
        connection.close()

    # Gets account Balance Information
    def get_Balance_Info(self):
        # Setting Parameters
        params = {
            "timestamp": int(round(time() * 1000, 0))

        }

        # Using Binance REST API
        path.append("Misc/Programs")
        from Binance_Rest_Api import run

        # print("Live Trade")
        
        method = "GET"
        request_path = "/sapi/v1/margin/account"
        r_type = 0 # Private request

        Balance_Data_list = run(method, request_path, params, r_type)['userAssets']
        
        # Searching List for Specific Pair
        Balance_Data = []
        for i in range(len(Balance_Data_list)):
            if Balance_Data_list[i]['asset'] == self.trading_pair:
                Balance_Data.append(Balance_Data_list[i])
            else: pass

        return Balance_Data[0]
    
    # Printing Lve Asset Balance Data to DB
    def printTodatabase(self):
        # Getting Balance Information
        asset_Data = self.get_Balance_Info()
        free_Balance = asset_Data["free"]
        locked_Balance = asset_Data["locked"]
        borrowed_Balance = asset_Data["borrowed"]
        interest = asset_Data["interest"]
        net_Asset = asset_Data["netAsset"]

        # Setting Filiname
        
        date_and_time = (datetime.now())
        date = date_and_time.strftime("%b%d%y")
        file_name = f"3-AccountBalance/data_gathered/{self.trading_pair}_data/{date}{self.exchange_name}{self.trading_pair}{self.db_name}_data.db"
        try:
            #Checks to see if there's an existing db file inside the data gathering dircetory
            if exists(file_name) == True:
                # Only Adds a Balance if new one has changed from the previous one
                connection = sqlite3.connect(file_name)
                cursor = connection.cursor()
                
                # [1] Check if there's a recent entry in the DB
                cursor.execute("Select * FROM account_balance")
                list_check = cursor.fetchall()
                current_time = (datetime.now())
                formatted_time = str(current_time.strftime('"%H:%M:%S"'))

                # [1.1] If the orderbook is empty
                if not list_check:
                    cursor.execute(f"""INSERT INTO account_balance (time, Balance, Locked, Borrowed, Interest, NetAsset) 
                                VALUES ({formatted_time}, {free_Balance}, {locked_Balance}, {borrowed_Balance}, {interest}, {net_Asset})""")
                    connection.commit()
                    connection.close() #Closing the database
                
                # [1.2] IF the the Current Asset Balance from the Exchange isn't the same as the last db entry
                elif float(list_check[-1][1]) != float(free_Balance):
                    cursor.execute(f"""INSERT INTO account_balance (time, Balance, Locked, Borrowed, Interest, NetAsset) 
                                VALUES ({formatted_time}, {free_Balance}, {locked_Balance}, {borrowed_Balance}, {interest}, {net_Asset})""")
                    connection.commit()
                    connection.close() #Closing the database

                # [1.3] Pass for everything else
                else: pass


            else: #Creates new db file
                self.creating_db_file() #Creates new file

        except Exception as e: 
            program_name = f"3-AccountBalance/Programs/{self.trading_pair}/Live_Account_Balance_{self.trading_pair}.py"
            # RECORDING ERROR
            path.append("00-Run_Log/Programs")
            from Log_Output import Record_Output
            Record_Output(trading_pair, exchange_name, e, program_name)
            
            # HANDLING NO DATA TABLE ERROR
            path.append("ZZ-General_Functions/Programs")
            from Error_handling import Handling_Error
            Handling_Error(e).No_Data_Table_Error()
        



""" [2] RUNS THE PROGRAM """   
def run(trading_pair, exchange_name, db_name, wait_time = 1):
    while 1:
        try:
            # [1] GETTING THE CURRENT BALANCE FROM THE EXCHANGE
            main = Live_Balance(trading_pair, exchange_name, db_name)
            main.printTodatabase()
            sleep(wait_time)
        except  Exception as e:
            program_name = f"3-AccountBalance/Programs/{trading_pair}/Live_Account_Balance_{trading_pair}.py"
            # RECORDING ERROR
            path.append("00-Run_Log/Programs")
            from Log_Output import Record_Output
            Record_Output(trading_pair, exchange_name, e, program_name)
            
            # HANDLING NO DATA TABLE ERROR
            path.append("ZZ-General_Functions/Programs")
            from Error_handling import Handling_Error
            Handling_Error(e).No_Data_Table_Error(1)




'''
# TESTING
# Variables
trading_pair = "USDT"
exchange_name = "Binance"
db_name = "Live_Balance"

# Creating a new instance of the class
#main = Live_Balance(trading_pair, exchange_name, db_name)

# main.creating_db_file() -> WORKING
# print(main.get_Balance_Info()) -> WORKING
# main.printTodatabase() -> WORKING

run(trading_pair, exchange_name, db_name)
'''