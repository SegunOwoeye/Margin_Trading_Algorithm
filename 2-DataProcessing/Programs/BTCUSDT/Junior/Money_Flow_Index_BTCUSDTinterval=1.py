from sys import path

path.append("2-DataProcessing/Programs")
from Money_Flow_Index_Legacy import run

#Interval
chart_interval = 1
#Limit
indicator_interval = 14


run("BTCUSDT", "ByBit", chart_interval, indicator_interval)

