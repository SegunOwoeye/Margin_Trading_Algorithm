### This file handles different errors that might occur in the program

from time import sleep
import sqlite3


class Handling_Error:
    # Initialising Error
    def __init__(self, Error):
        self.Error = Error

    # No data table Error handling
    def No_Data_Table_Error(self, timer=30):
        if sqlite3.OperationalError == type(self.Error):
            # print("W")
            sleep(timer) # Wait 30 seconds so the program has enough time to have deleted the file which has the error

        else: pass
            #print("L")

    # Float division by Zero Error
    def div_by_zero_error(self):
        if ZeroDivisionError == type(self.Error):
            return 100
        else: pass

            



""" TEST """

#Variables
'''
try:
    lol = 1/0
    print(lol)
except Exception as Error: 
    #print(type(Error))

    main = Handling_Error(Error)
    print(main.div_by_zero_error())'''
        