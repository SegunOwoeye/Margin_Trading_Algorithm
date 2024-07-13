from datetime import datetime
from os.path import exists
import sqlite3
from time import sleep
from sys import path

#CREATES A DATABASE FILE - WORKING
def creating_db_file(exchange_pair, exchange_names, chart_interval):
    trading_pair = exchange_pair
    
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")
    ###BELOW NEEDS TO BE EDITED
    file_name = f"2-DataProcessing/data_gathered/{trading_pair}_data/" + str(date) + exchange_names + exchange_pair + "interval=" + str(chart_interval) + "ATR_data.db"
    f = open(file_name, "x")
    
    #Defining Connection and cursor
    connection = sqlite3.connect(file_name)
    cursor = connection.cursor()

    #Creating Current exchange_tag price table]

    command1 = """CREATE TABLE IF NOT EXISTS
    processed_data(time TEXT, ATR FLOAT)"""
    
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
    if exists(file_name) == True:
        connection = sqlite3.connect(file_name)
        cursor = connection.cursor()

        cursor.execute("Select * FROM pair_price")
        
        list_check = cursor.fetchall()
        
        #COMES OUT as a LIST
        recent_log = list_check[-(indicator_interval):] #Most Recent data gathered from file
    
        connection.commit()
        #Closing the database
        connection.close()

        return recent_log
    else: # If the file doesn't exist, will wait 5 seconds before checking again to see if the file exists
        print("%s file does not exist" % file_name)
        sleep(5)
        get_historical_data(trading_pair, exchange_name, chart_interval, indicator_interval)


#GATHERS THE CURRENT DATA OF A CERTAIN NUMBER OF KLINES - WORKING
def get_current_data(trading_pair, exchange_name, chart_interval):
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")
    file_name = f"1-DataGathering/data_gathered/{trading_pair}_data/Live_Data/" + str(date) + exchange_name + trading_pair + "interval=" + str(chart_interval) + "kline_data.db"
    #print(file_name)
    if exists(file_name) == True:
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
    
    else: # If the file doesn't exist, will wait 5 seconds before checking again to see if the file exists
        print("%s file does not exist" % file_name)
        sleep(5)
        get_current_data(trading_pair, exchange_name, chart_interval)

#CALCULATES TRUE RANGE - WORKING
def true_range(trading_pair, exchange_name, chart_interval, indicator_interval):
    #Gathering DATA to calculate ATR
    historical_data = get_historical_data(trading_pair, exchange_name, chart_interval, indicator_interval)
    current_data = get_current_data(trading_pair, exchange_name, chart_interval)
    data_list = historical_data + current_data

    #Calculating the TR (True Range)
    tr_list = []
    for i in range(1,len(data_list)):
        pos1 = round(data_list[i][2] - data_list[i][3]) #  Current High minus low
        pos2 = abs(data_list[i][2] - data_list[i-1][4])# Abs value of current high minus previous low
        pos3 = abs(data_list[i][3] - data_list[i-1][4])# Abs value of current low minus previous low

        max_tr = max(pos1, pos2, pos3) #Determining the max value
        tr_list.append(max_tr)

    return tr_list
#CALCULATES THE FIRST ATR WHEN A PREVIOUS ONE ISN'T GIVEN - WORKING
def first_ATR(trading_pair, exchange_name, chart_interval, indicator_interval):
    
    tr_list = true_range(trading_pair, exchange_name, chart_interval, indicator_interval)
    
    #Calculating ATR when not given
    tr_sum = 0
    for i in range(len(tr_list)):
        tr_sum += tr_list[i]

    atr = (1/indicator_interval) * tr_sum

    #print(data_list)
    return (atr)

