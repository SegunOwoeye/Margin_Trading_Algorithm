from sys import path


path.append("1-DataGathering/Programs")
from Data_Gathering_Binance_Orderbook_LEGACY import run

#interval
levels = 5

#Run program
run("BTCUSDT", "Binance", levels)