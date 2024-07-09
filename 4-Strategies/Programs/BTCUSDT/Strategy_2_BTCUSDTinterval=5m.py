from sys import path


path.append("4-Strategies/Programs")
from Strategy_2_Legacy import run

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
L_TP = 0.8
S_TP = 0.5
L_SL = 0.7
S_SL = 1.0
flag = 1
tradeable_fund_Percentage = 50

#Run program

run(trading_pair, exchange_name, chart_interval, emaL1_interval, emaL2_interval, emaL3_interval,
             emaS1_interval, emaS2_interval, emaS3_interval, rsi_interval, leverage, L_TP, S_TP, 
             L_SL, S_SL, flag, tradeable_fund_Percentage)