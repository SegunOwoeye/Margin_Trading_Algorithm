import pandas as pd
import vectorbt as vbt

# Assume you have a pandas DataFrame 'df' with your trading data
df = pd.read_csv('6-DynamicBacktesting/data_gathered/BTCUSDT/raw_output5m.csv', index_col='open_time', parse_dates=['open_time'])

# Calculate William's Fractals
fractals = vbt.indicators.WilliamsFractals.run(df['close'])

# Create a VectorBT portfolio
portfolio = vbt.Portfolio.from_df(df, cash=10000)

# Create a strategy based on the fractals
entries = fractals.fractal_high.entries
exits = fractals.fractal_low.exits

strat = portfolio.from_signals(entries, exits)

# Run the backtest
strat.run()

# Print the backtest results
print(strat.stats())