from sys import path

path.append("2-DataProcessing/Programs")
from GARCH_Model_Legacy import run

#Interval
chart_interval = "1m"
#Limit
indicator_interval = 1000


run("ETHUSDT", "Binance", chart_interval, indicator_interval)

                        