#!/usr/bin/python3.8.5

from datetime import datetime
from os import path
from time import sleep


"""
1. CODE FOR CREATING DATABASE AND WRITING ORDERBOOK DATA TO DATABASE
"""


#Generic Code - WORKING
def creating_db_file(exchange_pair, exchange_name):
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")

    #FOR TEXT FILE 
    file_name = f"00-Run_Log/data_gathered/" + str(date) + exchange_name + exchange_pair + "LOG.txt"
    f = open(file_name, "w")


def Record_Output(exchange_pair, exchange_name, Message: str, program_name: str = "", wait_time: int = 1):
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")
    record_time = date_and_time.strftime("%H:%M:%S")
    file_name = f"00-Run_Log/data_gathered/" + str(date) + exchange_name + exchange_pair + "LOG.txt"
    try:
        #Checks to see if there's an existing db file inside the data gathering dircetory
        if path.exists(file_name) == True:
            
            #Text file database
            f = open(file_name, "a")
            f.write(f"{record_time} | {program_name}: {(Message)} \n")
            sleep(wait_time)

        else: #Creates new db file
            creating_db_file(exchange_pair, exchange_name) #Creates new file

    except Exception as e: #Message email that an error on... has occured
        print(f"Error occured at 00-Run_Log/Programs/Log_Output.py: " + str(e))
        



#starts the program
#Record_Output("BTCUSDT","Binance", 5)
