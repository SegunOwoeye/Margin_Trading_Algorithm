import tkinter as tk
import sqlite3
from os import remove, kill, path
import subprocess
from time import sleep, time
from sys import path as sys_path
from signal import SIGTERM

####################################################################################
# [0] Getting System Config
####################################################################################
# Changing Path
sys_path.append("0-Settings/Program_Files/Misc/")
from read_config import run # User Defined Function
program_settings = run()

####################################################################################
#[1] Setting Up application
####################################################################################
#-> Declaring the pairs to be traded
pair_list = program_settings["application_settings"]["pair_list"]

#-> Getting list of signular assets (Ex: BTC, ETH, USDT)
def sing_asset_list():
    asset_pairs = []
    for i in range(len(pair_list)):
        asset_name = pair_list[i].replace("USDT", "")
        asset_pairs.append(asset_name)

    asset_pairs.append("USDT")

    return asset_pairs
asset_list = sing_asset_list()

# [A] Data Gathering Interval Settings
dg_settings = program_settings["application_settings"]["data_gathering"]

time_intervals = dg_settings["time_intervals"] # Declaring time intervals
config_ti = dg_settings["config_ti"] # Time intervals for creating program files 
limit = dg_settings["historical_data_limit"] # Declaring Limit for Historical Data Gathered
levels = dg_settings["orderbook_levels"] # Declaring levels for Orderbook


# [B] Data Processing Interval Settings
dp_settings = program_settings["application_settings"]["data_processing"]

sma_intervals = dp_settings["sma_long_intervals"] + dp_settings["sma_short_intervals"] # SMA Intervals
ema_intervals = dp_settings["ema_long_intervals"] + dp_settings["ema_short_intervals"] # EMA Intervals
wf_intervals = dp_settings["wf_intervals"]
rsi_intervals = dp_settings["rsi_intervals"]
wfc_intervals = dp_settings['wfc_intervals']


# [C] TRADING ENVIRONMENT (flag)
#     [0] LIVE TRADING
#     [1] DEMO TRADING

flag = program_settings["application_settings"]['trading_environment']['flag'] # Flag


# [D] CREATING FOLDERS
sys_path.append("0-Run")
from Setup import start_1, start_2, start_3, start_4, start_5

#[1.1] Creates folders for data storage
####################################################################################
start_1(pair_list)
start_2(pair_list)
start_3(pair_list)
start_4(pair_list)
start_5(pair_list)

#[1.2] Creates python files for data gathering and analysis
####################################################################################
from config_files.Data_Gathering_file_C import create_data_gathering

#Create programs for data Gathering
create_data_gathering(pair_list, config_ti, limit, levels)

#[1.3] Creates pdb file for strats
sys_path.append("4-Strategies/Programs/")
from Strategy_2_Legacy import creating_db_file
strat_db_list = program_settings["application_settings"]["strategies"]
for i in range(len(strat_db_list)):
    for p in range(len(pair_list)):
        creating_db_file(pair_list[p], "Binance", flag, db_name = strat_db_list[i])

####################################################################################
#[2] Data Gathering
####################################################################################
def gathering_data_file_list1(): #COMPLETE
    # Running historical klines programs
    run_historical_klines = []
    for n in range(len(pair_list)):
        for i in range(len(time_intervals)):
            program_name = f"1-DataGathering/Programs/{pair_list[n]}/Historical_Klines/Data_Gathering_Binance_Historical_{pair_list[n]}_interval={time_intervals[i]}.py"
            run_historical_klines.append(program_name)

    gathering_data_programs_list = run_historical_klines
    return gathering_data_programs_list

def gathering_data_file_list2(): #COMPLETE
    # Running live klines programs
    run_live_klines = []
    for n in range(len(pair_list)):
        for i in range(len(time_intervals)):
            program_name = f"1-DataGathering/Programs/{pair_list[n]}/Live_Data/Data_Gathering_Binance_Live_{pair_list[n]}_interval={time_intervals[i]}.py"
            run_live_klines.append(program_name)

    gathering_data_programs_list = run_live_klines
    return gathering_data_programs_list

