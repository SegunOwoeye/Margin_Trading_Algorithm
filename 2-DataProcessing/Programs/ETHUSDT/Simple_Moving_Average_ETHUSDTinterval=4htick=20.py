from sys import path

path.append("2-DataProcessing/Programs")
from Simple_Moving_Average_Legacy import run

#Interval
chart_interval = "4h"
#Limit
indicator_interval = 20


run("ETHUSDT", "Binance", chart_interval, indicator_interval)

                        