import pandas as pd

from BTCUSDT.Strategy7_BTCUSDT_BT import bt_strategy7


class TPSL_Optimisation:
    # [1] Initialising Variables
    def __init__(self, trading_pair, chart_interval, flag, strategy):
        self.trading_pair = trading_pair
        self.chart_interval = chart_interval
        self.flag = flag
        self.strategy = strategy


    # [2] Runs the Analysis
    def run_analysis(self):
        # [2.1] Runs the analysis
        for i in range(len(trading_pair)):
            while True:
                if self.strategy == "Strategy7":
                    TPSL_Data = bt_strategy7(trading_pair=self.trading_pair, chart_interval=self.chart_interval, 
                                 flag=self.flag)
                break
            break 
        
        # Returning the TP SL data for Long and Short trades for the Strategies
        return TPSL_Data

    
    # [3] Optimising the TP and SL
    def point_optimisation(self):
        # [3.1] Trade Data
        data = self.run_analysis()
        long_data = data['long']
        short_data = data['short']

        # [3.2] Optimising the TP and SL for Short Trades
        df_short = pd.DataFrame(short_data)
        df_short_sorted = df_short.sort_values('Returns', ascending=False)
        
        # [3.2.1] Get the top 10 return points
        for i in range(10):
            try: # Tries to get the top 10, if not will go for a smaller pool
                top_10_short = df_short_sorted.head(10-i)
                break
            except:
                pass
            
        # Calculate the TP to SL ratio
        top_10_short['TP_SL_ratio'] = top_10_short['TP'] / top_10_short['SL']
        # Filter out entries with a ratio less than 0.5 (50%)
        top_10_short_filtered = top_10_short[top_10_short['TP_SL_ratio'] >= 0.5]

        # Sort the DataFrame by 'win rate' in descending order
        df_short_WR = top_10_short_filtered.sort_values('win rate', ascending=False)
        # Find the highest win rate
        highest_short_win_rate = df_short_WR['win rate'].max()
        # Filter the DataFrame for entries with the highest win rate
        highest_short_win_rate_entries = df_short_WR[df_short_WR['win rate'] == highest_short_win_rate]
        
        # [3.2.2] In the event there are multiple high WR BTs
        if len(highest_short_win_rate_entries) > 1:
            # Get Highest TP/SL ratio
            highest_short_TP_SL_ratio = highest_short_win_rate_entries['TP_SL_ratio'].max()
            highest_short_TPSL_ratio_entries = highest_short_win_rate_entries[highest_short_win_rate_entries['TP_SL_ratio'] == highest_short_TP_SL_ratio]
            short_tpsl_dict = highest_short_TPSL_ratio_entries
        else:
            short_tpsl_dict = highest_short_win_rate_entries
        
        # [3.2.3] Best Short TP and SL for the trade
        best_short_tpsl = {"TP": short_tpsl_dict['TP'].values[0], "SL": short_tpsl_dict['SL'].values[0]}
       


        # [3.3] Optimising the TP and SL for long Trades
        df_long = pd.DataFrame(long_data)
        df_long_sorted = df_long.sort_values('Returns', ascending=False)
        
        # [3.3.1] Get the top 10 return points
        for i in range(10):
            try: # Tries to get the top 10, if not will go for a smaller pool
                top_10_long = df_long_sorted.head(10-i)
                break
            except:
                pass
            
        # Calculate the TP to SL ratio
        top_10_long['TP_SL_ratio'] = top_10_long['TP'] / top_10_long['SL']
        # Filter out entries with a ratio less than 0.5 (50%)
        top_10_long_filtered = top_10_long[top_10_long['TP_SL_ratio'] >= 0.5]

        # Sort the DataFrame by 'win rate' in descending order
        df_long_WR = top_10_long_filtered.sort_values('win rate', ascending=False)
        # Find the highest win rate
        highest_long_win_rate = df_long_WR['win rate'].max()
        # Filter the DataFrame for entries with the highest win rate
        highest_long_win_rate_entries = df_long_WR[df_long_WR['win rate'] == highest_long_win_rate]
        
        # [3.3.2] In the event there are multiple high WR BTs
        if len(highest_long_win_rate_entries) > 1:
            # Get Highest TP/SL ratio
            highest_long_TP_SL_ratio = highest_long_win_rate_entries['TP_SL_ratio'].max()
            highest_long_TPSL_ratio_entries = highest_long_win_rate_entries[highest_long_win_rate_entries['TP_SL_ratio'] == highest_long_TP_SL_ratio]
            long_tpsl_dict = highest_long_TPSL_ratio_entries
        else:
            long_tpsl_dict = highest_long_win_rate_entries
        
        # [3.3.3] Best long TP and SL for the trade
        best_long_tpsl = {"TP": long_tpsl_dict['TP'].values[0], "SL": long_tpsl_dict['SL'].values[0]}
        
        
        
        return {"long": best_long_tpsl, "short": best_short_tpsl}


"""
'''PARAMETERS'''
#STANDARD PARAMS
trading_pair = ["BTCUSDT", "ETHUSDT"]#"ETHUSDT"]
chart_interval = "1h"
flag = "optimise: TP/SL"
strategy = "Strategy7"


# RUN
main = TPSL_Optimisation(trading_pair=trading_pair, chart_interval=chart_interval, flag=flag,
                         strategy=strategy)

# print(main.run_analysis()) # -> Working
print(main.point_optimisation()) # -> Working

"""