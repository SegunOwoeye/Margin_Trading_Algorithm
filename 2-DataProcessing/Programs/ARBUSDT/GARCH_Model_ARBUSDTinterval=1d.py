from sys import path

path.append("2-DataProcessing/Programs")
from GARCH_Model_Legacy import run

#Interval
chart_interval = "1d"
#Limit
indicator_interval = 1000


run("ARBUSDT", "Binance", chart_interval, indicator_interval)

                        