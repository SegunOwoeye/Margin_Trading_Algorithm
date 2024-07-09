from sys import path

path.append("2-DataProcessing/Programs")
from Average_True_Range_Legacy import run

#Interval
chart_interval = "15m"
#Limit
indicator_interval = 14


run("BTCUSDT", "Binance", chart_interval, indicator_interval)

                        