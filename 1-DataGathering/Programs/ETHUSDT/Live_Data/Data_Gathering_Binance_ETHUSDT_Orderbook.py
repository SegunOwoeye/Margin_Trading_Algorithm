from sys import path

path.append("1-DataGathering/Programs")
from Data_Gathering_Binance_Orderbook_LEGACY import run

#Levels
levels = 10

#Run program
run("ETHUSDT", "Binance", levels)

    