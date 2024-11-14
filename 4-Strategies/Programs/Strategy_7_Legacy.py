#STRATEGY 7: Cointegration

""" BRIEF:
        This strategy uses contegration to between pairs to determine when a secondary asset has
        a greater spread then the base asset

"""

#General Use Imports
from datetime import datetime
import sqlite3
from time import sleep, time
from os.path import exists
from sys import path
from Trade_Order_Planning import pair_balance, calculating_markers


""" [1] Strategy 7 """
class strategy:
    # [1] Initialising Variables
    def __init__(self, trading_pair_list: list, exchange_name: str, flag: int, chart_interval: str, 
                 leverage: int, L_TP: float, S_TP: float, L_SL: float, S_SL: float, tradeable_fund_Percentage: float,
                 trade_type: str, indicator_interval=None, db_name="Strategy7_Orders", low_USDT_balance=5):
        # Trading Pairs
        self.trading_pair_list = trading_pair_list
        self.base_pair = self.trading_pair_list[0]
        self.pair2 = self.trading_pair_list[1]

        self.exchange_name = exchange_name
        self.flag = flag
        self.chart_interval = chart_interval
        self.indicator_interval = indicator_interval
        self.db_name = db_name

        # Order Information
        self.leverage = leverage
        self.L_TP = L_TP
        self.S_TP = S_TP
        self.L_SL = L_SL
        self.S_SL = S_SL
        self.tradeable_fund_Percentage = tradeable_fund_Percentage
        self.low_USDT_balance = low_USDT_balance
        self.trade_type = trade_type




    # [2] Creating Storage File
    def creating_db_file(self):
        # [2.1] Getting Current date in years
        date_and_time = (datetime.now())
        date = date_and_time.strftime("%y")

        # [2.2] Assigning file name based on flag
        if self.flag == 0: # Live
            file_name = f"4-Strategies/data_gathered/{self.base_pair}_data/{str(date)}{self.exchange_name}{self.base_pair}{self.pair2}{self.db_name}.db"
        elif self.flag == 1: # Demo
            file_name = f"4-Strategies/data_gathered/{self.base_pair}_data/{str(date)}{self.exchange_name}{self.base_pair}{self.pair2}{self.db_name}DEMO.db"
        
        # [2.3] Checking to see if the file exists
        # [2.3.1] Do nothing in the file exists
        if exists(file_name):
            pass

        # [2.3.2] Creates a file
        else:
            f = open(file_name, "x")
            
            #Defining Connection and cursor
            connection = sqlite3.connect(file_name)
            cursor = connection.cursor()

            # Creating table
            command1 = f"""CREATE TABLE IF NOT EXISTS
            trade_data(time TEXT, server_time TEXT, trading_pair TEXT, Side TEXT, Order_Type TEXT, Leverage FLOAT, Fund_Amount FLOAT, Equity FLOAT, HIR FLOAT,
                Target_Price FLOAT, Stop_Loss FLOAT, Stop_Limit FLOAT, Entry_Time TEXT, Entry_Order_ID TEXT, Entry_Price FLOAT, O_Funds_Traded FLOAT,
                Exit_Time TEXT, Exit_Price FLOAT, C_Funds_Traded FLOAT, Percentage_Change FLOAT, Entry_Fee FLOAT, Exit_Fee FLOAT, 
                Strat_Name TEXT, Status TEXT, TP_Order_ID TEXT, SL_Order_ID TEXT)"""
            

            cursor.execute(command1)
            connection.commit()

            #Closing the database
            connection.close()

     
    """ READS THE DATA FROM THE PREVIOUS FILES AND OUTPUTS A BULLISH [1] OR BEARISH [-1] SIGNAL """
    # [3] READS THE DATA IN THE Cointegration DB FILE AND RETURNS A PROCESSING SIGNAL
    def cointegration_read(self, std_threshold=2):
        # [3.1] Getting Date
        date_and_time = (datetime.now())
        date = date_and_time.strftime("%b%d%y%H")

        # [3.2] Getting File name of Database
        file_name = f"2-DataProcessing/data_gathered/{self.base_pair}_data/{date}{self.exchange_name}{self.base_pair}{self.pair2}interval={self.chart_interval}Cointegration_data.db"
        
        # [3.3] Connecting to the Database
        connection = sqlite3.connect(file_name, timeout=10.0)
        cursor = connection.cursor()

        # [3.4] Retrieving Data from Database
        cursor.execute("Select * FROM processed_data")
        list_check = cursor.fetchall() # COMES OUT as a LIST
        recent_log = list_check[-1] # Most Recent data gathered from file
        connection.commit()
        #Closing the database
        connection.close()

        # [3.5] Specified recent data
        is_coint = recent_log[1]
        z_score = recent_log[5]
        
        # [3.6] Returning the signal
        if is_coint == 0: # Not Cointegrated
            return 0
        
        elif z_score >= std_threshold: # Bullish -> Long Pair2
            return 1
        elif z_score <= -std_threshold: # Bearish -> Short Pair2
            return -1
        else: return 0


    """ DETERMINES IF ALL THE CONDITIONS FOR TRIGGERING A LONG/ SHORT SIGNAL HAVE BEEN MET """
    # [4] Strategy 7 Logic
    def strat_logic(self, record_signal=False):
        try: 
            # [4.1] Gathering Signals
            coint_value = self.cointegration_read()

            total_signals = coint_value

            # [4.2] Recording Signals to a txt file of required, otherwise it won't        
            if record_signal == True:
                # For testing
                message = f"{total_signals}"# For testing
                # RECORDING ERROR
                program_name = f"4-Strategies/Programs/{self.base_pair}/Strategy_7_{self.base_pair}{self.pair2}interval={str(chart_interval)}.py"
                path.append("00-Run_Log/Programs")
                from Log_Output import Record_Output
                Record_Output(self.base_pair, exchange_name, message, program_name)
                sleep(1)
            else:
                pass


            # [4.3] COMBINED SIGNAL PROCESSING
            if total_signals == 1: # Go long
                return 1
            elif total_signals == -1: # Go short
                return -1
            else: # Do nothing
                return 0
    

        except Exception as e:
            program_name = f"4-Strategies/Programs/{self.base_pair}/Strategy_7_{self.base_pair}{self.pair2}interval={str(chart_interval)}.py"
            # RECORDING ERROR
            path.append("00-Run_Log/Programs")
            from Log_Output import Record_Output
            Record_Output(self.base_pair, exchange_name, e, program_name)

            path.append("ZZ-General_Functions/Programs")
            from Error_handling import Handling_Error
            Handling_Error(e).No_Data_Table_Error(5) # Waits if the table of the file doesn't exist
            
            return 0 # Do Nothing


    """ PRINTING THE CALCULATED DATA TO A DATABASE """
    # [5] Print to database
    def printTodatabase(self):
        """ Trade type:
        = [S]: Short
        - [L]: Long
        - [B]: Short and Long
        """

        # [5.1] Setting Current Time of the db file in years
        date_and_time_db = (datetime.now())
        date_db = date_and_time_db.strftime("%y")

        # [5.2] Setting File Name
        if self.flag == 0: # Live
            file_name = f"4-Strategies/data_gathered/{self.base_pair}_data/{str(date_db)}{self.exchange_name}{self.base_pair}{self.pair2}{self.db_name}.db"
        elif self.flag == 1: # Demo
            file_name = f"4-Strategies/data_gathered/{self.base_pair}_data/{str(date_db)}{self.exchange_name}{self.base_pair}{self.pair2}{self.db_name}DEMO.db"
        
        # [5.3]
        try:
            # [5.3.1] Checks to see if there's an existing db file inside the data gathering dircetory
            # [5.3.1.1] File Exists
            if exists(file_name) == True: 
                ## [1] Renaming Strategy_Name
                Strategy_Name = f"{Strategy_Name}{chart_interval}"

                ## [2] Getting the Signal
                signal = self.strat_logic()

                ## [3] Gathering Current date and time down to seconds
                date_and_time = (datetime.now())
                date = date_and_time.strftime("%m/%d/%Y, %H:%M:%S") 

                #signal = -1 # -> For testing

                ## [4] Analysing signal
                ## [4.1] Signal to Order 
                if abs(signal) == 1:
                    """ SETUP ORDERBOOK """

                    ## [4.1.1] Side
                    if signal == 1: #== 1:
                        side = "LONG"
                    elif signal == -1: #== -1:
                        side = "SHORT"

                    ## [4.1.2] Makes sure Signal and Trade_Type match up
                    if self.trade_type == "B": #-> Long and Short
                        pass
                    elif (self.trade_type == "S") and (side == "SHORT"): #-> Short only with short signal
                        pass
                    elif (self.trade_type == "L") and (side == "LONG"): #-> Long only with long signal
                        pass
                    else: return # Stop rest of function from executing

                    
                    ## [4.1.3] Setting Up Calculation Class
                    calc_marker = calculating_markers(trading_pair=self.pair2, exchange_name=self.exchange_name,
                                                      chart_interval=self.chart_interval, leverage=self.leverage,
                                                      L_TP=self.L_TP, S_TP=self.S_TP, L_SL=self.L_SL, S_SL=self.S_SL,
                                                      tradable_funds_percentage=self.tradeable_fund_Percentage, side=side)
                    trading_funds = calc_marker.tradable_funds()
                    """ The Numbers inside the curley brackets {}, are the positions in the database """
                    ### {5} Account Balance to Trade
                    balances = pair_balance(trading_pair=self.pair2, exchange_name=self.exchange_name,
                                            chart_interval=self.chart_interval, flag=self.flag).flag_balance[1]
                    ### {4} Leverage
                    Leverage = self.leverage
                    ### {5} Equity
                    Equity = trading_funds[0]
                    ### {7} Hourly Interest Rate
                    Hourly_Interest_Rate = calc_marker.get_HIR()
                    


                ## [4.2] NO order signal -> Do Nothing
                else: pass
            

            # [5.3.1.2] When File Doesn't Exist
            else: #Creates new db file
                self.creating_db_file()

        # [5.4] File ouput recording the error
        except Exception as e: 
            program_name = f"4-Strategies/Programs/{self.base_pair}/Strategy_7_{self.base_pair}{self.pair2}interval={str(chart_interval)}.py"
            # RECORDING ERROR
            path.append("00-Run_Log/Programs")
            from Log_Output import Record_Output
            Record_Output(self.base_pair, exchange_name, e, program_name)





""" TESTING """

# Variables
trading_pair_list = ["BTCUSDT", "ETHUSDT"] 
exchange_name = "Binance"
flag = 0 
chart_interval = "1h"

leverage = 3
trade_type = "S"
L_TP = 0
S_TP = 0.9
L_SL = 0
S_SL = 1.5
tradeable_fund_Percentage = 50


main = strategy(trading_pair_list=trading_pair_list, exchange_name=exchange_name, flag=flag, 
                chart_interval=chart_interval, leverage=leverage, trade_type=trade_type, L_TP=L_TP,
                S_TP=S_TP, L_SL=L_SL, S_SL=S_SL, tradeable_fund_Percentage=tradeable_fund_Percentage)

# Function Testing
# main.creating_db_file() # -> Working
# print(main.cointegration_read()) # -> Working
print(main.strat_logic()) # ->

