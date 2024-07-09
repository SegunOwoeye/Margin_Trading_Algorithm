from sys import path

path.append("3-AccountBalance/Programs")
from Paper_Trading_Account_Create_Legacy import run

# Balance
balance = 10000

#Run program
run("ARB", "Binance", "Demo_Balance", balance)

                        