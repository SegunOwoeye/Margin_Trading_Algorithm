from sys import path

path.append("3-AccountBalance/Programs")
from Paper_Trading_Account_Create_Legacy import run

# Variables
trading_pair = "SOL"
exchange_name = "Binance"
db_name = "db_name"
balance = 100
strat_db_name = "Strategy2_Orders"
R_Trading_Pairs = "SOLUSDT"

run(trading_pair, exchange_name, db_name, balance, strat_db_name, R_Trading_Pairs)

                        