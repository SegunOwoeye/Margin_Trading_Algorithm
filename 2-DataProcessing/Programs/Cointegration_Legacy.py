""" {0} IMPORTING LIBARIES """
# Data processing imports
import pandas as pd
from statsmodels.tsa.vector_ar.vecm import coint_johansen

#from scipy.stats import shapiro

# General Use Imports
from datetime import datetime
import sqlite3
from time import sleep
from os.path import exists
from sys import path as sys_path


# Math Functions Import
sys_path.append("MM-Math_Operations/Programs/")
from Time_Series_Analyzer import Time_Series_Analysis 


""" {1} CLASS DECLARATION """
class Cointegration:
    # [1] Initialiases Variables
    def __init__(self, base_pair, trading_pairs, exchange_name, chart_interval):
        # Cointegrated_pairs
        self.base_pair = base_pair # Base pair (Normally BTCUSDT)
        self.pair_2 = trading_pairs.copy()
        self.pair_2.remove(self.base_pair) 
        self.pair_2 = self.pair_2[0] # 2nd Pair

        self.exchange_name = exchange_name
        self.chart_interval = chart_interval
     
    # [2] CREATES A DATABASE FILE for Cointegration
    def creating_db_file(self):
        date_and_time = (datetime.now())
        date = date_and_time.strftime("%b%d%y%H")
        file_name = f"2-DataProcessing/data_gathered/{self.base_pair}_data/{date}{self.exchange_name}{self.base_pair}{self.pair_2}interval={self.chart_interval}Cointegration_data.db"
        f = open(file_name, "x")
        
        #Defining Connection and cursor
        connection = sqlite3.connect(file_name)
        cursor = connection.cursor()

        #Creating Table 

        command1 = """CREATE TABLE IF NOT EXISTS
        processed_data(time TEXT, is_Coint INT, Base_Return FLOAT, Pair2_Return FLOAT, Spread FLOAT, Zscore FLOAT)"""

        cursor.execute(command1)
        connection.commit()

        #Closing the database
        connection.close()

    # [3] GATHERS THE HISTORICAL DATA OF A CERTAIN NUMBER OF KLINES
    def get_historical_data(self, trading_pairs, indicator_interval=1000):
        date_and_time = (datetime.now())
        date = date_and_time.strftime("%b%d%y")
        file_name = f"1-DataGathering/data_gathered/{trading_pairs}_data/Historical_Klines/{date}{self.exchange_name}{trading_pairs}interval={self.chart_interval}kline_data.db"
        #print(file_name)
        if exists(file_name) == True:
            connection = sqlite3.connect(file_name)
            cursor = connection.cursor()

            cursor.execute("Select * FROM pair_price")
            
            list_check = cursor.fetchall()
            
            #COMES OUT as a LIST
            recent_log = list_check[(-indicator_interval):] #Most Recent data gathered from file
        
            connection.commit()
            #Closing the database
            connection.close()

            return recent_log
        
        else: # If the file doesn't exist, will wait 5 seconds before checking again to see if the file exists
            print("%s file does not exist" % file_name)
            sleep(5)
            self.get_historical_data(trading_pairs)

            
    # [4] GATHERS THE CURRENT DATA OF A CERTAIN NUMBER OF KLINES 
    def get_current_data(self, trading_pairs):
        date_and_time = (datetime.now())
        date = date_and_time.strftime("%b%d%y%H")
        file_name = f"1-DataGathering/data_gathered/{trading_pairs}_data/Live_Data/{date}{self.exchange_name}{trading_pairs}interval={self.chart_interval}kline_data.db"
        #print(file_name)

        # Checks to see if the database exists
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
            self.get_current_data(trading_pairs)


    # [5] Converting a list to a Pandas Dataframe
    def list_to_PD(self, trading_pairs):
        historical_data = self.get_historical_data(trading_pairs)
        current_data = self.get_current_data(trading_pairs)
        data_list = historical_data + current_data # [1] Timestamp, [2] Open, [3] High, [4] Low, [5] Close, [6] Volume
        
        comp_time = []
        close_data = []
        for i in range(len(data_list)):
            data = data_list[i]
            comp_time.append(data[0])
            close_data.append(data[4])

        
        # dictionary of lists 
        dict = {'open_time': comp_time, 'close': close_data} 
            
        df = pd.DataFrame(dict)
        df = df.set_index("open_time")
        return df
    
    
    # [6] Stationarity Check
    def stationarity_check(self, Testing=False):
        pair_list = [self.base_pair, self.pair_2]

        # [6.1] Stationarity
        is_stationary = []
        for i in range(len(pair_list)):
            # [6.1.1] Setting Up Price Data
            if Testing == True:
                price_data = None
            else:
                price_data = self.list_to_PD(pair_list[i])

            # [6.1.2] Importing Time Series Analysis Module
            TSA = Time_Series_Analysis(trading_pair=pair_list[i], chart_interval=self.chart_interval, 
                                       price_data=price_data)
            result = TSA.stationarity_Check()
            #print(result)
            is_stationary.append({"trading_pair": pair_list[i],
                                "chart_interval": self.chart_interval,
                                "Stationary": result[0],
                                "Time_Series": result[1]})
            
        # [6.2] Returns Result of the Stationarity
        stat_return = len(is_stationary)
        for p in range(len(is_stationary)):
            if is_stationary[p]["Stationary"] == True:
                stat_return -= 1
        
        # [3.3] Checking to see if the two Pairs can be cointegrated
        if stat_return == 0: 
            can_cointegrate = True
        else:
            can_cointegrate = False
        returns1 = is_stationary[0]["Time_Series"] # Base_Pair
        returns2 = is_stationary[1]["Time_Series"] # Other Pair

        return can_cointegrate, returns1, returns2

    # [7] Cointegration
    def coint_exec(self):
        # [7.1] Importing Results
        stat_check_results = self.stationarity_check()
        returns1 = stat_check_results[1]
        returns2 = stat_check_results[2]
        
        # [7.1.1] Current Time
        current_time = datetime.now()
        timestamp = str(int(round(current_time.timestamp()*10**3,0)))
        
        # [7.1.2] Get recent return valyes
        recent_return1 = returns1.iloc[-1]
        recent_return2 = returns2.iloc[-1]

        # [7.1.3] Removing Last entry from df
        index1_label = returns1.index[-1]
        index2_label = returns2.index[-1]
        returns1 = returns1.drop([index1_label])
        returns2 = returns2.drop([index2_label])


        # [7.1.4] Adding returns to df with current time
        new_return1 = pd.DataFrame({"open_time": timestamp, 'close': [recent_return1]})
        new_return1 = new_return1.set_index("open_time")['close']
        new_return2 = pd.DataFrame({"open_time": timestamp, 'close': [recent_return2]})
        new_return2 = new_return2.set_index("open_time")['close']
        
        rreturns1 = pd.concat([returns1, new_return1])
        returns2 = pd.concat([returns2, new_return2])


        # [7.2] Executing trade if Cointegrated
        if stat_check_results[0] == True:
            # [7.2.1] Ensure DataFrames have the same shape
            if returns1.shape != returns2.shape:
                raise ValueError("DataFrames must have the same shape")
            
            # [7.2.2] Calculating cointegrating_vector
            merged_results = pd.concat([returns1, returns2], axis=1)
            #print(merged_results, returns1[-1])
            c = coint_johansen(merged_results, det_order=0, k_ar_diff=1) 
            cointegrating_vector = c.evec[:, 0]
            #print(cointegrating_vector)

            # [7.2.3] Calculating Hedging Ratio
            # Normalize the vector (make the first element 1)
            hedge_ratio = round(-cointegrating_vector[1] / cointegrating_vector[0],3)

            # [7.2.4] Calculating Spread
            spread_df = returns1 - returns2 * hedge_ratio

            # [7.2.5] Determining Entry Points Based on z Score
            zscore_df = (spread_df - spread_df.mean())/spread_df.std()
            recent_z_score = zscore_df[-1]

        # [7.3] List out remaining arguements that need to be added to the dataframe, then export
        # Cointegration add_in
        if stat_check_results[0] == True:
            is_coint = 1
        else: 
            is_coint = 0

        # Returns
        Base_Return = returns1[-1]
        Pair2_Return = returns2[-1]

        # Recent Spread
        recent_spread = spread_df[-1]

        return {"is_coint": is_coint,
                "Base_Return": round(Base_Return, 4),
                "Pair2_Return": round(Pair2_Return, 4),
                "Spread": round(recent_spread, 4),
                "Zscore": round(recent_z_score, 4)}
            
    # [8] Printing the Data to a Database
    def printTodatabase(self):
        # [8.1] Importing Data
        data_results = self.coint_exec()
        is_coint =  data_results["is_coint"]
        Base_Return = data_results["Base_Return"]
        Pair2_Return = data_results["Pair2_Return"]
        Spread = data_results["Spread"]
        Zscore = data_results["Zscore"]
        exchange_pair = f"{self.base_pair}{self.pair_2}"

        # [8.2] Gathering date
        date_and_time = (datetime.now())
        date = date_and_time.strftime("%b%d%y%H")

        # [8.3] Setting Filename
        file_name = f"2-DataProcessing/data_gathered/{self.base_pair}_data/{date}{self.exchange_name}{self.base_pair}{self.pair_2}interval={self.chart_interval}Cointegration_data.db"
        # [8.4] Print Data to db
        try:
            # [8.4.1] Checks to see if there's an existing db file inside the data gathering dircetory
            if exists(file_name) == True:
                # [8.4.1.1] Connecting to db
                connection = sqlite3.connect(file_name)
                cursor = connection.cursor()
                current_time = (datetime.now())
                formatted_time = str(current_time.strftime('"%H:%M:%S"'))

                # [8.4.1.2] Adding data to db
                cursor.execute(f"""INSERT INTO processed_data (time, is_Coint, Base_Return, Pair2_Return, Spread, Zscore) VALUES ({formatted_time}, 
                            {int(is_coint)}, {Base_Return}, {Pair2_Return}, {Spread}, {Zscore})""")
                
                connection.commit()
                connection.close() #Closing the database
            
            # [8.4.2] Creates adb file if it doesn't already exist
            else:
                self.creating_db_file()

        # [8.4.3] Error Handling
        except Exception as e: 
            program_name = f"2-DataProcessing/Programs/{self.base_pair}/Cointegration_{exchange_pair}interval={self.chart_interval}.py"
            # RECORDING ERROR
            sys_path.append("00-Run_Log/Programs")
            from Log_Output import Record_Output
            Record_Output(exchange_pair, self.exchange_name, e, program_name)

            # HANDLING NO DATA TABLE ERROR
            sys_path.append("ZZ-General_Functions/Programs")
            from Error_handling import Handling_Error
            Handling_Error(e).No_Data_Table_Error()


