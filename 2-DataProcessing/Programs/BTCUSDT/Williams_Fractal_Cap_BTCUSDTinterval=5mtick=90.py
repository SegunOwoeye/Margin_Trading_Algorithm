from sys import path

path.append("2-DataProcessing/Programs")
from Williams_Fractal_Cap_Legacy import run

#Interval
chart_interval = "5m"
#Limit
indicator_interval = 90


run("BTCUSDT", "Binance", chart_interval, indicator_interval)

                        