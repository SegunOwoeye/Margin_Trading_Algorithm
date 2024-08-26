#THIS PYTHON FILE CREATES INDICATORS ACROSS SPECIFIED TIMEFRAMES

#IMPORTS
from os.path import exists, join, isfile
from os import listdir

# Creates trading pair specific statistics files
def stat_indicators(trading_pair, Exchange, Time_Interval, SA_Interval, file_name, Override = False):
    #Create Python File
    for i in range(len(Time_Interval)):
        for p in range(len(trading_pair)):
            file_directory =  f"2-DataProcessing/Programs/{trading_pair[p]}/"
            python_file = file_directory + file_name + "_" + trading_pair[p] + "interval=" + Time_Interval[i] + ".py"

            if exists(python_file) == True and Override == False: #If python file exists do nothing and doesn't need to be overided
                pass
            else: # Creates new files if python doesn't exists

                #Creates python file for indicators across specified time intervals
                file_contents = f"""from sys import path

path.append("2-DataProcessing/Programs")
from {file_name}_Legacy import run

#Interval
chart_interval = "{Time_Interval[i]}"
#Limit
indicator_interval = {SA_Interval}


run("{trading_pair[p]}", "{Exchange}", chart_interval, indicator_interval)

                        """

                f = open(python_file, "a")
                f.write(file_contents)
                f.close()

                print(f"{python_file} file created")

# Creates trading pair specific technical indicator files
def TA_indicators(trading_pair, Exchange, Time_Interval, TA_Interval, TA_file_names, Override = False):
    #Create Python File
    for i in range(len(Time_Interval)):
        for p in range(len(trading_pair)):
            for t in range(len(TA_file_names)):
                for l in range(len(TA_Interval)):
                    file_directory =  f"2-DataProcessing/Programs/{trading_pair[p]}/"
                    #python_file = file_directory + TA_file_names[t] + "_" + trading_pair[p] + "interval=" + Time_Interval[i] + ".py"
                    #FOR Intervals such as SMA 10, 20, 30
                    python_file = file_directory + TA_file_names[t] + "_" + trading_pair[p] + "interval=" + Time_Interval[i] + "tick="+ str(TA_Interval[l]) +".py"

                    if exists(python_file) == True and Override == False: #If python file exists do nothing and doesn't need to be overided
                        pass
                    else: # Creates new files if python doesn't exists

                        #Creates python file for indicators across specified time intervals
                        file_contents = f"""from sys import path

path.append("2-DataProcessing/Programs")
from {TA_file_names[t]}_Legacy import run

#Interval
chart_interval = "{Time_Interval[i]}"
#Limit
indicator_interval = {TA_Interval[l]}


run("{trading_pair[p]}", "{Exchange}", chart_interval, indicator_interval)

                        """

                        f = open(python_file, "a")
                        f.write(file_contents)
                        f.close()

                        print(f"{python_file} file created")







#Variables
trading_pair = ["BTCUSDT", "ETHUSDT", "ARBUSDT"]
#trading_pair = ["BTCUSDT"]
Exchange = "Binance" 
Time_Interval = ["1m", "5m", "15m", "1h", "4h", "1d"] 
SA_Interval = 100
#TA_Interval = [20, 50, 100]
TA_Interval = [100, 90]

#File 
file_name = "Williams_Fractal_Cap"
TA_file_names = ["Williams_Fractal_Cap"]

#Run program
#stat_indicators(trading_pair, Exchange, Time_Interval, SA_Interval, file_name)
TA_indicators(trading_pair, Exchange, Time_Interval, TA_Interval, TA_file_names)

