from sys import path


path.append("Misc/Programs")
from File_Monitoring_Legacy import run
path.append("")


# DataGathering

trading_pairs = ["BTCUSDT"] #, "ETHUSDT"]

path_list = []
for i in range(len(trading_pairs)):
    file_path = f"2-DataProcessing/data_gathered/{trading_pairs[i]}_data"
    
    path_list.append(file_path)
    

run(path_list)
