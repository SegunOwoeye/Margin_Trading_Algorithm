from sys import path

path.append("2-DataProcessing/Programs")
from Williams_Fractals_Legacy import run

#Interval
chart_interval = "1h"
#Limit
indicator_interval = 3


run("BTCUSDT", "Binance", chart_interval, indicator_interval)

                        