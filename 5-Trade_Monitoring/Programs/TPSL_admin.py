# Standard Import Library
import polars as pl
from datetime import datetime
from time import sleep




class admin:
    # [1] Initialising Variables
    def __init__(self):
            self.db_name = "5-Trade_Monitoring/data_gathered/TPSL_database.xlsx"



    # [2] Create TPSL database
    def create_db(self):
        # [2.1] Create data headers
        data = {"trading_pair": [""],
                "strategy": [""],
                "interval": [""],
                "LTP": [""],
                "STP": [""],
                "LSL": [""],
                "SSL": [""],
                "TFP": [""], # Tradable Fund Percentage: 50 %
                "date_updated": [""]        
                }
                
        # Create db
        df = pl.DataFrame(data)
        print(df)
        df.write_excel(self.db_name)

    # [3] GET TPSL data
    def get_tpsl_data(self, trading_pair: str, strategy: str, interval: str):
        # [3.1] Importing Data from excel database
        df = pl.read_excel(self.db_name)
        
        # [3.2] Filtering through db to get data
        filtered_df = df.filter(
            (pl.col("trading_pair") == trading_pair) &
            (pl.col("strategy").cast(pl.Utf8) == strategy) &
            (pl.col("interval") == interval)
        )    

        # [3.3] Returning the df
        if filtered_df.height > 0:  # Check if any rows match
            data = {
                    "LTP": filtered_df.select("LTP").item(),
                    "STP": filtered_df.select("STP").item(),
                    "LSL": filtered_df.select("LSL").item(),
                    "SSL": filtered_df.select("SSL").item(),
                    "TFP": filtered_df.select("TFP").item(),
                        }
            
            return data
            #return (filtered_df.select(["LTP", "STP", "LSL", "SSL"]).row(0)) 
        else:
            return None    


        

"""
# Variables

trading_pair = "ETHUSDT"
strategy = "7"
interval = "1h"

# Run function
main = admin()
# main.create_db() # -> Working
print(main.get_tpsl_data(trading_pair=trading_pair, strategy=strategy, interval=interval))"""