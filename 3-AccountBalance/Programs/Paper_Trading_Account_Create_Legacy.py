from datetime import datetime
from os.path import exists
import sqlite3

#CREATES A DATABASE FILE - WORKING
def creating_db_file(trading_pair, exchange_name, db_name):    
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y")
    ###BELOW NEEDS TO BE EDITED
    file_name = f"3-AccountBalance/data_gathered/{trading_pair}_data/" + str(date) + exchange_name + trading_pair + str(db_name) + "_data.db"
    f = open(file_name, "x")
    
    #Defining Connection and cursor
    connection = sqlite3.connect(file_name)
    cursor = connection.cursor()

    #Creating Current exchange_tag balance table
    command1 = f"""CREATE TABLE IF NOT EXISTS
    account_balance(time TEXT, Balance FLOAT)"""

    cursor.execute(command1)
    connection.commit()

    #Closing the database
    connection.close()

#ADDS FAKE ASSET TO ACCOUNT TO PAPER TRADE WITH
def add_balance(trading_pair, exchange_name, db_name, balance):
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y")
    ###BELOW NEEDS TO BE EDITED
    file_name = f"3-AccountBalance/data_gathered/{trading_pair}_data/" + str(date) + exchange_name + trading_pair + str(db_name) + "_data.db"
    
    connection = sqlite3.connect(file_name)
    cursor = connection.cursor()

    current_time = (datetime.now())
    formatted_time = str(current_time.strftime('"%H:%M:%S"'))
    cursor.execute(f"""INSERT INTO account_balance (time, Balance) VALUES ({formatted_time}, {float(balance)})""")

    connection.commit()
    connection.close() #Closing the database

#Creates paper trading account and adds a balance to it
def create_account(trading_pair, exchange_name, db_name, balance):
    creating_db_file(trading_pair, exchange_name, db_name)
    add_balance(trading_pair, exchange_name, db_name, balance)


def run(trading_pair, exchange_name, db_name, balance):
    
    try: 
        date_and_time = (datetime.now())
        date = date_and_time.strftime("%b%d%y")
        file_name = file_name = f"3-AccountBalance/data_gathered/{trading_pair}_data/" + str(date) + exchange_name + trading_pair + str(db_name) + "_data.db"
        if exists(file_name) == True: #Does nothing
            pass
        else: #Create New paper Trading Account
            #print(file_name)
            create_account(trading_pair, exchange_name, db_name, balance)
    except Exception as e:
        print(f"3-AccountBalance/Programs/{trading_pair}/Paper_Trading_Account_create_{trading_pair}.py has error: " + str(e))
    
#(run("USDT", "Binance", "Demo_Balance", 10000.00))




