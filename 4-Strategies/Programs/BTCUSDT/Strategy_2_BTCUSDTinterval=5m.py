from sys import path


path.append("4-Strategies/Programs")
path.append("0-Settings/Program_Files/Misc/")
from Strategy_2_Legacy import run
from read_config import run as config # type: ignore

# Defining Variables
trading_pair = "BTCUSDT"
exchange_name = "Binance"
chart_interval = "5m"
emaL1_interval = 20
emaL2_interval = 50
emaL3_interval = 100
emaS1_interval = 15
emaS2_interval = 45
emaS3_interval = 90
rsi_interval = 6
leverage = 3 
L_TP = 1.6
S_TP = 0.9
L_SL = 0.7
S_SL = 0.6
flag = config()["application_settings"]['trading_environment']['flag']
tradeable_fund_Percentage = 50

#Run program

run(trading_pair, exchange_name, chart_interval, emaL1_interval, emaL2_interval, emaL3_interval,
             emaS1_interval, emaS2_interval, emaS3_interval, rsi_interval, leverage, L_TP, S_TP, 
             L_SL, S_SL, flag, tradeable_fund_Percentage)