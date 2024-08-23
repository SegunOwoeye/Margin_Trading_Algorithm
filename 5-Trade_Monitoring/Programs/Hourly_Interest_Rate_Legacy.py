from datetime import datetime
from os.path import exists
import sqlite3
import time 
from sys import path

class Hourly_Interest_Rates:
    #Initialises variables for use through the class
    def __init__(self, trading_pair):
        self.trading_pair = trading_pair
    
    #Splits the trading pair into individual assets
    def pair_split(self):
        if "USDT" in self.trading_pair:
            pair1 = self.trading_pair.replace("USDT","")
            pair2 = "USDT"
            return pair1, pair2

        elif "USDC" in self.trading_pair:
            pair1 = self.trading_pair.replace("USDC","")
            pair2 = "USDC"
            return [pair1, pair2]

    # CREATES DB FILE
    def creating_db_file(self): # WORKING
        #getting individual pairs

        date_and_time = (datetime.now())
        date = date_and_time.strftime("%b%d%y") # 5-Trade_Monitoring\data_gathered\BTCUSDT_data
        file_name = f"5-Trade_Monitoring/data_gathered/{self.trading_pair}_data/{date}{self.trading_pair}HIR_data.db"
        f = open(file_name, "x")
        
        #Defining Connection and cursor
        connection = sqlite3.connect(file_name)
        cursor = connection.cursor()

        #Creating Current exchange_tag price table]

        command1 = f"""CREATE TABLE IF NOT EXISTS
        HIR_Data(time TEXT, HIR FLOAT)"""

        cursor.execute(command1)
        connection.commit()

        #Closing the database
        connection.close()
    
    # GETS THE PRECISION DATA
    def get_data(self): # WORKING
        
        pair1 = self.pair_split()[0]
        path.append("Misc/Programs")
        from Binance_Rest_Api import run
        

        #FOR HIR
        params = {
            "assets": {pair1},
            "isIsolated": "FALSE"
        }

        method = "GET"
        path = "/sapi/v1/margin/next-hourly-interest-rate"
        r_type = 0

        return run(method, path, params, r_type)[0]['nextHourlyInterestRate']

    def printTodatabase(self):
        # Getting precision data
        hir = self.get_data()
        pair1 = self.pair_split()[0]

        date_and_time = (datetime.now())
        date = date_and_time.strftime("%b%d%y") # 5-Trade_Monitoring\data_gathered\BTCUSDT_data
        file_name = f"5-Trade_Monitoring/data_gathered/{self.trading_pair}_data/{date}{self.trading_pair}HIR_data.db"
        try:
            #Checks to see if there's an existing db file inside the data gathering dircetory
            if exists(file_name) == True:
                # Sleep intervals
                wait_time = 60*60 # 1 hour

                #Checks to see if program returns anything
                connection = sqlite3.connect(file_name)
                cursor = connection.cursor()

                current_time = (datetime.now())
                formatted_time = str(current_time.strftime('"%H:%M:%S"'))
                cursor.execute(f"""INSERT INTO HIR_Data (time, HIR) VALUES 
                               ({formatted_time}, {hir})""")

                connection.commit()
                connection.close() #Closing the database
                

                time.sleep(wait_time) #RUNS THE PROGRAM EVERY INTERVAL PERIOD
            
            else: #Creates new db file
                Hourly_Interest_Rates(self.trading_pair).creating_db_file() #Creates new file

        except Exception as e: 
            program_name = f"5-Trade_Monitoring/Programs/{self.trading_pair}/asset_precision_{self.trading_pair}.py"
            path.append("00-Run_Log/Programs")
            from Log_Output import Record_Output
            Record_Output(self.trading_pair, "Binance", e, program_name)

#5-Trade_Monitoring\asset_precision_Legacy.py

def run(trading_pair):
    while 1:
        try: 
            Hourly_Interest_Rates(trading_pair).printTodatabase()
            time.sleep(1)
        except Exception as e:
            program_name = f"5-Trade_Monitoring/Programs/{trading_pair}/asset_precision_{trading_pair}.py"
            path.append("00-Run_Log/Programs")
            from Log_Output import Record_Output
            Record_Output(trading_pair, "Binance", e, program_name)
    

# TESTING

#run("BTCUSDT")

#print(Hourly_Interest_Rates("BTCUSDT").get_data())

