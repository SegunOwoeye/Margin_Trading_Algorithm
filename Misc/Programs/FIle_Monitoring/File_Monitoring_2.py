from sys import path


path.append("Misc/Programs")
path.append("0-Settings/Program_Files/Misc/")
from File_Monitoring_Legacy import run
from read_config import run as config # type: ignore


# DataGathering

trading_pairs = config()["application_settings"]["pair_list"]

path_list = []
for i in range(len(trading_pairs)):
    file_path = f"2-DataProcessing/data_gathered/{trading_pairs[i]}_data"
    
    path_list.append(file_path)
    

run(path_list)
