from sys import path

path.append("2-DataProcessing/Programs")
from Relative_Strength_Indicator_Legacy import run

#Interval
chart_interval = "1d"
#Limit
indicator_interval = 12


run("ARBUSDT", "Binance", chart_interval, indicator_interval)

                        