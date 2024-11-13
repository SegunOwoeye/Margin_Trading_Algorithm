from sys import path

path.append("2-DataProcessing/Programs")
from Cointegration_Legacy import run

base_pair = "BTCUSDT"
trading_pairs = ['BTCUSDT', 'ETHUSDT']
exchange_name = "Binance"
chart_interval = "5m"


run(base_pair=base_pair, trading_pairs=trading_pairs,exchange_name=exchange_name, chart_interval=chart_interval)

                        