# THIS FILE CREATES FILES FOR MONITORING TRADES

# Imports
from os.path import exists

# Main Function
class Create_Trade_Monitoring_Files:
    # [1] Initialising Variables
    def __init__(self, trading_pair, exchange, flag, chart_intervals, Override=False):
        self.trading_pair = trading_pair
        self.exchange = exchange
        self.flag = flag
        self.Override = Override

        # Turning chart interval into a list
        if isinstance(chart_intervals, list):
            self.chart_intervals = chart_intervals
        else:
            self.chart_intervals = [chart_intervals]

    
    # [2] Create Asset Precision Files
    def create_asset_precision(self):
        # Create Python File
        for p in range(len(self.trading_pair)):
            for t in range(len(self.chart_intervals)):
                file_directory =  f"5-Trade_Monitoring/Programs/{self.trading_pair[p]}/"
                python_file = f"{file_directory}asset_precision_{self.trading_pair[p]}.py"
                
                # Checks to see if the file already exists
                if exists(python_file) == True and self.Override == False: #If python file exists do nothing and doesn't need to be overided
                    pass
                else: # Creates new files if python doesn't exists
                    #Creates python file for indicators across specified time intervals
                    file_contents = f"""from sys import path

path.append("5-Trade_Monitoring/Programs")
from asset_precision_Legacy import run

# Run program
run("{self.trading_pair[p]}")

                        """
                    f = open(python_file, "w")
                    f.write(file_contents)
                    f.close()

                    #print(f"{python_file} file created")

    
    # [3] Create HIR Files
    def create_HIR_files(self):
        # Create Python File
        for p in range(len(self.trading_pair)):
            for t in range(len(self.chart_intervals)):
                file_directory =  f"5-Trade_Monitoring/Programs/{self.trading_pair[p]}/"
                python_file = f"{file_directory}Hourly_Interest_Rate_{self.trading_pair[p]}.py"
                # Checks to see if the file already exists
                if exists(python_file) == True and self.Override == False: #If python file exists do nothing and doesn't need to be overided
                    pass
                else: # Creates new files if python doesn't exists
                    #Creates python file for indicators across specified time intervals
                    file_contents = f"""from sys import path

path.append("5-Trade_Monitoring/Programs")
from Hourly_Interest_Rate_Legacy import run

# Run program
run("{self.trading_pair[p]}")

                        """
                    f = open(python_file, "w")
                    f.write(file_contents)
                    f.close()

                    #print(f"{python_file} file created")





"""
#''' Testing '''
# Variables
trading_pair = ["BTCUSDT", "ETHUSDT"]
exchange = "Binance" 
flag = 1 
chart_intervals = "5m"
Override = False


# Run
main = Create_Trade_Monitoring_Files(trading_pair=trading_pair, exchange=exchange,
                                     flag=flag, chart_intervals=chart_intervals, Override=Override)

# main.create_asset_precision() # -> Working
# main.create_HIR_files() # -> Working


"""