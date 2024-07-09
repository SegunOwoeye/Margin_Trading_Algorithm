#THIS PYTHON FILE CREATES FILES FOR DATA GATHERING IN PYTHON BASED ON TRADING PAIR FROM THE LEGACY FILES

#IMPORTS
from os.path import exists

#Main Function
def create_data_gathering(trading_pair, Time_Interval, limit, levels):
    #Folder Names
    program_folders = ['Historical_Klines', 'Live_Data']

    file_names_H = [] #List of file names from historical data
    for n in range(len(trading_pair)): #Historical data and interval appendege
        for i in range(len(Time_Interval)):
            file_name_k = f"Data_Gathering_Binance_Historical_{trading_pair[n]}_interval={Time_Interval[i]}.py" #kline name
            file_names_H.append(file_name_k) 

    file_names_L = [] #List of file names from live data
    for n in range(len(trading_pair)): #Live data and interval appendege
        file_name_o = f"Data_Gathering_Binance_{trading_pair[n]}_Orderbook.py" # Orderbook name
        file_names_L.append(file_name_o)
        for i in range(len(Time_Interval)):
            file_name_k = f"Data_Gathering_Binance_Live_{trading_pair[n]}_interval={Time_Interval[i]}.py" #Kline name
            file_names_L.append(file_name_k)
    
    #List of Python file names
    file_names_list = file_names_H + file_names_L    

    #creates a list of relative filename
    filename_list = []

    for i in range(len(file_names_list)):
        #Getting file data from file name
        p1d = file_names_list[i].replace(".py","")
        p2d = p1d.replace("Data_Gathering_Binance_","")
        del_char_position1 = p2d.rfind("_") # Finding the position of last _
        p3d_list = list(p2d)
        p3d = "".join(p3d_list[:del_char_position1])
        del_char_position2 = p3d.find("_") # Finding the position of last _
        p4d_list = list(p3d)
        pair_from_fn = "".join(p4d_list[del_char_position2+1:])
        
        for p in range(len(trading_pair)):
            for n in range(len(program_folders)):
                if program_folders[n] == "Historical_Klines" and "Historical" in file_names_list[i] and trading_pair[p] == pair_from_fn: #Creates files for historical data
                    python_file = f"1-DataGathering/Programs/{trading_pair[p]}/{program_folders[n]}/{file_names_list[i]}"
                    filename_list.append(python_file)

                elif program_folders[n] == "Historical_Klines" and "Orderbook" in file_names_list[i]: #pass through uknown error
                    pass   
                    
                elif program_folders[n] == "Live_Data" and "Live" in file_names_list[i] and trading_pair[p] == pair_from_fn: #Creates files for live data
                    python_file = f"1-DataGathering/Programs/{trading_pair[p]}/{program_folders[n]}/{file_names_list[i]}"
                    filename_list.append(python_file)
                
                elif program_folders[n] == "Live_Data" and "Orderbook" in file_names_list[i] and trading_pair[p] == pair_from_fn: #Creates files for orderbook data
                    python_file = f"1-DataGathering/Programs/{trading_pair[p]}/{program_folders[n]}/{file_names_list[i]}"
                    filename_list.append(python_file)

                else:
                    pass
    
    
    #Creates python file for indicators across specified time intervals and orderbook
    for i in range(len(filename_list)):
        #Getting file data from file name
        p1d = filename_list[i].replace(".py","")
        p2d = p1d.replace("1-DataGathering/Programs/","")
        pair_char_position = p2d.find("/") # Finding the position of the first /, represents trading pair
        char_list_name = list(p2d) # Turning the characters into a list
        pair_from_fn = "".join(char_list_name[0:pair_char_position]) # Joins the list back together to get trading pair name from list
        Time_Interval_char_position = p2d.find("=") # Finding the position of the first =, represents time interval
        ti_from_fn = "".join(char_list_name[Time_Interval_char_position+1:]) # Joins the list back together to get time interval from list

        #Checks to see if the path exists:
        if exists(filename_list[i]) == True: #Do nothing if the file exists
            pass

        else: #Create the data gathering files if they don't exist
            #Checks to see if the filename is an orderbook or not
            for n in range(len(trading_pair)):
                if trading_pair[n] == pair_from_fn:

                    if "Orderbook" in filename_list[i]: #Orderbook
                        file_contents = f"""from sys import path

path.append("1-DataGathering/Programs")
from Data_Gathering_Binance_Orderbook_LEGACY import run

#Levels
levels = {levels}

#Run program
run("{pair_from_fn}", "Binance", levels)

    """

                        f = open(filename_list[i], "a")
                        f.write(file_contents)
                        f.close()

                    elif "Historical" in filename_list[i]: #Historical Kline
                        file_contents = f"""from sys import path

path.append("1-DataGathering/Programs")
from Data_Gathering_Binance_Historical_LEGACY import run

#interval
interval = "{ti_from_fn}"
#Limit
limit = {limit}

#Run program
run("{pair_from_fn}", "Binance", interval, limit)

    """

                        f = open(filename_list[i], "a")
                        f.write(file_contents)
                        f.close()

                    elif "Live" in filename_list[i]: #Live Kline
                        file_contents = f"""from sys import path

path.append("1-DataGathering/Programs")
from Data_Gathering_Binance_Live_LEGACY import run

#interval
interval = "{ti_from_fn}"

#Run program
run("{pair_from_fn}", "Binance", interval)

    """

                        f = open(filename_list[i], "a")
                        f.write(file_contents)
                        f.close()
                    
                    else:
                        pass

                else:
                    pass
               

#Run program
#create_data_gathering(["BTCUSDT","ARBUSDT"], ["1m", "5m", "15m", "1h", "4h", "1d"] , 1000, 5)