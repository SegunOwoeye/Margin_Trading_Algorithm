from sys import path


path.append("5-Trade_Monitoring/Programs")
from Orderbook_Monitoring_Legacy import run
path.append("0-Settings/Program_Files/Misc/")
from read_config import run as config # type: ignore


#Variables
trading_pair = "BTCUSDT"
exchange_name = "Binance"
flag = config()["application_settings"]['trading_environment']['flag'] # 0 LIVE | 1 DEMO
chart_interval = "5m"
db_name = "Strategy2_Orders"

# Run Program
run(trading_pair, exchange_name, flag, chart_interval, db_name)

