from sys import path


path.append("Misc/Programs")
from File_Monitoring_Legacy import run


# DataGathering

trading_pairs = ["BTCUSDT"] #, "ETHUSDT"]

path_list = []
for i in range(len(trading_pairs)):
    file_path = f"5-Trade_Monitoring/data_gathered/{trading_pairs[i]}_data"
    
    path_list.append(file_path)
    

run(path_list)
