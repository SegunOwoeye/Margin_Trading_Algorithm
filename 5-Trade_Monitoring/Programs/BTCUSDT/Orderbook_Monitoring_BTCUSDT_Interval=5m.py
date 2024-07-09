from sys import path


path.append("5-Trade_Monitoring/Programs")
from Orderbook_Monitoring_Legacy import run


#Variables
trading_pair = "BTCUSDT"
exchange_name = "Binance"
flag = 1 # 0 LIVE | 1 DEMO
chart_interval = "5m"
db_name = "Strategy2_Orders"

# Run Program
run(trading_pair, exchange_name, flag, chart_interval, db_name)
