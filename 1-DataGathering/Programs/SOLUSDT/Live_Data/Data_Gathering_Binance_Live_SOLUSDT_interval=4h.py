from sys import path

path.append("1-DataGathering/Programs")
from Data_Gathering_Binance_Live_LEGACY import run

#interval
interval = "4h"

#Run program
run("SOLUSDT", "Binance", interval)

    