from datetime import datetime
from os.path import exists
import sqlite3
from time import sleep
from statistics import median

#CREATES A DATABASE FILE - WORKING
def creating_db_file(trading_pair, exchange_name, chart_interval, db_name):    
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")
    ###BELOW NEEDS TO BE EDITED
    file_name = f"2-DataProcessing/data_gathered/{trading_pair}_data/" + str(date) + exchange_name + trading_pair + "interval=" + str(chart_interval) + str(db_name) + "_data.db"
    f = open(file_name, "x")
    
    #Defining Connection and cursor
    connection = sqlite3.connect(file_name)
    cursor = connection.cursor()

    #Creating Current exchange_tag price table]
    #Fractal type can either be Bullish or Bearish
    command1 = f"""CREATE TABLE IF NOT EXISTS
    processed_data(time TEXT, High FLOAT, Low FLOAT)"""
    
    #IF TRADE STATUS IS OPEN, THE PURCHASE HASN'T GONE THROUGH
    #IF TRADE STATUS IS CLOSED, THE PURCHASE HAS GONE THROUGH

    cursor.execute(command1)
    connection.commit()

    #Closing the database
    connection.close()

#GATHERS THE HISTORICAL DATA OF A CERTAIN NUMBER OF KLINES - WORKING
def get_historical_data(trading_pair, exchange_name, chart_interval, indicator_interval):
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y")
    file_name = f"1-DataGathering/data_gathered/{trading_pair}_data/Historical_Klines/" + str(date) + exchange_name + trading_pair + "interval=" + str(chart_interval) + "kline_data.db"
    #print(file_name)
    connection = sqlite3.connect(file_name)
    cursor = connection.cursor()

    cursor.execute("Select * FROM pair_price")
    
    list_check = cursor.fetchall()
    recent_log = list_check[-(indicator_interval-1):] #Most Recent data gathered from file
  
    connection.commit()
    #Closing the database
    connection.close()

    return recent_log
#GATHERS THE CURRENT DATA OF A CERTAIN NUMBER OF KLINES - WORKING
def get_current_data(trading_pair, exchange_name, chart_interval):
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")
    file_name = f"1-DataGathering/data_gathered/{trading_pair}_data/Live_Data/" + str(date) + exchange_name + trading_pair + "interval=" + str(chart_interval) + "kline_data.db"
    #print(file_name)
    connection = sqlite3.connect(file_name)
    cursor = connection.cursor()

    cursor.execute("Select * FROM pair_price")
    
    list_check = cursor.fetchall()
    
    #COMES OUT as a LIST
    recent_log = list_check[-1] #Most Recent data gathered from file
  
    connection.commit()
    #Closing the database
    connection.close()

    return [recent_log]
#CALCULATES THE SWING HIGH AND LOW OF AN INTERVAL  - WORKING
def swings(trading_pair, exchange_name, chart_interval, indicator_interval):
    historical_data = get_historical_data(trading_pair, exchange_name, chart_interval, indicator_interval)
    current_data = get_current_data(trading_pair, exchange_name, chart_interval)

    data_set = historical_data + current_data

    #Gathering Highs prices
    high_prices_list = []
    for i in range(len(data_set)):
        high_price = data_set[i][2]
        high_prices_list.append(high_price)
    
    #Gathering Lows prices
    low_prices_list = []
    for i in range(len(data_set)):
        low_price = data_set[i][3]
        low_prices_list.append(low_price)
    
    #Finding the swing highs
    highs_list = []
    for i in range(len(high_prices_list)-2):
        if high_prices_list[i] > high_prices_list[i+1] and high_prices_list[i+1] > high_prices_list[i+2]:
            highs_list.append(high_prices_list[i])
        else:
            pass
    
    swing_high = max(highs_list)

    #Finding the swing lows
    lows_list = []
    for i in range(len(low_prices_list)-2):
        if low_prices_list[i] < low_prices_list[i+1] and low_prices_list[i+1] < low_prices_list[i+2]:
            lows_list.append(low_prices_list[i])
        else:
            pass
    
    swing_low = min(lows_list)
    
    #RETURNS THE SWING HIGH AND SWING LOW
    return swing_high, swing_low


#PRINT SMA DATA TO DATABASE - WORKING
def printTodatabase(trading_pair, exchange_name, chart_interval, indicator_interval, db_name):
    swing_pairs = swings(trading_pair, exchange_name, chart_interval, indicator_interval)
    swing_high = swing_pairs[0]
    swing_low = swing_pairs[1]

    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")
    ###BELOW NEEDS TO BE EDITED
    file_name = f"2-DataProcessing/data_gathered/{trading_pair}_data/" + str(date) + exchange_name + trading_pair + "interval=" + str(chart_interval) + str(db_name) + "_data.db"
    try:
        #Checks to see if there's an existing db file inside the data gathering dircetory
        if exists(file_name) == True:
            #Checks to see if program returns anything
            
            connection = sqlite3.connect(file_name)
            cursor = connection.cursor()

            current_time = (datetime.now())
            formatted_time = str(current_time.strftime('"%H:%M:%S.%f"'))
            cursor.execute(f"""INSERT INTO processed_data (time, High, Low) VALUES ({formatted_time}, {(swing_high)}, {swing_low})""")

            connection.commit()
            connection.close() #Closing the database
        
        else: #Creates new db file
            creating_db_file(trading_pair, exchange_name, chart_interval, db_name) #Creates new file

    except Exception as e: #Message email that an error on... has occured
        print(f"2-DataProcessing/Programs/{trading_pair}/{db_name}_{trading_pair}interval={chart_interval}.py has error: " + str(e))


def run(trading_pair, exchange_name, chart_interval, indicator_interval, db_name):
    sleep(3)
    while 1:
        try: 
            printTodatabase(trading_pair, exchange_name, chart_interval, indicator_interval, db_name)
            sleep(1)
        except Exception as e:
            print(f"2-DataProcessing/Programs/{trading_pair}/{db_name}_{trading_pair}interval={chart_interval}.py has error: " + str(e))


#print(run("BTCUSDT", "ByBit", 1, 14, "Swings"))




