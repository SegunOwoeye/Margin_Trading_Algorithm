from sys import path

path.append("2-DataProcessing/Programs")
from Relative_Strength_Indicator_Legacy import run

#Interval
chart_interval = "4h"
#Limit
indicator_interval = 6


run("BTCUSDT", "Binance", chart_interval, indicator_interval)

                        