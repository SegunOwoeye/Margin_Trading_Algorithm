#!/usr/bin/python3.8.5

import websocket
import rel

from datetime import datetime
from os import remove
from os.path import exists
from sys import path
import sqlite3
from json import loads
from functools import partial


"""
1. CODE FOR CREATING DATABASE AND WRITING ORDERBOOK DATA TO DATABASE
"""

#exchange_pair = "BTCUSDT"

#Generic Code - WORKING
def creating_db_file(exchange_pair, exchange_name, interval):
    trading_pair = exchange_pair
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")
    file_name = f"1-DataGathering/data_gathered/{trading_pair}_data/Live_Data/" + str(date) + exchange_name + exchange_pair + "interval=" + str(interval) + "kline_data.db"
    
    #f = open(file_name, "w")
    
    #Defining Connection and cursor
    connection = sqlite3.connect(file_name)
    cursor = connection.cursor()

    #Creating Current exchange_tag price table]

    command1 = """CREATE TABLE IF NOT EXISTS
    pair_price(time TEXT, Open FLOAT, High FLOAT, Low FLOAT, Close FLOAT, Volume FLOAT)"""

    cursor.execute(command1)
    connection.commit()
def printTodatabase(exchange_pair, exchange_name, interval, time, open_price, high_price, low_price, close_price, volume_traded):
    trading_pair = exchange_pair
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")
    file_name = f"1-DataGathering/data_gathered/{trading_pair}_data/Live_Data/" + str(date) + exchange_name + exchange_pair + "interval=" + str(interval) + "kline_data.db"
    try:
        #Checks to see if there's an existing db file inside the data gathering dircetory
        if exists(file_name) == True:
            #Defining Connection and cursor
            connection = sqlite3.connect(file_name)
            cursor = connection.cursor()
            cursor.execute(f"""INSERT INTO pair_price VALUES ({time}, {open_price}, {high_price}, {low_price}, {close_price}, {volume_traded})""")
            connection.commit()
            connection.close() #Closing the databas
        
        else: #Creates new db file
            creating_db_file(exchange_pair, exchange_name, interval) #Creates new file

    except Exception as e: 
        # RECORDING ERROR
        path.append("00-Run_Log/Programs")
        from Log_Output import Record_Output
        Record_Output(exchange_pair, exchange_name, e, file_name)
        
        # HANDLING NO DATA TABLE ERROR
        path.append("ZZ-General_Functions/Programs")
        from Error_handling import Handling_Error
        Handling_Error(e).No_Data_Table_Error(1)
        if len(file_name) == 0:

            remove(file_name)

"""
2. CODE FOR GETTING ORDERBOOK DATA
"""
def on_message(ws, message, exchange_pair, exchange_name, interval):
    raw_data_string = message
    json_data_string = raw_data_string.replace("++Rcv raw:", "").strip()
    data_list = loads(json_data_string)
    
    ohlcv_list = data_list['k']
    time = data_list["E"] 
    open_price = float(ohlcv_list['o'])
    close_price = float(ohlcv_list['c'])
    high_price = float(ohlcv_list['h'])
    low_price = float(ohlcv_list['l'])
    volume_traded = float(ohlcv_list['v'])
    
    try: 
        printTodatabase(exchange_pair, exchange_name, interval, time, open_price, high_price, low_price, close_price, volume_traded)
    except Exception as e:
        pass



"""
3. CODE FOR CONNECTING TO WEBSOCKET 
"""
def on_error(ws, error):
    print(error)
def on_close(ws, close_status_code, close_msg):
    print("### closed ###")
def on_open(ws,interval):
    print(f"Opened connection: Live Data for Interval={interval}")

"""
4. RUNS THE PROGRAM
"""
def run(exchange_pair, exchange_name, interval):
    ws = websocket.WebSocketApp(f"wss://stream.binance.com:9443/ws/{exchange_pair.lower()}@kline_{interval}",
                              on_open=partial(on_open, interval=interval),
                              on_message=partial(on_message, exchange_pair=exchange_pair, exchange_name=exchange_name, interval=interval),
                              on_error=on_error,
                              on_close=on_close)

    ws.run_forever(dispatcher=rel)  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()

"""
5. CHECKS THE FILE LOG
"""
#Checking market data  database - WORKING
def check(exchange_pair, exchange_name, interval):
    trading_pair = exchange_pair
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")
    file_name = f"1-DataGathering/data_gathered/{trading_pair}_data/Live_Data/" + str(date) + exchange_name + exchange_pair + "interval="+ interval +"kline_data.db"
    print(file_name)
    #1-DataGathering\data_gathered\BTCUSDT_data\Live_Data\Apr072419BinanceBTCUSDTinterval=5mkline_data.db
    #1-DataGathering/data_gathered/BTC_data/Live_DataApr072419BinanceBTCUSDTinterval=5mkline_data.db
    connection = sqlite3.connect(file_name)
    cursor = connection.cursor()

    cursor.execute("Select * FROM pair_price")
    
    list_check = cursor.fetchall()

    for i in range(len(list_check)):
        print(list_check[i])
    
  
    connection.commit()
    #Closing the database
    connection.close()




#starts the program
#run("BTCUSDT","Binance", "5m")

#check("BTCUSDT", "Binance", "5m")