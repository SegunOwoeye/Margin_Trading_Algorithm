#STRATEGY 2: Adapted Williams Fractal Strategy

""" BRIEF:
        This strategy uses williams fractals, momentum rsi, ema crossover and wf cap
        to determine whether the asset is in an uptrend or a downtrend before placing an order

"""

#General Use Imports
from datetime import datetime
import sqlite3
from time import sleep, time
from os.path import exists
from sys import path
from Trade_Order_Planning import pair_balance, calculating_markers




"""[1] Creating Storage File"""
#CREATES A DATABASE FILE - WORKING
def creating_db_file(trading_pair, exchange_name, flag, db_name = "Strategy2_Orders"):    
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%y")
    ###BELOW NEEDS TO BE EDITED
    if flag == 0: # Live
        file_name = f"4-Strategies/data_gathered/{trading_pair}_data/{str(date)}{exchange_name}{trading_pair}{db_name}.db"
    elif flag == 1: # Demo
        file_name = f"4-Strategies/data_gathered/{trading_pair}_data/{str(date)}{exchange_name}{trading_pair}{db_name}DEMO.db"
    # Checking to see if the file exists
    if exists(file_name):
        pass
    else:
        f = open(file_name, "x")
        
        #Defining Connection and cursor
        connection = sqlite3.connect(file_name)
        cursor = connection.cursor()

        #Creating Current exchange_tag price table]
        #Fractal type can either be Bullish or Bearish
        command1 = f"""CREATE TABLE IF NOT EXISTS
        trade_data(time TEXT, server_time TEXT, trading_pair TEXT, Side TEXT, Order_Type TEXT, Leverage FLOAT, Fund_Amount FLOAT, Equity FLOAT, HIR FLOAT,
            Target_Price FLOAT, Stop_Loss FLOAT, Stop_Limit FLOAT, Entry_Time TEXT, Entry_Order_ID TEXT, Entry_Price FLOAT, O_Funds_Traded FLOAT,
            Exit_Time TEXT, Exit_Price FLOAT, C_Funds_Traded FLOAT, Percentage_Change FLOAT, Entry_Fee FLOAT, Exit_Fee FLOAT, 
            Strat_Name TEXT, Status TEXT, TP_Order_ID TEXT, SL_Order_ID TEXT)"""
        
        #IF TRADE STATUS IS OPEN, THE PURCHASE HASN'T GONE THROUGH
        #IF TRADE STATUS IS CLOSED, THE PURCHASE HAS GONE THROUGH

        cursor.execute(command1)
        connection.commit()

        #Closing the database
        connection.close()


"""[2] READS THE DATA FROM THE PREVIOUS FILES AND OUTPUTS A BULLISH [1] OR BEARIRCH [-1] SIGNAL """
# READS THE DATA IN THE WILLIAMS FRACTAL DB FILE AND RETURNS A PROCESSING SIGNAL
def WF_read(trading_pair, exchange_name, chart_interval):
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")
    file_name = f"2-DataProcessing/data_gathered/{trading_pair}_data/" + str(date) + exchange_name + trading_pair + "interval=" + str(chart_interval) + "WF_data.db"
    #print(file_name)
    connection = sqlite3.connect(file_name, timeout=10.0)
    cursor = connection.cursor()
    cursor.execute("Select * FROM processed_data")
    list_check = cursor.fetchall()
    #COMES OUT as a LIST
    recent_log = list_check[-1] #Most Recent data gathered from file
    connection.commit()
    #Closing the database
    connection.close()
    wf_signal = recent_log[1]

    return wf_signal

# READS THE DATA IN THE EMA DB FILE AND RETURNS A PROCESSING SIGNAL
def ema_read(trading_pair, exchange_name, chart_interval, indicator_interval):
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y")
    file_name = f"2-DataProcessing/data_gathered/{trading_pair}_data/{str(date)}{exchange_name}{trading_pair}interval={str(chart_interval)}tick={indicator_interval}EMAdata.db"
    connection = sqlite3.connect(file_name, timeout=10.0)
    cursor = connection.cursor()
    cursor.execute("Select * FROM processed_data")
    list_check = cursor.fetchall()
    #COMES OUT as a LIST
    recent_log = list_check[-1] #Most Recent data gathered from file
    connection.commit()
    #Closing the database
    connection.close()
    EMA_value = recent_log[1]

    return EMA_value

