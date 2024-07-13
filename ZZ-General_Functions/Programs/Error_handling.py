### This file handles different errors that might occur in the program

from time import sleep
import sqlite3


class Handling_Error:
    # Initialising Error
    def __init__(self, Error):
        self.Error = Error

    # No data table Error handling
    def No_Data_Table_Error(self):
        if sqlite3.OperationalError == type(self.Error):
            # print("W")
            sleep(30) # Wait 30 seconds so the program has enough time to have deleted the file which has the error

        else: pass
            #print("L")
            



""" TEST """

#Variables
'''
try:
    current_data("BTCUSDT", "Binance", "5m")
except Exception as Error: 
    print(type(Error))

    main = Handling_Error(Error)
    main.No_Data_Table_Error()'''
        