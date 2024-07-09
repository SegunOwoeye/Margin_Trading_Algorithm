from sys import path

path.append("2-DataProcessing/Programs")
from Exponential_Moving_Average_Legacy import run

#Interval
chart_interval = 15
#Limit
indicator_interval = 14
#Database Name
db_name = "EMA"

run("BTCUSDT", "ByBit", chart_interval, indicator_interval, db_name)