# READS THE DATA IN THE RSI DB FILE AND RETURNS A PROCESSING SIGNAL
def rsi_read(trading_pair, exchange_name, chart_interval, indicator_interval):
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")
    file_name  = f"2-DataProcessing/data_gathered/{trading_pair}_data/{str(date)}{exchange_name}{trading_pair}interval={str(chart_interval)}tick={indicator_interval}RSIdata.db"
    connection = sqlite3.connect(file_name, timeout=10.0)
    cursor = connection.cursor()
    cursor.execute("Select * FROM processed_data")
    list_check = cursor.fetchall()
    #COMES OUT as a LIST
    recent_log = list_check[-1] #Most Recent data gathered from file
    second_recent_log = list_check[-2] # Second most recent data gathered from file
    connection.commit()
    #Closing the database
    connection.close()
    rsi1_value = recent_log[1] #most recent rsi_value
    rsi2_value = second_recent_log[1] # Second most recent data gathered from file

    if rsi1_value > rsi2_value: # Bullish Signal
        return 1
    elif rsi1_value < rsi2_value: #Bearish Signal
        return -1
    else: # Are equal
        return 0

# READS THE DATA IN THE WF CONFIRMATION DB FILE AND RETURNS A PROCESSING SIGNAL
def wf_cofirmation(trading_pair, exchange_name, chart_interval, indicator_interval, db_name="WFC"):
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")
    file_name = (f"2-DataProcessing/data_gathered/{trading_pair}_data/{str(date)}{exchange_name}{trading_pair}interval="+
                 f"{str(chart_interval)}tick={indicator_interval}{db_name}data.db")
    connection = sqlite3.connect(file_name, timeout=10.0)
    cursor = connection.cursor()
    cursor.execute("Select * FROM processed_data")
    list_check = cursor.fetchall()
    #COMES OUT as a LIST
    recent_log = list_check[-1] #Most Recent data gathered from file
    connection.commit()
    #Closing the database
    connection.close()
    wfc_signal = recent_log[1]

    return wfc_signal
    

""" [3] DETERMINES IF ALL THE CONDITIONS FOR TRIGGERING A LONG/ SHORT SIGNAL HAVE BEEN MET """
def strategy(trading_pair, exchange_name, chart_interval, emaL1_interval, emaL2_interval, emaL3_interval,
             emaS1_interval, emaS2_interval, emaS3_interval, rsi_interval):
    try:
        """GATHERING SIGNALS - W"""
        # WF signal 
        wf_signal = WF_read(trading_pair, exchange_name, chart_interval)
        # EMA value Long
        emaL1_value = ema_read(trading_pair, exchange_name, chart_interval, emaL1_interval)
        emaL2_value = ema_read(trading_pair, exchange_name, chart_interval, emaL2_interval)
        emaL3_value = ema_read(trading_pair, exchange_name, chart_interval, emaL3_interval)
        # EMA value Short
        emaS1_value = ema_read(trading_pair, exchange_name, chart_interval, emaS1_interval)
        emaS2_value = ema_read(trading_pair, exchange_name, chart_interval, emaS2_interval)
        emaS3_value = ema_read(trading_pair, exchange_name, chart_interval, emaS3_interval)
        # EMA Crossover signal
        if emaL1_value > emaL2_value and emaL1_value > emaL3_value:
            ema_signal = 1
        elif emaS1_value < emaS2_value and emaS1_value < emaS3_value:
            ema_signal = -1
        else:
            ema_signal = 0
        # RSI signal
        rsi_signal = rsi_read(trading_pair, exchange_name, chart_interval, rsi_interval)
        # WFC_signal
        wfcL_value = wf_cofirmation(trading_pair, exchange_name, chart_interval, emaL3_interval) # Long
        wfcS_value = wf_cofirmation(trading_pair, exchange_name, chart_interval, emaS3_interval) # Short
        if wfcL_value == 1: # Long
            wfc_signal = 1
        elif wfcS_value == -1: # Short
            wfc_signal = -1
        else: # Do Nothing
            wfc_signal = 0

        total_signals = wf_signal + ema_signal + rsi_signal + wfc_signal
        
        """"""
        # For testing
        message = f"{total_signals}"# For testing
        # RECORDING ERROR
        program_name = f"4-Strategies/Programs/{trading_pair}/Strategy_2_{trading_pair}interval={str(chart_interval)}.py"
        path.append("00-Run_Log/Programs")
        from Log_Output import Record_Output
        Record_Output(trading_pair, exchange_name, message, program_name)
        sleep(1)
        """"""
        
        # COMBINED SIGNAL PROCESSING
        if total_signals == 4: # Go long
            return 1
        elif total_signals == -4: # Go short
            return -1
        else: # Do nothing
            return 0
        
    except Exception as e:
        program_name = f"4-Strategies/Programs/{trading_pair}/Strategy_2_{trading_pair}interval={str(chart_interval)}.py"
        # RECORDING ERROR
        path.append("00-Run_Log/Programs")
        from Log_Output import Record_Output
        Record_Output(trading_pair, exchange_name, e, program_name)

        path.append("ZZ-General_Functions/Programs")
        from Error_handling import Handling_Error
        Handling_Error(e).No_Data_Table_Error(5) # Waits if the table of the file doesn't exist
        return 0 # Do Nothing



