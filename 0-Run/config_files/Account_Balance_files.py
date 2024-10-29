# THIS PYTHON FILE CREATES Account Balances 

#IMPORTS
from sys import path as sys_path
sys_path.append("0-Settings/Program_Files/3-AcccountBalance/")

# Custom Imports
from Create_Live_Balances import live_balances # Live
from Create_Demo_Balances import demo_balances # Demo

# [1] Gather Balances
def Create_Trade_Balances(trading_pair, Override=False):
    # [1.1] Creating List of Assets with USDT removed
    base_asset = "USDT"
    asset_list = [asset.replace(base_asset, "") for asset in trading_pair] 
    asset_list.append(base_asset)

    # [1.2] Live Balances
    live_balances(asset_list, "Binance", "Live_Balance", Override)

    # [1.3] Demo Trading Balances
    demo_balances(trading_pair, "Binance", "db_name", Override)
    

    


#Create_Trade_Balances(["BTCUSDT", "ETHUSDT", "SOLUSDT"])