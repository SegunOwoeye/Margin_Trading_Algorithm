from sys import path

path.append("2-DataProcessing/Programs")
from Simple_Moving_Average_Legacy import run

#Interval
chart_interval = "5m"
#Limit
indicator_interval = 50


run("BTCUSDT", "Binance", chart_interval, indicator_interval)

                        