"""[4] PRINTING THE CALCULATED DATA TO A DATABASE"""
#PRINT WFC DATA TO DATABASE - WORKING
def printTodatabase(trading_pair, exchange_name, chart_interval, emaL1_interval, emaL2_interval, emaL3_interval,
             emaS1_interval, emaS2_interval, emaS3_interval, rsi_interval, leverage, L_TP, S_TP, 
             L_SL, S_SL, flag, tradeable_fund_Percentage, db_name = "Strategy2_Orders",
             Strategy_Name = "Strategy_2", low_USDT_balance = 100):
    
    # Getting file name
    date_and_time_db = (datetime.now())
    date_db = date_and_time_db.strftime("%y")
    ###BELOW NEEDS TO BE EDITED
    if flag == 0: # Live
        file_name = f"4-Strategies/data_gathered/{trading_pair}_data/{str(date_db)}{exchange_name}{trading_pair}{db_name}.db"
    elif flag == 1: # Demo
        file_name = f"4-Strategies/data_gathered/{trading_pair}_data/{str(date_db)}{exchange_name}{trading_pair}{db_name}DEMO.db"
    try:
        #Checks to see if there's an existing db file inside the data gathering dircetory
        if exists(file_name) == True:  
            Strategy_Name = f"{Strategy_Name}{chart_interval}"
    
            # Getting the Signal
            signal = strategy(trading_pair, exchange_name, chart_interval, emaL1_interval, emaL2_interval, emaL3_interval,
                    emaS1_interval, emaS2_interval, emaS3_interval, rsi_interval)
            
            #signal = -1

            # [0] Gathering the Date and time 
            date_and_time = (datetime.now())
            date = date_and_time.strftime("%m/%d/%Y, %H:%M:%S") #[0] Date

            if abs(signal) == 1:
            
                """ SETUP ORDERBOOK """
                # Side
                if signal == 1:
                    side = "LONG"
                elif signal == -1:
                    side = "SHORT"
                

                #Setup Calculation Class
                calc_marker = calculating_markers(trading_pair, exchange_name,chart_interval, flag, leverage, L_TP,
                                               S_TP,L_SL,S_SL, tradeable_fund_Percentage, side)
                
                tradeing_funds = calc_marker.tradable_funds()
                # [5] Account balance to trade
                balances = pair_balance(trading_pair, exchange_name, chart_interval, flag).flag_balance() # ["BTC", "USDT"]
                # [4] Leverage
                Leverage = leverage
                # [5] Equity
                Equity = tradeing_funds[0]
                # [7] Hourly Interest Rate
                Hourly_Interest_Rate = calc_marker.get_HIR()
                # [8] Target Price (Take Profit)
                Target_Price = calc_marker.get_target_trade_price()
                # [9] Stop Loss
                Stop_Loss = calc_marker.get_stop_loss_price()
                # [22] Stop Limit Price
                Stop_Limit = calc_marker.get_stop_limit_price()
                # [20] Order Type
                Order_type = "OCO" # Order Cancel Order 
                # [18] Account Balance Traded 
                Account_Balance_Traded = tradeing_funds[1] 
                # Timestamp Time
                server_time = round(time(),0)
                # Separate bairs
                base_pair = calc_marker.pair_split()[1]
                asset_pair = calc_marker.pair_split()[0]

                # asset_name
                if signal == 1: # Long
                    asset_name = base_pair
                elif signal == -1: # Short
                    asset_name = asset_pair



                """ SENDING EMAIL NOTIFICATION"""
                path.append("YY_Notifications/Programs") 
                from email_notification import email_alert 
                subject = "Creating an Order"
                message = (f"A {side} {Order_type} order has been placed for {Equity} {asset_name} on a {Leverage}x Leverage using {Account_Balance_Traded} {asset_name} with a " + 
                           f"target price of {Target_Price} {base_pair} for {Strategy_Name}")
                email_recipient = "aces.cryptotrading@gmail.com"
                
                

                """ Sending Order Details to Orderbook """

                # [1] Check if there's a recent trade for the current strategy
                connection = sqlite3.connect(file_name)
                cursor = connection.cursor()

                cursor.execute("Select * FROM trade_data")
                list_check = cursor.fetchall()
                #recent_log = list_check[-1]

                
                """ Impliment method for determining traded funds for the asset"""
                
                path.append("ZZ-General_Functions/Programs")
                from Interval_to_time import convert
                duplicate_time = convert(chart_interval) * 4

                
                # If the orderbook is empty
                if not list_check:
                    #print(f"No Recent trades for {Strategy_Name} with {trading_pair} has recently been placed")

                    cursor.execute(f"""INSERT INTO trade_data (time, server_time, trading_pair, Side, Order_Type, Leverage, Fund_Amount, Equity, HIR,
                    Target_Price, Stop_Loss, Stop_Limit, Strat_Name, Status) VALUES 
                               ("{date}", "{server_time}", "{trading_pair}", "{side}", "{Order_type}", {Leverage}, {Account_Balance_Traded}, {Equity},
                                 {Hourly_Interest_Rate}, {Target_Price}, {Stop_Loss}, {Stop_Limit}, "{Strategy_Name}", "Ready")""")

                    connection.commit()
                    connection.close() #Closing the database
                    # Send Email
                    email_alert(subject, message, email_recipient)
                
                # If an order for the same strategy has recently been placed
                elif ((server_time-float(list_check[-1][1])) <= duplicate_time) and (list_check[-1][22] == Strategy_Name): # Wait and do nothing
                    #print(f"An order for {Strategy_Name} with {trading_pair} has recently been placed")
                    sleep(5)

                # IF Account Balance is Low do Nothing
                elif float(balances) < float(low_USDT_balance):
                    sleep(5)


                else: #Run normally
                    cursor.execute(f"""INSERT INTO trade_data (time, server_time, trading_pair, Side, Order_Type, Leverage, Fund_Amount, Equity, HIR,
                    Target_Price, Stop_Loss, Stop_Limit, Strat_Name, Status) VALUES 
                               ("{date}", "{server_time}", "{trading_pair}", "{side}", "{Order_type}", {Leverage}, {Account_Balance_Traded}, {Equity},
                                 {Hourly_Interest_Rate}, {Target_Price}, {Stop_Loss}, {Stop_Limit}, "{Strategy_Name}", "Ready")""")

                    connection.commit()
                    connection.close()
                    # Send Email
                    email_alert(subject, message, email_recipient)
                



                pass
            else: # Do Nothing
                pass

        
        else: #Creates new db file
            creating_db_file(trading_pair, exchange_name, flag,) #Creates new file
    
    except Exception as e: #Message email that an error on... has occured
        program_name = f"4-Strategies/Programs/{trading_pair}/Strategy_2_{trading_pair}interval={str(chart_interval)}.py"
        # RECORDING ERROR
        path.append("00-Run_Log/Programs")
        from Log_Output import Record_Output
        Record_Output(trading_pair, exchange_name, e, program_name)



