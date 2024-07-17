from sys import path


path.append("Misc/Programs")
from File_Monitoring_Legacy import run


# DataGathering

trading_pairs = ["BTCUSDT"] #, "ETHUSDT"]

path_list = []
for i in range(len(trading_pairs)):
    live_path = f"1-DataGathering/data_gathered/{trading_pairs[i]}_data/Live_Data"
    historic_path = f"1-DataGathering/data_gathered/{trading_pairs[i]}_data/Historical_Klines"
    
    path_list.append(live_path)
    path_list.append(historic_path)
    

run(path)


