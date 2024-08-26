#THIS PYTHON FILE CREATES Demo Balances to Paper Trade

#IMPORTS
from os.path import exists, join, isfile
from os import listdir



# Creates trading pair specific demo account balance files
def demo_balances(trading_pair, Exchange, db_name, Override = False):
    #Create Python File
    for p in range(len(trading_pair)):
        
        #Spliting Trading Pairs into individual symbols 
        if "USDT" in trading_pair[p]:
            pair1 = trading_pair[p].replace("USDT","")
            pair2 = "USDT"
            symbol_list = [pair1, pair2]
            for i in range(len(symbol_list)):

                file_directory =  f"3-AccountBalance/Programs/{symbol_list[i]}/"
                python_file = f"{file_directory}Paper_Trading_Account_Create_{symbol_list[i]}.py"

                if exists(python_file) == True and Override == False: #If python file exists do nothing and doesn't need to be overided
                    pass
                else: # Creates new files if python doesn't exists
                    # Setting Balances
                    if symbol_list[i] == "BTC":
                        balance = 5
                    elif symbol_list[i] == "ETH":
                        balance = 10
                    else:
                        balance = 10000

                    #Creates python file for indicators across specified time intervals
                    file_contents = f"""from sys import path

path.append("3-AccountBalance/Programs")
from Paper_Trading_Account_Create_Legacy import run

# Variables
trading_pair = "{symbol_list[i]}"
exchange_name = "{Exchange}"
db_name = "{db_name}"
balance = {balance}
strat_db_name = "Strategy2_Orders"
R_Trading_Pairs = "{trading_pair[p]}"

run(trading_pair, exchange_name, db_name, balance, strat_db_name, R_Trading_Pairs)

                        """

                    f = open(python_file, "a")
                    f.write(file_contents)
                    f.close()

                    print(f"{python_file} file created")







#Variables
trading_pair = ["BTCUSDT", "ETHUSDT", "ARBUSDT"]
#trading_pair = ["BTCUSDT"]
Exchange = "Binance" 
db_name = "Demo_Balance"



#Run program
#stat_indicators(trading_pair, Exchange, Time_Interval, SA_Interval, file_name)
demo_balances(trading_pair, Exchange, db_name)

