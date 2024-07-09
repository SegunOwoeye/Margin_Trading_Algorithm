from datetime import datetime
from os.path import exists
import sqlite3
from time import sleep
from statistics import median

#CREATES A DATABASE FILE - WORKING
def creating_db_file(trading_pair, exchange_name, chart_interval):    
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")
    ###BELOW NEEDS TO BE EDITED
    file_name = f"2-DataProcessing/data_gathered/{trading_pair}_data/" + str(date) + exchange_name + trading_pair + "interval=" + str(chart_interval) + "MFI_data.db"
    f = open(file_name, "x")
    
    #Defining Connection and cursor
    connection = sqlite3.connect(file_name)
    cursor = connection.cursor()

    #Creating Current exchange_tag price table]
    #Fractal type can either be Bullish or Bearish
    command1 = """CREATE TABLE IF NOT EXISTS
    processed_data(time TEXT, MFI FLOAT)"""
    
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
#CALCULATES THE MFI  - WORKING
def Money_Flow_Index(trading_pair, exchange_name, chart_interval, indicator_interval):
    historical_data = get_historical_data(trading_pair, exchange_name, chart_interval, indicator_interval)
    current_data = get_current_data(trading_pair, exchange_name, chart_interval)

    data_set = historical_data + current_data

    #Calculates the typical price for the past x periods
    typical_price_list = []
    for i in range(len(data_set)):
        typical_price = (data_set[i][2] + data_set[i][3] + data_set[i][4])/3
        typical_price_list.append([typical_price, data_set[i][5]]) #Returns a list of typical_prices with the period volume 

    #Determining whether the typical price was higher or lower than the one of the prior period
    positive_MF_list = []
    negative_MF_list = []
    for i in range(1,len(typical_price_list)):
        if typical_price_list[i][0] > typical_price_list[i-1][0]:
            positive_MF_list.append(typical_price_list[i])
        elif typical_price_list[i][0] < typical_price_list[i-1][0]:
            negative_MF_list.append(typical_price_list[i])
        else:
            pass
    
    #Getting raw money flow
    positive_RMF_list = []
    for i in range(len(positive_MF_list)):
        MF = positive_MF_list[i][0] * positive_MF_list[i][1]
        positive_RMF_list.append(MF)
    
    negative_RMF_list = []
    for i in range(len(negative_MF_list)):
        MF = negative_MF_list[i][0] * negative_MF_list[i][1]
        negative_RMF_list.append(MF)

    #Calculating the positive and negative raw money flow
    positive_MF = 0
    for i in range(len(positive_RMF_list)):
        positive_MF += positive_RMF_list[i]
    
    negative_MF = 0
    for i in range(len(negative_RMF_list)):
        negative_MF += negative_RMF_list[i]

    MF_ratio = positive_MF/negative_MF

    MFI = 100 - (100/(1+MF_ratio))

    return MFI

        

#PRINT WF DATA TO DATABASE - WORKING
def printTodatabase(trading_pair, exchange_name, chart_interval, indicator_interval):
    MFI = Money_Flow_Index(trading_pair, exchange_name, chart_interval, indicator_interval)
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")
    ###BELOW NEEDS TO BE EDITED
    file_name = f"2-DataProcessing/data_gathered/{trading_pair}_data/" + str(date) + exchange_name + trading_pair + "interval=" + str(chart_interval) + "MFI_data.db"
    try:
        #Checks to see if there's an existing db file inside the data gathering dircetory
        if exists(file_name) == True:
            #Checks to see if program returns anything
            
            connection = sqlite3.connect(file_name)
            cursor = connection.cursor()

            current_time = (datetime.now())
            formatted_time = str(current_time.strftime('"%H:%M:%S.%f"'))
            cursor.execute(f"""INSERT INTO processed_data (time, MFI) VALUES ({formatted_time}, {(MFI)})""")

            connection.commit()
            connection.close() #Closing the database
        
        else: #Creates new db file
            creating_db_file(trading_pair, exchange_name, chart_interval) #Creates new file

    except Exception as e: #Message email that an error on... has occured
        print(f"2-DataProcessing/Programs/{trading_pair}/Money_Flow_Index_{trading_pair}interval={chart_interval}.py has error: " + str(e))


def run(trading_pair, exchange_name, chart_interval, indicator_interval):
    sleep(3)
    while 1:
        
        try: 
            printTodatabase(trading_pair, exchange_name, chart_interval, indicator_interval)
            sleep(1)
        except Exception as e:
            print(f"2-DataProcessing/Programs/{trading_pair}/Money_Flow_Index_{trading_pair}interval={chart_interval}.py has error: " + str(e))





#(run("BTCUSDT", "ByBit", 1, 14))


