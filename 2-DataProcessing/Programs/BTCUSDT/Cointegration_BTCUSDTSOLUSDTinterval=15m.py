from sys import path

path.append("2-DataProcessing/Programs")
from Cointegration_Legacy import run

base_pair = "BTCUSDT"
trading_pairs = ['BTCUSDT', 'SOLUSDT']
exchange_name = "Binance"
chart_interval = "15m"


run(base_pair=base_pair, trading_pairs=trading_pairs,exchange_name=exchange_name, chart_interval=chart_interval)

                        