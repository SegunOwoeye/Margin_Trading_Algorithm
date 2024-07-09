from datetime import datetime
from requests import get
from os.path import exists
import sqlite3
import time 

class asset_precision:
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
        pairs = asset_precision(self.trading_pair).pair_split()
        pair1 = pairs[0]
        pair2 = pairs[1]

        date_and_time = (datetime.now())
        date = date_and_time.strftime("%b%d%y") # 5-Trade_Monitoring\data_gathered\BTCUSDT_data
        file_name = f"5-Trade_Monitoring/data_gathered/{self.trading_pair}_data/{date}{self.trading_pair}precision_data.db"
        f = open(file_name, "x")
        
        #Defining Connection and cursor
        connection = sqlite3.connect(file_name)
        cursor = connection.cursor()

        #Creating Current exchange_tag price table]

        command1 = f"""CREATE TABLE IF NOT EXISTS
        Precision_Data(time TEXT, {pair1} INT, {pair2} INT)"""

        cursor.execute(command1)
        connection.commit()

        #Closing the database
        connection.close()
    
    # GETS THE PRECISION DATA
    def get_data(self): # WORKING
        # Precision is the total amount of Asset significant figures that can be present in the orderQTy field
        host = 'https://api.binance.com'
        path = f"/api/v3/exchangeInfo?symbol={self.trading_pair}"
        url = host + path
        
        # make a GET request to the endpoint
        response = get(url) # response = get(url, headers = headers)
        precision = response.json()['symbols'][0]['baseAssetPrecision']

        return int(precision)

    def printTodatabase(self):
        # Getting precision data
        precision = asset_precision(self.trading_pair).get_data()
        pairs = asset_precision(self.trading_pair).pair_split()
        pair1 = pairs[0]
        pair2 = pairs[1]

        date_and_time = (datetime.now())
        date = date_and_time.strftime("%b%d%y") # 5-Trade_Monitoring\data_gathered\BTCUSDT_data
        file_name = f"5-Trade_Monitoring/data_gathered/{self.trading_pair}_data/{date}{self.trading_pair}precision_data.db"
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
                cursor.execute(f"""INSERT INTO Precision_Data (time, {pair1}, {pair2}) VALUES 
                               ({formatted_time}, {precision}, {precision})""")

                connection.commit()
                connection.close() #Closing the database
                

                time.sleep(wait_time) #RUNS THE PROGRAM EVERY INTERVAL PERIOD
            
            else: #Creates new db file
                asset_precision(self.trading_pair).creating_db_file() #Creates new file

        except Exception as e: #Message email that an error on... has occured
            print(f"5-Trade_Monitoring/Programs/{self.trading_pair}/asset_precision_{self.trading_pair}.py has error: " + str(e))

#5-Trade_Monitoring\asset_precision_Legacy.py

def run(trading_pair):
    while 1:
        try: 
            asset_precision(trading_pair).printTodatabase()
            time.sleep(1)
        except Exception as e:
            print(f"5-Trade_Monitoring/Programs/{trading_pair}/asset_precision_{trading_pair}.py has error: " + str(e))

# TESTING

#run("BTCUSDT")