"""[5] RUNS THE PROGRAM """
def run(trading_pair, exchange_name, chart_interval, emaL1_interval, emaL2_interval, emaL3_interval,
             emaS1_interval, emaS2_interval, emaS3_interval, rsi_interval, leverage, L_TP, S_TP, 
             L_SL, S_SL, flag, tradeable_fund_Percentage):
    
    while 1:
        try: 
            # Checks to see if program should be suspended before running due to overlap error
            path.append("ZZ-General_Functions/Programs")
            from Suspend_programs import Suspend_programs
            Suspend_programs()

            """ CHECKS TO SEE IF THE REQUIRED FILES ARE PRESENT, IF NOT IT WAITS"""
            # [1] Gets required filenames
            date_and_time = (datetime.now())
            WF_date = date_and_time.strftime("%b%d%y%H")
            ema_date = date_and_time.strftime("%b%d%y")
            RSI_date = date_and_time.strftime("%b%d%y%H")
            WFC_date = date_and_time.strftime("%b%d%y%H")
            
            # WF Name
            WF_filename = f"2-DataProcessing/data_gathered/{trading_pair}_data/" + str(WF_date) + exchange_name + trading_pair + "interval=" + str(chart_interval) + "WF_data.db"
            
            # EMA File List
            ema_filename = []
            ema_intervals = [emaL1_interval, emaL2_interval, emaL3_interval, emaS1_interval, emaS2_interval, emaS3_interval]
            for i in range(len(ema_intervals)):
                ema_filename.append(f"2-DataProcessing/data_gathered/{trading_pair}_data/{str(ema_date)}{exchange_name}{trading_pair}interval={str(chart_interval)}tick={ema_intervals[i]}EMAdata.db")

            # RSI File List
            RSI_filename = []
            RSI_intervals = [rsi_interval]
            for i in range(len(RSI_intervals)):
                RSI_filename.append(f"2-DataProcessing/data_gathered/{trading_pair}_data/{str(RSI_date)}{exchange_name}{trading_pair}interval={str(chart_interval)}tick={RSI_intervals[i]}RSIdata.db")
            
            # WFC File List
            WFC_filename = []
            WFC_intervals = [emaL3_interval, emaS3_interval]
            for i in range(len(WFC_intervals)):
                name = (f"2-DataProcessing/data_gathered/{trading_pair}_data/{str(WFC_date)}{exchange_name}{trading_pair}interval="+
                 f"{str(chart_interval)}tick={WFC_intervals[i]}WFCdata.db")
                WFC_filename.append(name)


            # [2] Checks to see if required files exists
            # [2.1] WF Check
            if exists(WF_filename) == True:
                # [2.2] EMA Check
                ema_file_check = []
                for i in range(len(ema_filename)):
                    if exists(ema_filename[i]) == True:
                        ema_file_check.append(1)
                    else:
                        ema_file_check.append(0)
                if sum(ema_file_check) == len(ema_filename):
                    # [2.3] RSI Check
                    rsi_file_check = []
                    for n in range(len(RSI_filename)):
                        if exists(RSI_filename[n]) == True:
                            rsi_file_check.append(1)
                        else:
                            rsi_file_check.append(0)
                    if sum(rsi_file_check) == len(RSI_filename):
                        # [2.4] WFC Check
                        WFC_file_check = []
                        for m in range(len(WFC_filename)):
                            if exists(WFC_filename[m]) == True:
                                WFC_file_check.append(1)
                            else:
                                WFC_file_check.append(0)
                        if sum(WFC_file_check) == len(WFC_filename): 
                            # Run Program
                            printTodatabase(trading_pair, exchange_name, chart_interval, emaL1_interval, emaL2_interval, emaL3_interval,
                                emaS1_interval, emaS2_interval, emaS3_interval, rsi_interval, leverage, L_TP, S_TP, 
                                L_SL, S_SL, flag, tradeable_fund_Percentage)

                           
                        
                        else:
                            sleep(1)
                    else:
                        sleep(1)

                else:
                    sleep(1)

            else:
                sleep(1)

            """printTodatabase(trading_pair, exchange_name, chart_interval, emaL1_interval, emaL2_interval, emaL3_interval,
                emaS1_interval, emaS2_interval, emaS3_interval, rsi_interval, leverage, L_TP, S_TP, 
                L_SL, S_SL, flag, tradeable_fund_Percentage)
            sleep(2)"""
        except Exception as e:
            program_name = f"4-Strategies/Programs/{trading_pair}/Strategy_2_{trading_pair}interval={str(chart_interval)}.py"
            # RECORDING ERROR
            path.append("00-Run_Log/Programs")
            from Log_Output import Record_Output
            Record_Output(trading_pair, exchange_name, e, program_name)
            
            # HANDLING NO DATA TABLE ERROR
            path.append("ZZ-General_Functions/Programs")
            from Error_handling import Handling_Error
            Handling_Error(e).No_Data_Table_Error()


