#THIS PYTHON FILE CREATES Live Balanes for Real Traing Environment

#IMPORTS
from os.path import exists, join, isfile
from os import listdir



# Creates trading pair specific demo account balance files
def live_balances(trading_pair, Exchange, db_name, Override = False):
    #Create Python File
    for p in range(len(trading_pair)):

        file_directory =  f"3-AccountBalance/Programs/{trading_pair[p]}/"
        python_file = f"{file_directory}Live_Account_Balance_Legacy_{trading_pair[p]}.py"

        if exists(python_file) == True and Override == False: #If python file exists do nothing and doesn't need to be overided
            pass
        else: # Creates new files if python doesn't exists
            #Creates python file for indicators across specified time intervals
            file_contents = f"""from sys import path

path.append("3-AccountBalance/Programs")
from Live_Account_Balance_Legacy import run

# Variables
trading_pair = "{trading_pair[p]}"
exchange_name = "{Exchange}"
db_name = "{db_name}"

run(trading_pair, exchange_name, db_name)

                """

            f = open(python_file, "a")
            f.write(file_contents)
            f.close()

            print(f"{python_file} file created")







#Variables
trading_pair = ["USDT", "ETH", "ARB", "BTC"]
#trading_pair = ["BTCUSDT"]
Exchange = "Binance" 
db_name = "Live_Balance"



#Run program
live_balances(trading_pair, Exchange, db_name)