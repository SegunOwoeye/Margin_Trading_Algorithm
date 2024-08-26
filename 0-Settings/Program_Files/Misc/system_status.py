import streamlit as st
import os 
import subprocess
from time import sleep 
import sqlite3

def bot_status_checker(file_name):
    sleep(5)
    while 1:
        connection = sqlite3.connect(file_name)
        cursor = connection.cursor()
        cursor.execute("Select * FROM proc")
        list_check = cursor.fetchall()
        running_data = list_check[-1]
        connection.commit()
        #Closing the database
        connection.close()
        print(running_data[1])
        if running_data[1] == "T": #Terminate the programs
            for proc in processes:
                proc.terminate()
            break

        else: 
            sleep(1)
            pass

bot_status_checker(f"0-Settings/running_bot_programs.db")