from datetime import datetime
from requests import get
from os import path
import sqlite3


#Exchange Specific Code - WORKING
def get_historical_kline_data(exchange_pair, interval, limit): 
    host = 'https://api.binance.com'
    path = f"/api/v3/klines"
    url = host + path
    
    # make a GET request to the endpoint
    params = {
        "symbol": exchange_pair,
        "interval": interval,
        "limit": limit
    
    }

    response = get(url, params=params) # response = get(url, headers = headers)
    data = response.json()
    #ORDER [0] Timestamp, [1] Open, [2] High, [3] Low, [4] Close, [5] Trading Volume in security
    
    #Gets previous klines for the interval except for the current one
    historical_klines = []
    for i in range(0,len(data)-1): #Captures Data up to the most recent candle
        historical_klines.append(data[i])
    
    #last_recent_list = list(reversed(historical_klines))
    last_recent_list = list(historical_klines)
    #print(historical_klines)
    #print("\n\n\n")
    return last_recent_list #Newest klines come in at the bottom"""
    
def creating_db_file(exchange_pair, exchange_name, interval):
    trading_pair = exchange_pair
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y") #date_and_time.strftime("%b%d%y%H")
    file_name = f"1-DataGathering/data_gathered/{trading_pair}_data/Historical_Klines/" + str(date) + exchange_name + exchange_pair + "interval=" + str(interval) + "kline_data.db"
    
    #f = open(file_name, "w")
    
    #Defining Connection and cursor
    connection = sqlite3.connect(file_name)
    cursor = connection.cursor()

    #Creating Current exchange_tag price table]

    command1 = """CREATE TABLE IF NOT EXISTS
    pair_price(time TEXT, Open FLOAT, High FLOAT, Low FLOAT, Close FLOAT, Volume FLOAT)"""

    cursor.execute(command1)
    connection.commit()

    #Closing the database
    connection.close()

#Collects data on all the previous stimestaps recorded in the file
def time_stamp_collection(exchange_pair, exchange_name, interval):
    trading_pair = exchange_pair
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y") #date_and_time.strftime("%b%d%y%H")
    file_name = f"1-DataGathering/data_gathered/{trading_pair}_data/Historical_Klines/" + str(date) + exchange_name + exchange_pair + "interval=" + str(interval) + "kline_data.db"
    
    #GETS TIMESTAMP OF PREVIOUS RECORDED DATA
    timestamp_log = [] #List that will hold all the timestamp data from the db file

    date_and_time = (datetime.now())
    
    connection = sqlite3.connect(file_name)
    cursor = connection.cursor()

    cursor.execute("Select * FROM pair_price")
    
    list_check = cursor.fetchall()

    for i in range(len(list_check)):
        timestamp_log.append(list_check[i][0])
    
  
    connection.commit()
    #Closing the database
    connection.close()
    return timestamp_log


def printTodatabase(exchange_pair, exchange_name, interval, limit):
    #Gathering data
    historical_klines = get_historical_kline_data(exchange_pair, interval, limit) #Gets historical Kline Data
    
    #Creating name of db file
    trading_pair = exchange_pair
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y") #date_and_time.strftime("%b%d%y%H")
    file_name = f"1-DataGathering/data_gathered/{trading_pair}_data/Historical_Klines/" + str(date) + exchange_name + exchange_pair + "interval=" + str(interval) + "kline_data.db"
  
    try:
        #Checks to see if there's an existing db file inside the data gathering dircetory
        if path.exists(file_name) == True:
            timestamp_log = time_stamp_collection(exchange_pair, exchange_name, interval) #Gets time interval data
            
            #CHECKS TO SEE IF THE TIMESTAMP ALREADY EXISTS WITHIN THE DATABASE FILE
            
            for i in range(len(historical_klines)):
                #Does nothing if the timestamp is already
                if str(historical_klines[i][0]) in timestamp_log:
                    pass
                    #print('Time Exists')
                
                #Adds new data to db file if there is a new 
                else:
                    #print("printing to db")
                    #Defining Connection and cursor
                    connection = sqlite3.connect(file_name)
                    cursor = connection.cursor()

                    current_time = (datetime.now())
                    cursor.execute(f"""INSERT INTO pair_price VALUES ({str(historical_klines[i][0])}, {historical_klines[i][1]}, {historical_klines[i][2]},
                        {historical_klines[i][3]}, {historical_klines[i][4]}, {historical_klines[i][5]})""")
                    connection.commit()
                    connection.close() #Closing the database
        
        else: #Creates new db file
            creating_db_file(exchange_pair, exchange_name, interval) #Creates new file
            printTodatabase(exchange_pair, exchange_name, interval, limit) # Runs program again

    except Exception as e: #Message email that an error on... has occured
        print(f"{file_name}: {str(e)}")
        path.append("ZZ-General_Functions/Programs")
        from Error_handling import Handling_Error
        Handling_Error(e).No_Data_Table_Error(10)


#runs program in a loop
def run(exchange_pair, exchange_name, interval, limit):
    while 1:
        printTodatabase(exchange_pair, exchange_name, interval, limit)

    

#run("BTCUSDT", "Binance", "5m", 10) # Change interval to 1000 (it's the max)

"""
5. CHECKS THE FILE LOG
"""
#Checking market data  database - WORKING
def check(exchange_pair, exchange_name, interval):
    trading_pair = exchange_pair
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y")
    file_name = f"1-DataGathering/data_gathered/{trading_pair}_data/Historical_Klines/" + str(date) + exchange_name + exchange_pair + "interval="+ interval +"kline_data.db"
    print(file_name)
    connection = sqlite3.connect(file_name)
    cursor = connection.cursor()

    cursor.execute("Select * FROM pair_price")
    
    list_check = cursor.fetchall()

    for i in range(len(list_check)):
        print(list_check[i])
    
  
    connection.commit()
    #Closing the database
    connection.close()


#check("BTCUSDT", "Binance", "5m")