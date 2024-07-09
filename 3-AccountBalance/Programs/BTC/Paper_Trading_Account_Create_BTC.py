from sys import path


path.append("3-AccountBalance/Programs")
from Paper_Trading_Account_Create_Legacy import run

#interval
balance = 5

#Run program
run("BTC", "Binance", "Demo_Balance", balance)
