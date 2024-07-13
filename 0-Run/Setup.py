from sys import path

"""TRADING PAIR LIST"""
#pair_list = ["BTCUSDT"]

path.append("01-Program_Setup")
from Folder_creation import create_program_folder, create_data_folder, create_Subfolder_folder

"""[1] CREATING FOLDERS FOR '1-DataGathering' """
def start_1(pair_list):

    for i in range(0,len(pair_list)):
        create_program_folder(pair_list[i], "1-DataGathering/Programs")
        create_data_folder(pair_list[i], "1-DataGathering/data_gathered", "_data")

    for n in range(0,len(pair_list)):
        #Data Folder
        create_Subfolder_folder(pair_list[n], "1-DataGathering/data_gathered", "Historical_Klines", "_data")
        create_Subfolder_folder(pair_list[n], "1-DataGathering/data_gathered", "Live_Data", "_data")

        #Program Folder
        create_Subfolder_folder(pair_list[n], "1-DataGathering/Programs", "Historical_Klines", "")
        create_Subfolder_folder(pair_list[n], "1-DataGathering/Programs", "Live_Data", "")


"""[2] CREATING FOLDERS FOR '2-DataProcessing' """
def start_2(pair_list):

    for i in range(0,len(pair_list)):
        create_program_folder(pair_list[i], "2-DataProcessing/Programs")
        create_data_folder(pair_list[i], "2-DataProcessing/data_gathered", "_data")


"""[3] CREATING FOLDERS FOR '3-AccountBalance' """
def start_3(pair_list):
    #Splitting up trading pairs into their individual Crypto Currencies
    individual_pair_list = []
    for i in range(len(pair_list)):
        individual_pair = pair_list[i].replace("USDT","")
        individual_pair_list.append(individual_pair)

    individual_pair_list.append('USDT')


    for i in range(0,len(individual_pair_list)):
        create_program_folder(individual_pair_list[i], "3-AccountBalance/Programs")
        create_data_folder(individual_pair_list[i], "3-AccountBalance/data_gathered", "_data")

"""[4] CREATING FOLDERS FOR '4-Strategies' """
def start_4(pair_list):
    for i in range(0,len(pair_list)):
        create_program_folder(pair_list[i], "4-Strategies/Programs")
        create_data_folder(pair_list[i], "4-Strategies/data_gathered", "_data")

"""[5] CREATING FOLDERS FOR '5-Trade_Monitoring"""
def start_5(pair_list):
    for i in range(0,len(pair_list)):
        create_program_folder(pair_list[i], "5-Trade_Monitoring/Programs")
        create_data_folder(pair_list[i], "5-Trade_Monitoring/data_gathered", "_data")



#start_4(["BTCUSDT"])

#start_2(pair_list)



#check("ETHBTC", "ByBit")