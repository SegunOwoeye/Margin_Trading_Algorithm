from sys import path

path.append("2-DataProcessing/Programs")
from Average_True_Range_Legacy import run

#Interval
chart_interval = "D"
#Limit
indicator_interval = 14


run("BTCUSDT", "ByBit", chart_interval, indicator_interval)

