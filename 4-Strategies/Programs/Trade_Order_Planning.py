from datetime import datetime
from os.path import exists
import sqlite3
from sys import path
from math import floor, log10

# [5] Class for retrieving balance details
class pair_balance:
    #Initialises variables for use through the class
    def __init__(self, trading_pair, exchange_name, chart_interval, flag):
        self.trading_pair = trading_pair
        self.exchange_name = exchange_name
        self.flag = flag
        self.chart_interval = chart_interval 
    
    #Splits the trading pair into individual assets
    def pair_split(self):
        if "USDT" in self.trading_pair:
            pair1 = self.trading_pair.replace("USDT","")
            pair2 = "USDT"
            return pair1, pair2

        elif "USDC" in self.trading_pair:
            pair1 = self.trading_pair.replace("USDC","")
            pair2 = "USDC"
            return [pair1, pair2]
    
    # [1] Get the balances of the tradig pairs for the demo account
    def get_demo_balances(self):
        # Getting Symbols
        pairs = pair_balance(self.trading_pair, self.exchange_name, self.chart_interval, self.flag).pair_split()
        balance_list = []
        # Geting demo balance for each symbol
        for i in range(len(pairs)):
            db_name = "Demo_Balance"
            date_and_time = (datetime.now())
            date = date_and_time.strftime("%b%d%y")
            file_name = f"3-AccountBalance/data_gathered/{pairs[i]}_data/{date}{self.exchange_name}{pairs[i]}{db_name}_data.db"
            #print(file_name)
            
            try:
                if exists(file_name):
                    connection = sqlite3.connect(file_name)
                    cursor = connection.cursor()

                    cursor.execute("Select * FROM account_balance")
                    
                    list_check = cursor.fetchall()
                    recent_log = list_check[-1] #Most Recent data gathered from file
                
                    connection.commit()
                    #Closing the database
                    connection.close()
                    balance_list.append(recent_log[1])

            except Exception as e: # 2-DataProcessing\Programs\BTCUSDT\Exponential_Moving_Average_BTCUSDTinterval=1mtick=50.py
                error_file_name = f"4-Strategies/Programs/{self.trading_pair}/Strategy_2_{self.trading_pair}interval={self.chart_interval}.py"
                print(F"{error_file_name}: {e}")

        return balance_list

    # [0] Get the balances of the tradig pairs for the live account
    def get_live_balances(self):
         # Getting Symbols
        pairs = pair_balance(self.trading_pair, self.exchange_name, self.chart_interval, self.flag).pair_split()
        balance_list = []
        # Geting demo balance for each symbol
        for i in range(len(pairs)):
            db_name = "Live_Balance"
            date_and_time = (datetime.now())
            date = date_and_time.strftime("%b%d%y")
            file_name = f"3-AccountBalance/data_gathered/{pairs[i]}_data/{date}{self.exchange_name}{pairs[i]}{db_name}_data.db"
            #print(file_name)
            
            try:
                if exists(file_name):
                    connection = sqlite3.connect(file_name)
                    cursor = connection.cursor()

                    cursor.execute("Select * FROM account_balance")
                    
                    list_check = cursor.fetchall()
                    recent_log = list_check[-1] #Most Recent data gathered from file
                
                    connection.commit()
                    #Closing the database
                    connection.close()
                    balance_list.append(recent_log[1])

            except Exception as e: # 2-DataProcessing\Programs\BTCUSDT\Exponential_Moving_Average_BTCUSDTinterval=1mtick=50.py
                error_file_name = f"4-Strategies/Programs/{self.trading_pair}/Strategy_2_{self.trading_pair}interval={self.chart_interval}.py"
                print(F"{error_file_name}: {e}")


        return balance_list

    ### GETS THE BALANCE INFO FROM EITHER THE DEMO OR THE LIVE ACCOUNT
    def flag_balance(self):
        if self.flag == 1: # Demo
            return pair_balance(self.trading_pair, self.exchange_name, self.chart_interval, self.flag).get_demo_balances()
        elif self.flag == 0: # Live
            return pair_balance(self.trading_pair, self.exchange_name, self.chart_interval, self.flag).get_live_balances()

