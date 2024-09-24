# [1] Import Library
from sys import path

# [2] Import Created Programs
path.append("8-Risk_Managment/Programs")
from Trailing_Stop_Loss import run
path.append("0-Settings/Program_Files/Misc")
from read_config import run as config # type: ignore

# [3] Setting Variables
trading_pair = "BTCUSDT"
exchange_name = "Binance"
flag = config()["application_settings"]['trading_environment']['flag'] # 0 LIVE | 1 DEMO
chart_interval = "5m"
db_name = "Strategy2_Orders"


# [4] Run Program
run(trading_pair, exchange_name, flag, chart_interval, db_name)