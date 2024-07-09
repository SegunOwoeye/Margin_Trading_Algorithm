import tkinter as tk
import os
import subprocess
from time import sleep


#[1] Setting Up application

#-> Declaring the pairs to be traded
pair_list = ["BTCUSDT"]#, "ETHUSDT"]
#-> Declaring time intervals
#time_intervals = ["1", "5", "15", "60"]

time_intervals = ["5m"]

from sys import path

"""TRADING PAIR LIST"""
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
            Paper_Trading_Account_create.run(individual_pair_list[n], "Binance", "Demo_Balance", 10000.00)

        else:
            Paper_Trading_Account_create.run(individual_pair_list[n], "Binance", "Demo_Balance", 5.00)
            
if flag == 1:
    run_demo_trading_account()
else:
    pass




#[2] Data Gathering
def gathering_data_file_list1():
    # Running historical klines programs
    run_historical_klines = []
    for n in range(len(pair_list)):
        for i in range(len(time_intervals)):
            program_name = f"1-DataGathering/Programs/{pair_list[n]}/Historical_Klines/Data_Gathering_Binance_Historical_{pair_list[n]}_interval={time_intervals[i]}.py"
            run_historical_klines.append(program_name)

    gathering_data_programs_list = run_historical_klines
    return gathering_data_programs_list

def gathering_data_file_list2():
    # Running live klines programs
    run_live_klines = []
    for n in range(len(pair_list)):
        for i in range(len(time_intervals)):
            program_name = f"1-DataGathering/Programs/{pair_list[n]}/Live_Data/Data_Gathering_Binance_Live_{pair_list[n]}_interval={time_intervals[i]}.py"
            run_live_klines.append(program_name)

    gathering_data_programs_list = run_live_klines
    return gathering_data_programs_list


gathering_data_programs_1 = gathering_data_file_list1() 
gathering_data_programs_2 = gathering_data_file_list2()
gathering_data_programs_list = gathering_data_programs_1 + gathering_data_programs_2


#[3] Processing Data into from Market Information
def data_processing_file_lists():
    # Running ATR programs
    run_atr_programs = []
    for n in range(len(pair_list)):
        for i in range(len(time_intervals)):
            program_name = f"2-DataProcessing/Programs/{pair_list[n]}/Average_True_Range_{pair_list[n]}interval={time_intervals[i]}.py"
            run_atr_programs.append(program_name)

    # Running Williams Fractals programs
    run_WF_programs = []
    for n in range(len(pair_list)):
        for i in range(len(time_intervals)):
            program_name = f"2-DataProcessing/Programs/{pair_list[n]}/Williams_Fractals_{pair_list[n]}interval={time_intervals[i]}.py"
            run_WF_programs.append(program_name)
    
    #Running the Money Flow Indicator Programs
    run_MFI_programs = []
    for n in range(len(pair_list)):
        for i in range(len(time_intervals)):
            program_name = f"2-DataProcessing/Programs/{pair_list[n]}/Money_Flow_Index_{pair_list[n]}interval={time_intervals[i]}.py"
            run_MFI_programs.append(program_name)
    
    #Running the Simple Moving Average Programs
    run_SMA_programs = []
    for n in range(len(pair_list)):
        for i in range(len(time_intervals)):
            program_name = f"2-DataProcessing/Programs/{pair_list[n]}/Simple_Moving_Average_{pair_list[n]}interval={time_intervals[i]}.py"
            run_SMA_programs.append(program_name)
    
    #Running the Exponential Moving Average Programs
    run_EMA_programs = []
    for n in range(len(pair_list)):
        for i in range(len(time_intervals)):
            program_name = f"2-DataProcessing/Programs/{pair_list[n]}/Exponential_Moving_Average_{pair_list[n]}interval={time_intervals[i]}.py"
            run_EMA_programs.append(program_name)
    
    #Running the Swings Programs
    run_swings_programs = []
    for n in range(len(pair_list)):
        for i in range(len(time_intervals)):
            program_name = f"2-DataProcessing/Programs/{pair_list[n]}/Swings_{pair_list[n]}interval={time_intervals[i]}.py"
            run_swings_programs.append(program_name)


    program_list = run_atr_programs + run_WF_programs + run_MFI_programs + run_SMA_programs + run_EMA_programs + run_swings_programs
    return program_list
processing_data_programs_list = data_processing_file_lists()


"""ALL PROGRAMS TO BE RUN"""
programs = gathering_data_programs_list #+ processing_data_programs_list

#UI INTERFACE

# Create a function to run the programs
def run_programs():
    for program in programs:
        # Run the program using the subprocess module
        proc = subprocess.Popen(["python", program])
        print(proc)
        # Store the process in a list
        processes.append(proc)
        # Update the list of running files
        running_files.set("\n".join([proc.args[1] for proc in processes]))
        
        sleep(1) #Waits 0.5 second between starting every program
        

# Create a function to terminate the programs
def terminate_programs():
    for proc in processes:
        # Terminate the process
        print(proc)
        proc.terminate()
    # Clear the list of running files
    running_files.set("")

# Create a list to store the running processes
processes = []

# Create the GUI
root = tk.Tk()
root.title("Python Program Runner")

# Create a label to display the running files
running_files = tk.StringVar()
running_files_label = tk.Label(root, textvariable=running_files)
running_files_label.pack()

# Create the "Run Programs" button
run_button = tk.Button(root, text="Run Programs", command=run_programs)
run_button.pack()

# Create the "Terminate Programs" button
terminate_button = tk.Button(root, text="Terminate Programs", command=terminate_programs)
terminate_button.pack()

# Start the GUI event loop
root.mainloop()







