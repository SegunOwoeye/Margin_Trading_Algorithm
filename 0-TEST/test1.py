trading_pairs = ["BTCUSDT", "ETHUSDT", "ARBUSDT"]

asset_pairs = []
for i in range(len(trading_pairs)):
    asset_name = trading_pairs[i].replace("USDT", "")
    asset_pairs.append(asset_name)

asset_pairs.append("USDT")
print(asset_pairs)