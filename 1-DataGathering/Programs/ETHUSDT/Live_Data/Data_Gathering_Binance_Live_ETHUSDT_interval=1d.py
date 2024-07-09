from sys import path

path.append("1-DataGathering/Programs")
from Data_Gathering_Binance_Live_LEGACY import run

#interval
interval = "1d"

#Run program
run("ETHUSDT", "Binance", interval)

    