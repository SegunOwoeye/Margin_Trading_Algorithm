from sys import path

path.append("1-DataGathering/Programs")
from Data_Gathering_Binance_Historical_LEGACY import run

#interval
interval = "1d"
#Limit
limit = 1000

#Run program
run("ARBUSDT", "Binance", interval, limit)

    