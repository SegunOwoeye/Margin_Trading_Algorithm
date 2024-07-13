from datetime import datetime
from os.path import exists
from sys import path
import sqlite3
import time
from statistics import median

#CREATES A DATABASE FILE - WORKING
def creating_db_file(trading_pair, exchange_name, chart_interval):    
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")
    ###BELOW NEEDS TO BE EDITED
    file_name = f"2-DataProcessing/data_gathered/{trading_pair}_data/" + str(date) + exchange_name + trading_pair + "interval=" + str(chart_interval) + "WF_data.db"
    f = open(file_name, "x")
    
    #Defining Connection and cursor
    connection = sqlite3.connect(file_name)
    cursor = connection.cursor()

    #Creating Current exchange_tag price table]
    #Fractal type can either be Bullish or Bearish
    command1 = """CREATE TABLE IF NOT EXISTS
    processed_data(time TEXT, Fractal_Type FLOAT)"""
    
    #IF TRADE STATUS IS OPEN, THE PURCHASE HASN'T GONE THROUGH
    #IF TRADE STATUS IS CLOSED, THE PURCHASE HAS GONE THROUGH

    cursor.execute(command1)
    connection.commit()

    #Closing the database
    connection.close()
#Checks to see if inputted number is a prime number
def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True
#Gets the next prime number
def next_prime(n):
    while True:
        n += 1
        if is_prime(n):
            return n

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
    
    #COMES OUT as a LIST
    data_range = next_prime(indicator_interval) + 2
    recent_log = list_check[-(data_range-1):] #Most Recent data gathered from file
  
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
#Determines whether a Williams fractal has occurred within a specific  - WORKING
def Willian_Fractal(trading_pair, exchange_name, chart_interval, indicator_interval):
    historical_data = get_historical_data(trading_pair, exchange_name, chart_interval, indicator_interval)
    current_data = get_current_data(trading_pair, exchange_name, chart_interval)

    data_set = historical_data + current_data
    #print(data_set)
    list_length = len(data_set)
    #Setting up calculation to find the middle most number from the ranger
    range_1 = range(0,list_length)
    placement_list = list(range_1)

    N = median(placement_list)

    #Bearish Fractals = -1
    bearish_middle_set = data_set[N][2]
    usable_dataset = data_set
    usable_dataset.pop(N) # Removes middle set from set being compared
    bearish_high_data = []
    for i in range(len(usable_dataset)):
        bearish_high_data.append(usable_dataset[i][2])

    #Bullish Fractals = 1
    bullish_middle_set = data_set[N][3]
    Bullish_low_data = []
    for i in range(len(usable_dataset)):
        Bullish_low_data.append(usable_dataset[i][3])
    
    #Final Analysis
    if bullish_middle_set < min(Bullish_low_data): #Bullish Conditions
        return 1 #1 is Bullish
    
    elif bearish_middle_set > max(bearish_high_data): #Bearish Conditions
        return -1 #-1 is Bearish

    else:
        return None
        

#PRINT WF DATA TO DATABASE - WORKING
def printTodatabase(trading_pair, exchange_name, chart_interval, indicator_interval):
    WF = Willian_Fractal(trading_pair, exchange_name, chart_interval, indicator_interval)
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")
    ###BELOW NEEDS TO BE EDITED
    file_name = f"2-DataProcessing/data_gathered/{trading_pair}_data/" + str(date) + exchange_name + trading_pair + "interval=" + str(chart_interval) + "WF_data.db"
    try:
        #Checks to see if there's an existing db file inside the data gathering dircetory
        if exists(file_name) == True:
            # Using chart interval time to set a sleep interval for calculating WF
            c_time = time.localtime()
            hour_past = c_time.tm_hour
            minutes_past = c_time.tm_min
            seconds_past = c_time.tm_sec

            sleep_timer = chart_interval.lower()
            if "m" in sleep_timer: 
                sleep_interval = int(sleep_timer.replace("m", ""))
                wait_time = (sleep_interval - minutes_past % sleep_interval) * 60 - seconds_past
            elif "h" in sleep_timer: 
                sleep_interval = int(sleep_timer.replace("h", ""))
                wait_time = (sleep_interval*60 - minutes_past % sleep_interval*60) * 60 - seconds_past
            elif "d" in sleep_timer: 
                sleep_interval = int(sleep_timer.replace("d", ""))
                wait_time = (24 - hour_past) * 3600 + (60 - minutes_past) * 60 - seconds_past
            else:
                pass

            #Checks to see if program returns anything
            if WF == None: #If Empty skips the rest of the program
                #Defining Connection and cursor
                connection = sqlite3.connect(file_name)
                cursor = connection.cursor()

                current_time = (datetime.now())
                formatted_time = str(current_time.strftime('"%H:%M:%S.%f"'))
                cursor.execute(f"""INSERT INTO processed_data (time, Fractal_Type) VALUES ({formatted_time}, 0)""")

                connection.commit()
                connection.close() #Closing the database

                time.sleep(wait_time) #RUNS THE PROGRAM EVERY INTERVAL PERIOD
            else: #Prints if the williams fractal has occurred to the database

                #Defining Connection and cursor
                connection = sqlite3.connect(file_name)
                cursor = connection.cursor()

                current_time = (datetime.now())
                formatted_time = str(current_time.strftime('"%H:%M:%S.%f"'))
                cursor.execute(f"""INSERT INTO processed_data (time, Fractal_Type) VALUES ({formatted_time}, {(WF)})""")

                connection.commit()
                connection.close() #Closing the database

                time.sleep(wait_time) #RUNS THE PROGRAM EVERY INTERVAL PERIOD
        
        else: #Creates new db file
            creating_db_file(trading_pair, exchange_name, chart_interval) #Creates new file

    except Exception as e: #Message email that an error on... has occured
        print(f"2-DataProcessing/Programs/{trading_pair}/Williams_Fractals_{trading_pair}interval={str(chart_interval)}tick={indicator_interval}.py has error: " + str(e))


def run(trading_pair, exchange_name, chart_interval, indicator_interval):
    while 1:
        try: 
            """ CHECKS TO SEE IF THE REQUIRED FILES ARE PRESENT, IF NOT IT WAITS"""
            # [1] Gets required filenames
            date_and_time = (datetime.now())
            live_date = date_and_time.strftime("%b%d%y%H")
            historical_date = date_and_time.strftime("%b%d%y")
            live_data_file = f"1-DataGathering/data_gathered/{trading_pair}_data/Live_Data/" + str(live_date) + exchange_name + trading_pair + "interval=" + str(chart_interval) + "kline_data.db"
            historical_data_file = f"1-DataGathering/data_gathered/{trading_pair}_data/Historical_Klines/" + str(historical_date) + exchange_name + trading_pair + "interval=" + str(chart_interval) + "kline_data.db"
            
            
            # [2] Checks to see if required files exists
            if exists(live_data_file) == True and exists(historical_data_file) == True:
                printTodatabase(trading_pair, exchange_name, chart_interval, indicator_interval)
                time.sleep(1)
            
            # [3] Waits 1 seconds if the required filenames don't exist
            else:
                time.sleep(1)
                #print("No Files yet")



        except Exception as e:
            print(f"2-DataProcessing/Programs/{trading_pair}/Relative_Strength_Indicator_{trading_pair}interval={str(chart_interval)}tick={indicator_interval}.py has error: " + str(e))

            path.append("ZZ-General_Functions/Programs")
            from Error_handling import Handling_Error
            Handling_Error(e).No_Data_Table_Error()



#(run("BTCUSDT", "ByBit", 1, 2))


