from sys import path

path.append("1-DataGathering/Programs")
from Data_Gathering_Binance_Live_LEGACY import run

#interval
interval = "5m"

#Run program
run("ETHUSDT", "Binance", interval)

    