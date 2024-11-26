import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import os 
import subprocess
from time import sleep 
import sqlite3



#[1] Setting Up application

#-> Declaring the pairs to be traded
#"""THESE WILL BE CHANGED TO COMING FROM A SETTING SILE LATER ON"""
pair_list = ["BTCUSDT"]#, "ETHUSDT"]
#-> Declaring time intervals
#time_intervals = ["1", "5", "15", "60"]
time_intervals = ["5m"]

exchange = "Binance"

from sys import path

#"""TRADING PAIR LIST"""
#pair_list = ["BTCUSDT", "ETHUSDT"]

path.append("0-Run")
from Setup import start_1, start_2, start_3

#Creates folders for data storage
start_1(pair_list)
start_2(pair_list)
start_3(pair_list)

#TRADING ENVIRONMENT (flag)
#     [0] LIVE TRADING
#     [1] DEMO TRADING
flag = 1

#CREATING ACCOUNT BALANCES
if flag == 1: #Creats Demo Balances
    path.append("3-AccountBalance/Programs")
    import Paper_Trading_Account_create
else: #Uses Real Balances
    pass

def run_demo_trading_account():
    #Splitting up trading pairs into their individual Crypto Currencies
    individual_pair_list = []
    for i in range(len(pair_list)):
        individual_pair = pair_list[i].replace("USDT","")
        individual_pair_list.append(individual_pair)

    individual_pair_list.append('USDT')

    for n in range(len(individual_pair_list)):
        if individual_pair_list[n] == "USDT":
            Paper_Trading_Account_create.run(individual_pair_list[n], exchange, "Demo_Balance", 10000.00)

        else:
            Paper_Trading_Account_create.run(individual_pair_list[n], exchange, "Demo_Balance", 5.00)
   




######################################################################################################
#[2] DATA GATHERING

#Historical Data
def gathering_data_file_list1():
    # Running historical klines programs
    run_historical_klines = []
    for n in range(len(pair_list)):
        for i in range(len(time_intervals)):
            program_name = f"1-DataGathering/Programs/{pair_list[n]}/Historical_Klines/Data_Gathering_{exchange}_Historical_{pair_list[n]}_interval={time_intervals[i]}.py"
            run_historical_klines.append(program_name)

    gathering_data_programs_list = run_historical_klines
    return gathering_data_programs_list
#Live Data
def gathering_data_file_list2():
    # Running live klines programs
    run_live_klines = []
    for n in range(len(pair_list)):
        for i in range(len(time_intervals)):
            program_name = f"1-DataGathering/Programs/{pair_list[n]}/Live_Data/Data_Gathering_{exchange}_Live_{pair_list[n]}_interval={time_intervals[i]}.py"
            run_live_klines.append(program_name)

    gathering_data_programs_list = run_live_klines
    return gathering_data_programs_list








#######################################################################################################
#ALL PROGRAMS TO BE RUN
gathering_data_programs_1 = gathering_data_file_list1() 
gathering_data_programs_2 = gathering_data_file_list2()
gathering_data_programs_list = gathering_data_programs_1 + gathering_data_programs_2

programs = gathering_data_programs_list #+ processing_data_programs_list


# Create a function to run the programs

#######################################################################################################
#[3] Creating db list of files running
def creating_db_sub_file(subprocess_file_name):

    #Defining Connection and cursor
    connection = sqlite3.connect(subprocess_file_name)
    cursor = connection.cursor()

    #Creating Current exchange_tag price table]

    command1 = """CREATE TABLE IF NOT EXISTS
    proc(number INT, Status TEXT)""" #R/T

    cursor.execute(command1)
    connection.commit()

    #Closing the database
    connection.close()

def run_programs():
    if flag == 1:
        run_demo_trading_account()
    else:
        pass
    
    ################################################
    #Running Process Variables
    processes = []
    for program in programs:
        # Run the program using the subprocess module
        proc = subprocess.Popen(["python", program])
        # Store the process in a list
        processes.append(proc)
        # Update the list of running files
        sleep(1) #Waits 0.5 second between starting every program
    
    #################################################
    #Creating db file for status of running all files
    subprocess_file_name = f"0-Settings/running_bot_programs.db"
    try:
        #Checks to see if there's an existing db file inside the data gathering dircetory
        if os.path.exists(subprocess_file_name) == True:
            connection = sqlite3.connect(subprocess_file_name)
            cursor = connection.cursor()
            cursor.execute(f"""INSERT INTO proc (number, Status) VALUES (1,'R')""")
            #f"""INSERT INTO processed_data (time, {db_name}) VALUES ({formatted_time}, {(exponential_moving_average)})"""
            connection.commit()
            connection.close() #Closing the database

        else: #Creates new db file
            creating_db_sub_file(subprocess_file_name) #Creates new file
            # Runs program again
            connection = sqlite3.connect(subprocess_file_name)
            cursor = connection.cursor()
            cursor.execute(f"""INSERT INTO proc (number, Status) VALUES (1,'R')""")
            #f"""INSERT INTO processed_data (time, {db_name}) VALUES ({formatted_time}, {(exponential_moving_average)})"""
            connection.commit()
            connection.close() #Closing the database
    except Exception as e: #Message email that an error on... has occured
        print(str(e))
    

    
    sleep(3) #Gives program a chance to get created
    #Do a while function now that checks to see if shutdown signal has been sent
    while 1:
        connection = sqlite3.connect(subprocess_file_name)
        cursor = connection.cursor()
        cursor.execute("Select * FROM proc")
        list_check = cursor.fetchall()
        running_data = list_check[-1]
        connection.commit()
        #Closing the database
        connection.close()
        print(running_data[1])
        if running_data[1] == "T": #Terminate the programs
            for proc in processes:
                proc.terminate()
            break

        else: 
            sleep(1)
            pass

        
    
    


# Create a function to terminate the programs
def terminate_programs():
    #Appending runfile status to terminate programs
    subprocess_file_name = f"0-Settings/running_bot_programs.db"

    try:
        connection = sqlite3.connect(subprocess_file_name)
        cursor = connection.cursor()
        cursor.execute(f"""INSERT INTO proc (number, Status) VALUES (2,'T')""")
        connection.commit()
        connection.close() #Closing the database
    except Exception as e: #Message email that an error on... has occured
        print(str(e))




#print(processes)

#######################################################################################################
#UI Interface
st.write("Run Files")

#Creating Buttons that will run the trading bot or terminate it

with st.container():
   col1, col2 = st.columns(2)

   with col1:
       if st.button("Run Bot"):
           run_programs()
           st.write("Programs are running")  # Replace with your desired action

   with col2:
       if st.button("Terminate Bot"):
           terminate_programs()
           st.write("Programs have been Terminates")  # Replace with your desired action

