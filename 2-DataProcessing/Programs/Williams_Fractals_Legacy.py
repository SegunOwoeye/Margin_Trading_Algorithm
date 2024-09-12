from datetime import datetime
from os.path import exists
from sys import path
import sqlite3
import time

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
  
    connection.commit()
    #Closing the database
    connection.close()

    return list_check
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
    """ [1] Importing and Initialising Variables"""
    # [1.0] Importing variables from previous functions
    window = indicator_interval 
    historical_data = get_historical_data(trading_pair, exchange_name, chart_interval, indicator_interval)
    current_data = get_current_data(trading_pair, exchange_name, chart_interval)

    # [1.1] Initialising Variables
    data_set = historical_data + current_data
    lookback_window = window * 2 + 1
    lookback_dataset = data_set[-lookback_window:]

    # [1.2] Getting List of High Prices
    high_list = []
    for i in range(len(lookback_dataset)):
        high_list.append(lookback_dataset[i][2])
    
    # [1.3] Getting List of Low Prices
    low_list = []
    for i in range(len(lookback_dataset)):
        low_list.append(lookback_dataset[i][3])

    
    """ [2] Calculating WF """
    fractal_data = []
    for i in range(len(high_list)):
        if i < window or i > len(high_list) - window:
            fractal_data.append(0)

        else:
            #Bearish fractal = -1
            if all(high_list[i] > high_list[i+j] for j in range(-window, window) if j != 0):
                fractal_data.append(-1)
            
            #Bullish fractal = 1
            elif all(low_list[i] < low_list[i+j] for j in range(-window, window) if j != 0):
                fractal_data.append(1)

            else: #No fractal = 0
                fractal_data.append(0)

    fractal_data = [0] * window + fractal_data[:-window]
    current_fractal = fractal_data[-1]
    
    # 3 Returing the value of the function
    if current_fractal == 0:
        return None
    else:
        return current_fractal
    

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
        program_name = f"2-DataProcessing/Programs/{trading_pair}/Relative_Strength_Indicator_{trading_pair}interval={str(chart_interval)}tick={indicator_interval}.py"
        # RECORDING ERROR
        path.append("00-Run_Log/Programs")
        from Log_Output import Record_Output
        Record_Output(trading_pair, exchange_name, e, program_name)

        # HANDLING NO DATA TABLE ERROR 
        path.append("ZZ-General_Functions/Programs")
        from Error_handling import Handling_Error
        Handling_Error(e).No_Data_Table_Error()


def run(trading_pair, exchange_name, chart_interval, indicator_interval):
    while 1:
        try: 
            # Checks to see if program should be suspended before running due to overlap error
            path.append("ZZ-General_Functions/Programs")
            from Suspend_programs import Suspend_programs
            Suspend_programs(interval=chart_interval)
            
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
            program_name = f"2-DataProcessing/Programs/{trading_pair}/Relative_Strength_Indicator_{trading_pair}interval={str(chart_interval)}tick={indicator_interval}.py"
            # RECORDING ERROR
            path.append("00-Run_Log/Programs")
            from Log_Output import Record_Output
            Record_Output(trading_pair, exchange_name, e, program_name)
            
            # HANDLING NO DATA TABLE ERROR 
            path.append("ZZ-General_Functions/Programs")
            from Error_handling import Handling_Error
            Handling_Error(e).No_Data_Table_Error()



#(run("BTCUSDT", "Binance", "5m", 3))


