from sys import path

path.append("2-DataProcessing/Programs")
from Exponential_Moving_Average_Legacy import run

#Interval
chart_interval = "15m"
#Limit
indicator_interval = 20


run("ARBUSDT", "Binance", chart_interval, indicator_interval)

                        