# [9] Run Programs
def run(base_pair, trading_pairs, exchange_name, chart_interval):
    while 1:
        try: 
            # [9.1] Initialising and Running Class
            main = Cointegration(base_pair=base_pair, trading_pairs=trading_pairs, exchange_name=exchange_name, chart_interval=chart_interval)
            main.printTodatabase()
            sleep(1)
        
        # [9.2] Error Handling
        except Exception as e:
            exchange_pair = trading_pairs[0] + trading_pairs[1]
            program_name = f"2-DataProcessing/Programs/{base_pair}/Cointegration_{exchange_pair}interval={chart_interval}.py"
            # RECORDING ERROR
            sys_path.append("00-Run_Log/Programs")
            from Log_Output import Record_Output
            Record_Output(exchange_pair, exchange_name, e, program_name)

            # HANDLING NO DATA TABLE ERROR
            sys_path.append("ZZ-General_Functions/Programs")
            from Error_handling import Handling_Error
            Handling_Error(e).No_Data_Table_Error()


'''


""" TESTING """

# Variables
base_pair = "BTCUSDT"
trading_pairs = ["BTCUSDT", "ETHUSDT"]
exchange_name = "Binance"
chart_interval = "5m"


# Run
#main = Cointegration(base_pair=base_pair, trading_pairs=trading_pairs, exchange_name=exchange_name, chart_interval=chart_interval)


# main.creating_db_file() -> Working
# main.get_historical_data(base_pair) # -> Working
# main.get_current_data(base_pair) # -> Working

# print(main.stationarity_check()) # -> Working
# print(main.coint_exec()) # -> Working
# main.printTodatabase() # -> Working


""" Final TEST | Status: PASSED"""
run(base_pair=base_pair, trading_pairs=trading_pairs,exchange_name=exchange_name, chart_interval=chart_interval)

'''