def gathering_data_file_list3(): #PENDING TESTS
    #Running Orderbook
    run_orderbooks = []
    for n in range(len(pair_list)):
        program_name = f"1-DataGathering/Programs/{pair_list[n]}/Live_Data/Data_Gathering_Binance_{pair_list[n]}_Orderbook.py"
        run_orderbooks.append(program_name)

    gathering_data_programs_list = run_orderbooks
    return gathering_data_programs_list

####################################################################################
#[3] Processing Data into from Market Information
####################################################################################

def data_processing_file_lists():
    # Running ATR programs
    run_atr_programs = []
    for n in range(len(pair_list)):
        for i in range(len(time_intervals)):
            program_name = f"2-DataProcessing/Programs/{pair_list[n]}/Average_True_Range_{pair_list[n]}interval={time_intervals[i]}.py"
            run_atr_programs.append(program_name)

    #Running GARCH programs
    run_GARCH_programs = []
    for n in range(len(pair_list)):
        for i in range(len(time_intervals)):
            program_name = f"2-DataProcessing/Programs/{pair_list[n]}/GARCH_Model_{pair_list[n]}interval={time_intervals[i]}.py"
            run_GARCH_programs.append(program_name)

    #Running Mean Reversion programs
    run_mr_programs = []
    for n in range(len(pair_list)):
        for i in range(len(time_intervals)): 
            program_name = f"2-DataProcessing/Programs/{pair_list[n]}/Mean_Reversion_{pair_list[n]}interval={time_intervals[i]}.py"
            run_mr_programs.append(program_name)
    
    #Running SMA programs
    run_SMA_programs = []
    for n in range(len(pair_list)):
        for i in range(len(time_intervals)): 
            for l in range(len(sma_intervals)):
                program_name = f"2-DataProcessing/Programs/{pair_list[n]}/Simple_Moving_Average_{pair_list[n]}interval={time_intervals[i]}tick={sma_intervals[l]}.py"
                run_SMA_programs.append(program_name)

    #Running EMA programs
    run_EMA_programs = []
    for n in range(len(pair_list)):
        for i in range(len(time_intervals)): 
            for l in range(len(ema_intervals)):
                program_name = f"2-DataProcessing/Programs/{pair_list[n]}/Exponential_Moving_Average_{pair_list[n]}interval={time_intervals[i]}tick={ema_intervals[l]}.py"
                run_EMA_programs.append(program_name)

    #Running WF programs
    run_WF_programs = []
    for n in range(len(pair_list)):
        for i in range(len(time_intervals)): 
            for l in range(len(wf_intervals)):
                program_name = f"2-DataProcessing/Programs/{pair_list[n]}/Williams_Fractals_{pair_list[n]}interval={time_intervals[i]}tick={wf_intervals[l]}.py"
                run_WF_programs.append(program_name)

    #Running RSI programs
    run_RSI_programs = []
    for n in range(len(pair_list)):
        for i in range(len(time_intervals)): 
            for l in range(len(rsi_intervals)):
                program_name = f"2-DataProcessing/Programs/{pair_list[n]}/Relative_Strength_Indicator_{pair_list[n]}interval={time_intervals[i]}tick={rsi_intervals[l]}.py"
                run_RSI_programs.append(program_name) 
    
    #Running WFC programs 
    run_WFC_programs = []
    for n in range(len(pair_list)):
        for i in range(len(time_intervals)): 
            for l in range(len(rsi_intervals)):
                program_name = f"2-DataProcessing/Programs/{pair_list[n]}/Williams_Fractal_Cap_{pair_list[n]}interval={time_intervals[i]}tick={wfc_intervals[l]}.py"
                run_WFC_programs.append(program_name)  


    # Running Delete Empty Files programs
    run_File_Monitoring = []
    sections_monitored = 2
    for i in range(sections_monitored):
        program_name = f"Misc/Programs/FIle_Monitoring/File_Monitoring_{i+1}.py"
        run_File_Monitoring.append(program_name)
    additional_program_name = "Misc/Programs/FIle_Monitoring/File_Monitoring_5.py"
    run_File_Monitoring.append(additional_program_name)
    
    """program_list = (run_atr_programs + run_GARCH_programs + run_mr_programs + run_SMA_programs + run_EMA_programs + run_WF_programs 
                    + run_RSI_programs + run_WFC_programs)"""
    
    program_list = (run_SMA_programs + run_EMA_programs + run_WF_programs 
                    + run_RSI_programs + run_WFC_programs + run_File_Monitoring)
    
    return program_list