# Class for calculating Markers based on order conditions
class calculating_markers:
    #Initialises variables for use through the class
    def __init__(self, trading_pair, exchange_name, chart_interval, flag, leverage, L_TP, S_TP, 
                 L_SL, S_SL, tradable_funds_percentage, side):
        self.trading_pair = trading_pair
        self.exchange_name = exchange_name
        self.flag = flag
        self.chart_interval = chart_interval 
        self.leverage = leverage
        self.L_TP = L_TP
        self.S_TP = S_TP
        self.L_SL = L_SL
        self.S_SL = S_SL
        self.tradable_funds_percentage = tradable_funds_percentage
        self.side = side

    # Function for getting the current Closing Price of an asset - WORKING
    def get_current_data(self):
        path.append("ZZ-General_Functions/Programs")
        from get_current_data import current_data
        return current_data(self.trading_pair, self.exchange_name, self.chart_interval)
    
    # [4] Leverage
    def Leverage(self):
        return self.leverage

    #Splits the trading pair into individual assets
    def pair_split(self):
        if "USDT" in self.trading_pair:
            pair1 = self.trading_pair.replace("USDT","")
            pair2 = "USDT"
            return pair1, pair2

        elif "USDC" in self.trading_pair:
            pair1 = self.trading_pair.replace("USDC","")
            pair2 = "USDC"
            return [pair1, pair2]
    
    # Gets the precision of the asset
    def get_asset_precision(self):
        try:
            date_and_time = (datetime.now())
            date = date_and_time.strftime("%b%d%y")
            file_name = f"5-Trade_Monitoring/data_gathered/{self.trading_pair}_data/{date}{self.trading_pair}precision_data.db"
            #print(file_name)
            connection = sqlite3.connect(file_name)
            cursor = connection.cursor()

            cursor.execute("Select * FROM Precision_Data")
            
            list_check = cursor.fetchall()
            
            #COMES OUT as a LIST
            recent_log = list_check[-1] #Most Recent data gathered from file
        
            connection.commit()
            #Closing the database
            connection.close()
            return recent_log
        except:
            return ["Time", 8, 8]

    # Rounds the number to the amount of significant figures determined by the asset precision
    def round_sign_number(self, precision: int, value: float):
        return round(value, -int(floor(log10(abs(value)))) + (precision - 1))

    # [6] Returns the amount of symbol to be traded condsidering leverage
    def tradable_funds(self): # WORKING
        pairs = calculating_markers(self.trading_pair, self.exchange_name, self.chart_interval, self.flag, self.leverage, 
                                    self.L_TP, self.S_TP, self.L_SL, self.S_SL, self.tradable_funds_percentage,
                                    self.side).pair_split()
        
        precision_data = calculating_markers(self.trading_pair, self.exchange_name, self.chart_interval, self.flag, self.leverage, 
                                    self.L_TP, self.S_TP, self.L_SL, self.S_SL, self.tradable_funds_percentage,
                                    self.side).get_asset_precision()
        
        # For Initialising trades, all assets origionate from the USDT balance
        for i in range(len(pairs)):
            if (pairs[i] == "USDT" or pairs[i] == "USDC"): 
                if self.side == "LONG":
                    balance = pair_balance(self.trading_pair, self.exchange_name, self.chart_interval, self.flag).flag_balance()[1]
                    precision = precision_data[2]
                else: pass
            elif self.side == "SHORT":
                balance = pair_balance(self.trading_pair, self.exchange_name, self.chart_interval, self.flag).flag_balance()[1]
                precision = precision_data[2]
            else: pass
          
        ### NEED TO FIND THE PRECISION OF ALL ASSETS
        # Continues with Regular Operation for Leveraging
        if self.side == "LONG":   
            equity = balance * (self.tradable_funds_percentage/100) * self.leverage
            Account_balance_Traded = balance * (self.tradable_funds_percentage/100)
        # Special conditioning
        elif self.side == "SHORT":
            closing_price = self.get_current_data()[4]
            #print(closing_price)
            equity = (balance * (self.tradable_funds_percentage/100) * (self.leverage-1))/closing_price
            Account_balance_Traded = (balance * (self.tradable_funds_percentage/100))/closing_price


        return self.round_sign_number(precision, equity), self.round_sign_number(precision, Account_balance_Traded)
        
    # [7] Gets the hourly interest rate of the asset
    def get_HIR(self):
        date_and_time = (datetime.now())
        date = date_and_time.strftime("%b%d%y")
        file_name = f"5-Trade_Monitoring/data_gathered/{self.trading_pair}_data/{date}{self.trading_pair}HIR_data.db"
        #print(file_name)
        connection = sqlite3.connect(file_name)
        cursor = connection.cursor()

        cursor.execute("Select * FROM HIR_Data")
        
        list_check = cursor.fetchall()
        
        #COMES OUT as a LIST
        recent_log = list_check[-1] #Most Recent data gathered from file
    
        connection.commit()
        #Closing the database
        connection.close()
        return recent_log[1]
    
    # [8] Calculates the price the asset needs to reach to Take Profit
    def get_target_trade_price(self):
        precision = self.get_asset_precision()[1]
        date_and_time = (datetime.now())
        date = date_and_time.strftime("%b%d%y%H")
        file_name = f"1-DataGathering/data_gathered/{self.trading_pair}_data/Live_Data/" + str(date) + self.exchange_name + self.trading_pair + "interval=" + str(self.chart_interval) + "kline_data.db"
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
        
        current_price = recent_log[4]
        
        # Target Price depends on going LONG or SHORT
        if self.side == "LONG":
            target_trade_price = current_price * (1 + (self.L_TP)/100)
        elif self.side == "SHORT":
            target_trade_price = current_price * (1 - (self.S_TP)/100)

        return self.round_sign_number(precision,target_trade_price)
    
    # [9] Calculates the price the asset needs to reach to trigger the stop loss
    def get_stop_loss_price(self):
        precision = self.get_asset_precision()[1]
        date_and_time = (datetime.now())
        date = date_and_time.strftime("%b%d%y%H")
        file_name = f"1-DataGathering/data_gathered/{self.trading_pair}_data/Live_Data/" + str(date) + self.exchange_name + self.trading_pair + "interval=" + str(self.chart_interval) + "kline_data.db"
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
        
        current_price = recent_log[4]
        
        # Stop Loss depends on going LONG or SHORT
        if self.side == "LONG":
            stop_loss_price = current_price * (1 - (self.L_SL)/100)
        elif self.side == "SHORT":
            stop_loss_price = current_price * (1 + (self.S_SL)/100)

        return self.round_sign_number(precision,stop_loss_price)

    # [22] Calculates the price the asset stop limit
    def get_stop_limit_price(self):
        precision = self.get_asset_precision()[1]
        # Stop limit will be within 1% 
        stop_loss = self.get_stop_loss_price()

        if self.side == "LONG":
            stop_limit = stop_loss * (1 - (1)/100)
        elif self.side == "SHORT":
            stop_limit = stop_loss * (1 + (1)/100)
        
        return self.round_sign_number(precision,stop_limit)
    
    
    

# TESTING


#print(calculating_markers("BTCUSDT", "Binance", "5m", 1, 3, 0.8, 0.5,0.7, 1.0, 50, "LONG").get_stop_limit_price())

#print(calculating_markers("BTCUSDT", "Binance", "5m", 1, 3, 0.8, 0.5,0.7, 1.0, 50, "SHORT").tradable_funds())