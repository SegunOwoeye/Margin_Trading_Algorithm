from sys import path

path.append("2-DataProcessing/Programs")
from Exponential_Moving_Average_Legacy import run

#Interval
chart_interval = "1m"
#Limit
indicator_interval = 100


run("ETHUSDT", "Binance", chart_interval, indicator_interval)

                        