####################################################################################
#[4] Get Account Balances
####################################################################################

def demo_account_Balance_list(): # Creates Demo account balances for relevant pairs
    #Running Demo_balance programs | Onlyy Runs USDT Account
    run_demo_balance_programs = []
    """for p in range(len(asset_list)): 
        program_name = F"3-AccountBalance/Programs/{asset_list[p]}/Paper_Trading_Account_Create_{asset_list[p]}.py"
        run_demo_balance_programs.append(program_name)"""
    program_name = F"3-AccountBalance/Programs/USDT/Paper_Trading_Account_Create_USDT.py"
    run_demo_balance_programs.append(program_name)
    return run_demo_balance_programs            

def live_account_Balance_list(): # Gets live account balances for relevant pairs
    # Running Live balance programs 
    run_live_balance_programs = []
    for p in range(len(asset_list)):
        program_name = F"3-AccountBalance/Programs/{asset_list[p]}/Live_Account_Balance_Legacy_{asset_list[p]}.py"
        run_live_balance_programs.append(program_name) 
    return run_live_balance_programs 


if flag == 1: # Demo
    account_balance_program = demo_account_Balance_list()
elif flag == 0: # Live
    account_balance_program = live_account_Balance_list()
else:
    pass

####################################################################################
#[5] Programs to monitor live trades
####################################################################################

def live_trade_monitoring_file_lists():
    # Running asset precision monitoring programs
    run_asset_precision = []
    for n in range(len(pair_list)): 
        program_name = f"5-Trade_Monitoring/Programs/{pair_list[n]}/asset_precision_{pair_list[n]}.py"
        run_asset_precision.append(program_name)
    
    # Running Hourling Interest rate monitoring programs
    run_HIR = []
    for n in range(len(pair_list)): 
        program_name = f"5-Trade_Monitoring/Programs/{pair_list[n]}/Hourly_Interest_Rate_{pair_list[n]}.py"
        run_HIR.append(program_name)

    program_list = run_asset_precision + run_HIR

    return program_list


####################################################################################
#[6] Programs for Strategies to place orders
####################################################################################
def strategy_file_list():
    # Running asset strategy 2 programs
    run_strategy_2 = []
    for n in range(len(pair_list)): 
        for p in range(len(time_intervals)):
            program_name = f"4-Strategies/Programs/{pair_list[n]}/Strategy_2_{pair_list[n]}interval={time_intervals[p]}.py"
            run_strategy_2.append(program_name)
    

    program_list = run_strategy_2

    return program_list

####################################################################################
# [7] Programs for Orderbook Monitoring
####################################################################################
def orderbook_monitoring_file_lists():
    # Running orderbook monitoring programs
    run_orderbook_monitoring = []
    for n in range(len(pair_list)):
        for i in range(len(time_intervals)):
            program_name = f"5-Trade_Monitoring/Programs/{pair_list[n]}/Orderbook_Monitoring_{pair_list[n]}_Interval={time_intervals[i]}.py"
            run_orderbook_monitoring.append(program_name)



    program_list = run_orderbook_monitoring

    return program_list

####################################################################################
# [8] Core Programs
####################################################################################
def core_programs_list():
    program_name = ["0-Run/RunTime_Tools/Restart_[Start(Main)].py"]
    return program_name



####################################################################################
#[9] lists of all programs to be run
####################################################################################

# 1. Account Balance Gathering + {Trade system startup}
trade_sys_start_programs = core_programs_list()
account_balance_programs = account_balance_program

# 2. Raw Data Gathering
gathering_data_programs_1 = gathering_data_file_list1() 
gathering_data_programs_2 = gathering_data_file_list2()
gathering_data_programs_3 = gathering_data_file_list3()
raw_data_lists = gathering_data_programs_1 + gathering_data_programs_2 + gathering_data_programs_3
# 3. Processed Data Gathering
processed_data_program = data_processing_file_lists()

# 4. Trade monitoring
trade_monitoring_programs = live_trade_monitoring_file_lists()

# 5. Strategies
strategy_programs = strategy_file_list()

# 6. Orderbook Monitoring
orderbook_monitoring_programs = orderbook_monitoring_file_lists()

