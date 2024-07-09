from sys import path

path.append("2-DataProcessing/Programs")
from Relative_Strength_Indicator_Legacy import run

#Interval
chart_interval = "15m"
#Limit
indicator_interval = 6


run("ARBUSDT", "Binance", chart_interval, indicator_interval)

                        