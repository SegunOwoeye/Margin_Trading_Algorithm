from sys import path

path.append("3-AccountBalance/Programs")
from Live_Account_Balance_Legacy import run

# Variables
trading_pair = "SOL"
exchange_name = "Binance"
db_name = "Live_Balance"

run(trading_pair, exchange_name, db_name)

                