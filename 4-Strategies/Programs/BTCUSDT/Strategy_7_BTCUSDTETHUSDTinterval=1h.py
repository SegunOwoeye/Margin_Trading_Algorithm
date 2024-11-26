# General Library Imports
from sys import path

# Custom Library Imports
path.append("4-Strategies/Programs")
path.append("0-Settings/Program_Files/Misc/")
from Strategy_7_Legacy import run
from read_config import run as config # type: ignore

# Get Custom TPSL Lib
path.append("5-Trade_Monitoring/Programs")
from TPSL_admin import admin



# Variables
trading_pair_list = ["BTCUSDT", "ETHUSDT"] 
exchange_name = "Binance"
flag = config()["application_settings"]['trading_environment']['flag']
chart_interval = "1h"
leverage = 3
trade_type = "S"

# TPSL Data
TPSL_data = admin().get_tpsl_data(trading_pair=trading_pair_list[1], strategy="7", interval=chart_interval)
L_TP = float(TPSL_data["LTP"])
S_TP = float(TPSL_data["STP"])
L_SL = float(TPSL_data["LSL"])
S_SL = float(TPSL_data["SSL"])
tradeable_fund_Percentage = float(TPSL_data["TFP"])

# Run Function
run(trading_pair_list=trading_pair_list, exchange_name=exchange_name, flag=flag, 
                chart_interval=chart_interval, leverage=leverage, trade_type=trade_type, L_TP=L_TP,
                S_TP=S_TP, L_SL=L_SL, S_SL=S_SL, tradeable_fund_Percentage=tradeable_fund_Percentage)