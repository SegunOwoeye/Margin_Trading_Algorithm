import yfinance as yf

"""
LOOK AT CLUSTERING OF PRICE (MAYBE RETURNS) OF AN ASSET AT DIFFERENT LEVELS WITHIN THE DATA TO DETERMINE
"""



symbol = 'SOLUSDT'  # Note: yfinance might not support Binance-specific symbols

# Get historical data for the last 24 hours in 15-minute intervals
data = yf.download(symbol, period='24h', interval='15m')

# Extract closing prices
closing_prices = data['Close'].tolist()

# Print the closing prices
print("Closing prices for Solana in the last 24 hours (15-minute intervals):")
for price in closing_prices:
    print(price)