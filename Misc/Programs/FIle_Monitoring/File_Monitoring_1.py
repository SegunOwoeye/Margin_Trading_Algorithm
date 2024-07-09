from sys import path


path.append("Misc/Programs")
from File_Monitoring_Legacy import run


# DataGathering

trading_pairs = ["BTCUSDT"] #, "ETHUSDT"]

path_list = []
for i in range(len(trading_pairs)):
    file_path = [f"1-DataGathering/data_gathered/{trading_pairs[i]}_data/Live_Data", 
            f"1-DataGathering/data_gathered/{trading_pairs[i]}_data/Historical_Klines"]
    
    path_list.append(file_path)
    

run(path)


