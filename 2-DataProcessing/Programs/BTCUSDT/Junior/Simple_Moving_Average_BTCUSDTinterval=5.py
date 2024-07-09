from sys import path

path.append("2-DataProcessing/Programs")
from Simple_Moving_Average_Legacy import run

#Interval
chart_interval = 5
#Limit
indicator_interval = 14
#Database Name
db_name = "SMA"

run("BTCUSDT", "ByBit", chart_interval, indicator_interval, db_name)