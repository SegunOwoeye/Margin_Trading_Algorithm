from sys import path

path.append("2-DataProcessing/Programs")
from Williams_Fractal_Cap_Legacy import run

#Interval
chart_interval = "1h"
#Limit
indicator_interval = 100


run("ETHUSDT", "Binance", chart_interval, indicator_interval)

                        