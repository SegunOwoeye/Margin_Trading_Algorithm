#THIS PYTHON FILE CREATES INDICATORS ACROSS SPECIFIED TIMEFRAMES

#IMPORTS
from os.path import exists, join, isfile
from os import listdir

# Creates trading pair specific statistics files
def stat_indicators(trading_pair, Exchange, Time_Interval, SA_Interval, pairs_list, file_name, Override = False):
    #Create Python File
    for i in range(len(Time_Interval)):
        for p in range(len(trading_pair)):
            for l in range(len(pairs_list)):
                file_directory =  f"2-DataProcessing/Programs/{trading_pair[p]}/"
                python_file = f"{file_directory}{file_name}_{trading_pair[p]}{pairs_list[l][1]}interval={Time_Interval[i]}.py"
                if exists(python_file) == True and Override == False: #If python file exists do nothing and doesn't need to be overided
                    pass
                else: # Creates new files if python doesn't exists

                    #Creates python file for indicators across specified time intervals
                    file_contents = f"""from sys import path

path.append("2-DataProcessing/Programs")
from {file_name}_Legacy import run

base_pair = "{trading_pair[p]}"
trading_pairs = {pairs_list[l]}
exchange_name = "{Exchange}"
chart_interval = "{Time_Interval[i]}"


run(base_pair=base_pair, trading_pairs=trading_pairs,exchange_name=exchange_name, chart_interval=chart_interval)

                        """

                f = open(python_file, "a")
                f.write(file_contents)
                f.close()

                print(f"{python_file} file created")






#Variables
trading_pair = ["BTCUSDT"]
pairs_list = [["BTCUSDT", "ETHUSDT"], ["BTCUSDT", "SOLUSDT"], ["BTCUSDT", "XRPUSDT"]]
#trading_pair = ["BTCUSDT"]
Exchange = "Binance" 
Time_Interval = ["1m", "5m", "15m", "1h", "4h", "1d"] 
SA_Interval = 100

#File 
file_name = "Cointegration"

#Run program
stat_indicators(trading_pair, Exchange, Time_Interval, SA_Interval, pairs_list, file_name)

