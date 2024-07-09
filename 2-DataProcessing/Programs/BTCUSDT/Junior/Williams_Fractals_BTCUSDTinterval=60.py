from sys import path

path.append("2-DataProcessing/Programs")
from Williams_Fractals_Legacy import run

#Interval
chart_interval = 60
#Limit
indicator_interval = 2

run("BTCUSDT", "ByBit", chart_interval, indicator_interval)