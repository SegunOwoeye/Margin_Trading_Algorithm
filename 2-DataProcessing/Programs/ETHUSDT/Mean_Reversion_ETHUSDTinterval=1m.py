from sys import path

path.append("2-DataProcessing/Programs")
from Mean_Reversion_Legacy import run

#Interval
chart_interval = "1m"
#Limit
indicator_interval = 100


run("ETHUSDT", "Binance", chart_interval, indicator_interval)

                        