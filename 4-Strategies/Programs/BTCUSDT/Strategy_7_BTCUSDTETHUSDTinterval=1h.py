# General Library Imports
from sys import path

# Custom Library Imports
path.append("4-Strategies/Programs")
path.append("0-Settings/Program_Files/Misc/")
from Strategy_7_Legacy import run
from read_config import run as config # type: ignore


# Variables
trading_pair_list = ["BTCUSDT", "ETHUSDT"] 
exchange_name = "Binance"
flag = config()["application_settings"]['trading_environment']['flag']
chart_interval = "1h"
leverage = 3
trade_type = "S"
L_TP = 0
S_TP = 0.9
L_SL = 0
S_SL = 1.5
tradeable_fund_Percentage = 50

# Run Function
run(trading_pair_list=trading_pair_list, exchange_name=exchange_name, flag=flag, 
                chart_interval=chart_interval, leverage=leverage, trade_type=trade_type, L_TP=L_TP,
                S_TP=S_TP, L_SL=L_SL, S_SL=S_SL, tradeable_fund_Percentage=tradeable_fund_Percentage)