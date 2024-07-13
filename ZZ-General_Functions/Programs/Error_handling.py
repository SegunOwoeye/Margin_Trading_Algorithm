### This file handles different errors that might occur in the program

from time import sleep

class Handling_Error:
    # Initialising Error
    def __init__(self, Error):
        self.Error = Error

    # No data table Error handling
    def No_Data_Table_Error(self):
        if "no such table:" in self.Error:
            sleep(30) # Wait 30 seconds so the program has enough time to have deleted the file which has the error
        else: pass



""" TEST """

#Variables

"""Error = "no such table in file"

main = Handling_Error(Error)
main.No_Data_Table_Error()"""
        