#CALCULATES the ATR based of the previous one - WORKING
def ATR(trading_pair, exchange_name, chart_interval, indicator_interval):
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")
    file_name = f"2-DataProcessing/data_gathered/{trading_pair}_data/" + str(date) + exchange_name + trading_pair + "interval=" + str(chart_interval) + "ATR_data.db"
    
    #Checks to see if there's an existing db file inside the data gathering dircetory
    if exists(file_name) == True: #Continue onto calculating ATR based on previous ATR
        #Gathering data fro database
        connection = sqlite3.connect(file_name)
        cursor = connection.cursor()
        cursor.execute("Select * FROM processed_data")
        list_check = cursor.fetchall()


        #Checks to see if the DB file is empty
        if len(list_check) == 0: #Does primary atr calculation
            primary_atr = first_ATR(trading_pair, exchange_name, chart_interval, indicator_interval) #Calculates first ATR
            current_time = (datetime.now())
            formatted_time = str(current_time.strftime('"%H:%M:%S.%f"'))
            cursor.execute(f"""INSERT INTO processed_data VALUES ({formatted_time}, {primary_atr})""")
            connection.commit()
            connection.close() #Closing the database
            
        else: #Does Regular atr calculation since there's a previous atr

            #COMES OUT as a LIST
            recent_log = list_check[-1] #Most Recent data gathered from file
            connection.commit()
            #Closing the database
            connection.close()
        
            recent_ATR = recent_log[1]
            TR = true_range(trading_pair, exchange_name, chart_interval, indicator_interval)[indicator_interval-1]
            new_atr = (recent_ATR*(indicator_interval-1) + TR)/indicator_interval
            
            #Defining Connection and cursor
            connection = sqlite3.connect(file_name)
            cursor = connection.cursor()

            current_time = (datetime.now())
            formatted_time = str(current_time.strftime('"%H:%M:%S.%f"'))
            cursor.execute(f"""INSERT INTO processed_data VALUES ({formatted_time}, {new_atr})""")
            connection.commit()
            connection.close() #Closing the database



    else: #Creates new ATR Database
        creating_db_file(trading_pair, exchange_name, chart_interval) #Creates new Database file
        ATR(trading_pair, exchange_name, chart_interval, indicator_interval)

def run(trading_pair, exchange_name, chart_interval, indicator_interval):
    
    while 1:
        try:
            
            """ CHECKS TO SEE IF THE REQUIRED FILES ARE PRESENT, IF NOT IT WAITS"""
            # Gets required filenames
            date_and_time = (datetime.now())
            live_date = date_and_time.strftime("%b%d%y%H")
            historical_date = date_and_time.strftime("%b%d%y")

            live_data_file = f"1-DataGathering/data_gathered/{trading_pair}_data/Live_Data/" + str(live_date) + exchange_name + trading_pair + "interval=" + str(chart_interval) + "kline_data.db"
            historical_data_file = f"1-DataGathering/data_gathered/{trading_pair}_data/Historical_Klines/" + str(historical_date) + exchange_name + trading_pair + "interval=" + str(chart_interval) + "kline_data.db"
            #Checks to see if required files exists
            if exists(live_data_file) == True and exists(historical_data_file) == True:
                # Runs programs
                ATR(trading_pair, exchange_name, chart_interval, indicator_interval)
                if chart_interval == "1d":
                    sleep_interval = 60*60*24
                    sleep(1+sleep_interval)
                else:
                    if "h" in chart_interval:
                        sleep_interval = chart_interval.replace("h","")
                        sleep(1+60*60*float(sleep_interval))
                    elif "m" in chart_interval:
                        sleep_interval = chart_interval.replace("m","")
                        sleep(1+60*float(sleep_interval))

            # Waits 1 seconds if the required filenames don't exist
            else:
                sleep(1)

        except Exception as e:
            print(f"2-DataProcessing/Programs/{trading_pair}/Average_True_Range_{trading_pair}interval={chart_interval}.py has error: " + str(e))
            
            path.append("ZZ-General_Functions/Programs")
            from Error_handling import Handling_Error
            Handling_Error(e).No_Data_Table_Error()


#(run("BTCUSDT", "Binance", "5m", 14))


