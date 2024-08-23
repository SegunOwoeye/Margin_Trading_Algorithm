from datetime import datetime
from os.path import exists
from sys import path
import sqlite3
import time

"""[1] PERFORMS DATA GATHERING TASKS"""
#CREATES A DATABASE FILE - WORKING
def creating_db_file(trading_pair, exchange_name, chart_interval, indicator_interval, db_name):    
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y")
    ###BELOW NEEDS TO BE EDITED
    file_name = f"2-DataProcessing/data_gathered/{trading_pair}_data/{str(date)}{exchange_name}{trading_pair}interval={str(chart_interval)}tick={indicator_interval}{str(db_name)}data.db"
    f = open(file_name, "x")
    
    #Defining Connection and cursor
    connection = sqlite3.connect(file_name)
    cursor = connection.cursor()

    #Creating Current exchange_tag price table]
    command1 = f"""CREATE TABLE IF NOT EXISTS
    processed_data(time TEXT, {db_name} FLOAT)"""
    cursor.execute(command1)
    cursor.execute(f"""INSERT INTO processed_data (time, {db_name}) VALUES (1, 1)""")
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


"""[2] PERFORMS DATA PROCESSING TASKS"""
#CALCULATES THE EMA - WORKING
def EMA(trading_pair, exchange_name, chart_interval, indicator_interval, db_name="EMA"):
    K = 2/(indicator_interval+1) #WEIGHTED MULTIPLIER FOR EMA
    #Gathering Kline data
    current_data = get_current_data(trading_pair, exchange_name, chart_interval)
    
    #Getting the recent closing price
    recent_closing_price = current_data[-1][4]
    
    #Getting the correct time and date
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y")
    ###BELOW NEEDS TO BE EDITED
    file_name = f"2-DataProcessing/data_gathered/{trading_pair}_data/{str(date)}{exchange_name}{trading_pair}interval={str(chart_interval)}tick={indicator_interval}{str(db_name)}data.db"
    
    #Checks to see if there's an existing db file inside the data gathering dircetory
    
    #Gathering data from database
    connection = sqlite3.connect(file_name)
    cursor = connection.cursor()

    cursor.execute("Select * FROM processed_data")
    list_check = cursor.fetchall()
    #CALCULATING THE EMA
    if len(list_check) == 1: #Checks to see if the file has any data
        from sys import path
        path.append("2-DataProcessing/Programs")
        from SMA_to_EMA_prep import backed_EMA

        #Calculate EMA 
        first_EMA = backed_EMA(trading_pair, chart_interval, indicator_interval, 1000)[-1]  
        return first_EMA
                    
    else: #MEANS THE FILE HAS DATA
        #Calculates the EMA from previous EMA
        #COMES OUT as a LIST
        recent_EMA = list_check[-1] #Most Recent data gathered from file
        recent_EMA = recent_EMA[1]
        connection.commit()
        #Closing the database
        connection.close()
        #EMA = Closing price x multiplier + EMA (previous day) x (1-multiplier)
        actual_EMA = recent_closing_price * K + recent_EMA * (1-K)
            
            
        return actual_EMA

    

"""[3 PRINT THE DATA TO THE EMA DATABASE]"""    
#PRINT EMA DATA TO DATABASE - 
def printTodatabase(trading_pair, exchange_name, chart_interval, indicator_interval, db_name="EMA"):
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y")
    ###BELOW NEEDS TO BE EDITED
    file_name = f"2-DataProcessing/data_gathered/{trading_pair}_data/{str(date)}{exchange_name}{trading_pair}interval={str(chart_interval)}tick={indicator_interval}{str(db_name)}data.db"
    try:
        #Checks to see if there's an existing db file inside the data gathering dircetory
        if exists(file_name) == True:
            # Using chart interval time to set a sleep interval for calculating ema
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
            exponential_moving_average = EMA(trading_pair, exchange_name, chart_interval, indicator_interval, db_name)
            connection = sqlite3.connect(file_name)
            cursor = connection.cursor()

            current_time = (datetime.now())
            formatted_time = str(current_time.strftime('"%H:%M:%S"'))
            cursor.execute(f"""INSERT INTO processed_data (time, {db_name}) VALUES ({formatted_time}, {(exponential_moving_average)})""")

            connection.commit()
            connection.close() #Closing the database
            

            time.sleep(wait_time) #RUNS THE PROGRAM EVERY INTERVAL PERIOD
        
        else: #Creates new db file
            creating_db_file(trading_pair, exchange_name, chart_interval, indicator_interval, db_name) #Creates new file

    except Exception as e: #Message email that an error on... has occured
        program_name = f"2-DataProcessing/Programs/{trading_pair}/EMA_{trading_pair}interval={chart_interval}tick={indicator_interval}.py"
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

            
            # [3] Waits 1 seconds if the required filenames don't exist
            else:
                time.sleep(5)
                #print("No Files yet")

        except Exception as e:
            program_name = f"2-DataProcessing/Programs/{trading_pair}/EMA_{trading_pair}interval={chart_interval}tick={indicator_interval}.py"
            # RECORDING ERROR
            path.append("00-Run_Log/Programs")
            from Log_Output import Record_Output
            Record_Output(trading_pair, exchange_name, e, program_name)
            
            # HANDLING NO DATA TABLE ERROR
            path.append("ZZ-General_Functions/Programs")
            from Error_handling import Handling_Error
            Handling_Error(e).No_Data_Table_Error()



#(run("BTCUSDT", "Binance", "5m", 100))



