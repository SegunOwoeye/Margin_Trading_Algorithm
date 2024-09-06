#!/usr/bin/python3.6.5

import websocket
import rel

from datetime import datetime
from os.path import exists
from sys import path
import sqlite3
from time import time, sleep
from json import loads, dumps
from functools import partial


"""
1. CODE FOR CREATING DATABASE AND WRITING ORDERBOOK DATA TO DATABASE
"""

#exchange_pair = "BTCUSDT"

#Generic Code - WORKING
def creating_db_file(exchange_pair, exchange_name):
    trading_pair = exchange_pair
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")

    #FOR TEXT FILE
    file_name = f"1-DataGathering/data_gathered/{trading_pair}_data/Live_Data/" + str(date) + exchange_name + exchange_pair + "orderbook.txt"
    f = open(file_name, "w")


def printTodatabase(exchange_pair, exchange_name, depth):
    trading_pair = exchange_pair
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")
    #file_name = f"1-DataGathering/data_gathered/{trading_pair}_data/Live_Data/" + str(date) + exchange_name + exchange_pair + "interval=" + str(interval) + "depth_data.db"
    file_name = f"1-DataGathering/data_gathered/{trading_pair}_data/Live_Data/" + str(date) + exchange_name + exchange_pair + "orderbook.txt"
    program_name = f"1-DataGathering/Programs/{trading_pair}/Live_Data/Data_Gathering_{exchange_name}_{trading_pair}_Orderbook.py"
    try:
        #Checks to see if there's an existing db file inside the data gathering dircetory
        if exists(file_name) == True:
            #Defining Connection and cursor
            '''connection = sqlite3.connect(file_name)
            cursor = connection.cursor()
            cursor.execute(f"""INSERT INTO pair_price VALUES ({time}, {open_price}, {high_price}, {low_price}, {close_price}, {volume_traded})""")
            connection.commit()
            connection.close() #Closing the database'''
            
            #Text file database
            f = open(file_name, "a")
            f.write(depth + "\n")
        else: #Creates new db file
            creating_db_file(exchange_pair, exchange_name) #Creates new file

    except Exception as e: 
        # RECORDING ERROR
        path.append("00-Run_Log/Programs")
        from Log_Output import Record_Output
        Record_Output(exchange_pair, exchange_name, e, program_name)

"""
2. CODE FOR GETTING ORDERBOOK DATA
"""
def on_message(ws, message, exchange_pair, exchange_name):
    raw_data_string = message
    json_data_string = raw_data_string.replace("++Rcv raw:", "").strip()
    data_list = dumps(loads(json_data_string))
    
    #print(data_list)
    
    try: 
        printTodatabase(exchange_pair, exchange_name, data_list)
    except Exception as e:
        pass



"""
3. CODE FOR CONNECTING TO WEBSOCKET 
"""
def on_error(ws, error):
    print(error)
def on_close(ws, close_status_code, close_msg):
    print("### closed ###")
def on_open(ws, exchange_pair):
    print(f"Opened connection: {exchange_pair}, Orderbook")

"""
4. RUNS THE PROGRAM
"""
def run(exchange_pair, exchange_name, levels):
    while 1: # Run forever
        try:
            ws = websocket.WebSocketApp(f"wss://stream.binance.com:9443/ws/{exchange_pair.lower()}@depth{levels}",
                                    on_open=partial(on_open, exchange_pair=exchange_pair),
                                    on_message=partial(on_message, exchange_pair=exchange_pair, exchange_name=exchange_name),
                                    on_error=on_error,
                                    on_close=on_close)

            ws.run_forever(dispatcher=rel)  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
            rel.signal(2, rel.abort)  # Keyboard Interrupt
            rel.dispatch()
        except Exception as e:
            program_name = f"1-DataGathering/Programs/{exchange_pair}/Live_Data/Data_Gathering_{exchange_name}_{exchange_pair}_Orderbook.py"
            # RECORDING ERROR
            path.append("00-Run_Log/Programs")
            from Log_Output import Record_Output
            Record_Output(exchange_pair, exchange_name, e, program_name)



#starts the program
#run("BTCUSDT","Binance", 5)
