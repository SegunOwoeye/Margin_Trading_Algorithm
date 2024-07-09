from sys import path

path.append("2-DataProcessing/Programs")
from Simple_Moving_Average_Legacy import run

#Interval
chart_interval = "1d"
#Limit
indicator_interval = 45


run("BTCUSDT", "Binance", chart_interval, indicator_interval)

                        