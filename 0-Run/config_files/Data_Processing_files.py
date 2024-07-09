#THIS PYTHON FILE CREATES INDICATORS ACROSS SPECIFIED TIMEFRAMES

#IMPORTS
from os.path import exists, join, isfile
from os import listdir

"""DOESN'T WORK BECAUSE ALL THE INDICATORS ARE TOO CUSTOM, MIGHT BE BETTER OFF CREATING AN APPLICATION TO BULK CHANGE SETTINGS FOR INDICATORS OR 
CREATE A FILE FOR STORING THESE INTERVALS"""

def create_indicators(trading_pair, Exchange, Time_Interval, SA_interval, TA_interval):
    #Gathers names of all legacy files
    file_directory = "2-DataProcessing/Programs/"
    relative_legacy_filename_list = []
    for filename in listdir(file_directory):
        f = join(file_directory, filename)
        if isfile(f):
            relative_legacy_filename_list.append(f)
        else:
            pass
    
    filename_list = []
    for i in range(len(relative_legacy_filename_list)):
        file = relative_legacy_filename_list[i].replace("_Legacy.py","").replace("2-DataProcessing/Programs/", "")
        filename_list.append(file)
    
    relative_filename_list = []
    for i in range(len(filename_list)):
        for n in range(len(trading_pair)):
            for p in range(len(Time_Interval)):
                python_file = f"2-DataProcessing/Programs/{trading_pair[n]}/{filename_list[i]}_{trading_pair[n]}interval={Time_Interval[p]}.py"
                relative_filename_list.append(python_file)
                
    #Creates python file for indicators across specified time intervals and orderbook
    for i in range(len(relative_filename_list)):  
        #Getting file data from file name
        p1d = relative_filename_list[i].replace("2-DataProcessing/Programs/","").replace(".py","")
        pair_char_position = p1d.find("/") # Finding the position of the first /, represents trading pair
        char_list_name = list(p1d) # Turning the characters into a list
        pair_from_fn = "".join(char_list_name[0:pair_char_position]) # Joins the list back together to get trading pair name from list
        Time_Interval_char_position = p1d.find("=") # Finding the position of the first =, represents time interval
        ti_from_fn = "".join(char_list_name[Time_Interval_char_position+1:]) # Joins the list back together to get time interval from list
        
        # GETS THE FILE NAME
        p2d = "".join(char_list_name[pair_char_position+1:])
        fn_char_position = p2d.rfind("_") # Finding the position of the last _, represents file name
        char_list_fn = list(p2d)
        fn_from_fn = "".join(char_list_fn[:fn_char_position])

        #Checks to see if the path exists:
        if exists(relative_filename_list[i]) == True: #Do nothing if the file exists
            pass

        else: #Create the data gathering files if they don't exist
            for n in range(len(trading_pair)):
                if trading_pair[n] == pair_from_fn:
                    file_contents = f"""from sys import path

path.append("2-DataProcessing/Programs")
from {fn_from_fn}_Legacy import run

#Levels
levels = {levels}

#Run program
run("{pair_from_fn}", "Binance", levels)

    """
        


    


   

#Variables
trading_pair = ["BTCUSDT", "ARBUSDT"]
Exchange = "Binance" 
Time_Interval = ["1m", "5m", "15m", "1h", "4h", "1d"] 
SA_interval = 1000 # Interval for statistical analysis
TA_interval = 14 # Interval for Technical Analysis



#Run program
create_indicators(trading_pair, Exchange, Time_Interval, 
                  SA_interval, TA_interval)