""" TESTING """
#strategy("BTCUSDT", "Binance", "5m", 20, 50, 100, 15, 45, 90, 6)
#creating_db_file("BTCUSDT", "Binance", 1)

#printTodatabase("BTCUSDT", "Binance", "5m", 20, 50, 100, 15, 45, 90, 6, 3, 0.8, 0.5, 0.7, 1.0, 1, 50)

#run("BTCUSDT", "Binance", "5m", 20, 50, 100, 15, 45, 90, 6, 3, 0.8, 0.5, 0.7, 1.0, 1, 50)





''' For Later

cursor.execute(f"""INSERT INTO trade_data (time, server_time, trading_pair, Side, Order_Type, Leverage, Fund_Amount, Equity, HIR,
                    Target_Price, Stop_Loss, Stop_Limit, Entry_Time, Order_ID, Entry_Price, O_Funds_Traded, Exit_Time, Exit_Price, C_Funds_Traded, 
                                   Percentage_Change, Entry_Fee, Exit_Fee, Strat_Name, Status) VALUES 
                               ("{date}", "{server_time}", "{side}", "{trading_pair}", "{Order_type}", {Leverage}, {Account_Balance_Traded}, {Equity},
                                 {Hourly_Interest_Rate}, {Target_Price}, {Stop_Loss}, {Stop_Limit}, "A", "B", 1, 2, "C", 3, 4, 0.00, 5, 6,"{Strategy_Name}", "Sumbitted")""")





'''