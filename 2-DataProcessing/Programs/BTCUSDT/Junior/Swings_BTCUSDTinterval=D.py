from sys import path

path.append("2-DataProcessing/Programs")
from Swings_Legacy import run

#Interval
chart_interval = "D"
#Limit
indicator_interval = 20
#Database Name
db_name = "Swings"

run("BTCUSDT", "ByBit", chart_interval, indicator_interval, db_name)