gathering_programs_list = trade_sys_start_programs + account_balance_programs + raw_data_lists + processed_data_program + trade_monitoring_programs + strategy_programs + orderbook_monitoring_programs




"""ALL PROGRAMS TO BE RUN"""
programs = gathering_programs_list 

#UI INTERFACE

# Create a function to run the programs
def run_programs():
    """ [1] CREATE .DB FILE WITH ALL THE CURRENTLY RUNNING PROGRAMS, FILE OF PROC"""
    main_program_tasks = f"0-Run/RunTime_Tools/Data_Files/Task_Manager.db"
    connection = sqlite3.connect(main_program_tasks)
    cursor = connection.cursor()


    environment = ".venv/Scripts/python.exe" # For virtual environment #"python" - > Defaullt
    for program in programs:
        # Run the program using the subprocess module
        proc = subprocess.Popen([environment, program])
        # Store the process in a list
        processes.append(proc)
        # Update the list of running files
        running_files.set("\n".join([proc.args[1] for proc in processes]))
        
        # [2] Sending list of programs to database
        #Creating Table
        cursor.execute(f"""INSERT INTO Tasks (Process_Name, PID) VALUES ("{proc.args[1]}", "{proc.pid}")""")
        connection.commit()
        #Closing the database

        sleep(1) #Waits 0.5 second between starting every program
    
    connection.close()

# Create a function to terminate the programs
def terminate_programs():
    # [1] Connect to db file
    main_program_tasks = f"0-Run/RunTime_Tools/Data_Files/Task_Manager.db"
    connection = sqlite3.connect(main_program_tasks)
    cursor = connection.cursor()
    
    # [2] Loop through database of processes and stop them
    cursor.execute("Select * FROM Tasks")
    program_process_list = cursor.fetchall()

    for i in range(len(program_process_list)):
        pid = program_process_list[i][1]
        kill(int(pid), SIGTERM)
    
    # [3] Close the connection and delete the task file
    connection.close()
    remove(main_program_tasks) 


    """for proc in processes:
        # Terminate the process
        print(proc)
        proc.terminate()"""
    # Clear the list of running files
    running_files.set("")
    processes.clear() # Removes previous processes from the list

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

""" Creates the database files required for monitoring the runtime of the program"""
class create_database_files:
    # Initialising variables
    def __init__(self, file_name):
        self.file_name = file_name

    def program_timings(self):
        #Defining Connection and cursor
        connection = sqlite3.connect(self.file_name)
        cursor = connection.cursor()
        #Creating Table
        command1 = """CREATE TABLE IF NOT EXISTS
        times(Start_Timestamp TEXT, Last_Updated TEXT)"""
        cursor.execute(command1)
        current_timestamp = round(time())
        cursor.execute(f"""INSERT INTO times (Start_Timestamp) VALUES ({current_timestamp})""")
        connection.commit()
        #Closing the database
        connection.close()

    def live_programs(self):
        #Defining Connection and cursor
        connection = sqlite3.connect(self.file_name)
        cursor = connection.cursor()
        #Creating Table
        command1 = """CREATE TABLE IF NOT EXISTS
        Tasks(Process_Name TEXT, PID TEXT)"""
        cursor.execute(command1)
        connection.commit()
        #Closing the database
        connection.close()



def start_crypto_bot():
    """ [0] Delete orevious system start db files"""
    # [0.1] File Names
    main_time_file_name = f"0-Run/RunTime_Tools/Data_Files/Main_program_timings.db"
    main_program_tasks = f"0-Run/RunTime_Tools/Data_Files/Task_Manager.db"

    db_start_names_list = [main_time_file_name, main_program_tasks]

    # [0.2] For loop to see if file exists and if it does, deletes it
    for i in range(len(db_start_names_list)):
        if path.exists(db_start_names_list[i]):
            remove(db_start_names_list[i])
        else: pass # Do Nothing

    """ [1] Create .db file for main """
    # [1.1] Create .db for time program was started 
    create_database_files(main_time_file_name).program_timings()

    # [1.2] Create .db for the all the programs run for the algo
    create_database_files(main_program_tasks).live_programs()

    
    """ [2] Start the GUI event loop """
    root.mainloop()
    
    """ [3] Deleted .db file for main program timings """
    remove(main_time_file_name)

# Runs the program
start_crypto_bot()







