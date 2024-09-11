import os 
import sqlite3
from time import time, sleep, localtime
from signal import SIGTERM
import subprocess
from sys import path as sys_path

class restart_algo:
    # Initialising Variables
    def __init__(self, restart_time):
        self.restart_time = restart_time # Time is only checked in days

    # [1] Checks to see if it's yet time to restart the program
    def time_check(self):
        main_time_file_name = f"0-Run/RunTime_Tools/Data_Files/Main_program_timings.db"

        if os.path.exists(main_time_file_name):
            # Getting the most recent entry fromthe .db file
            connection = sqlite3.connect(main_time_file_name)
            cursor = connection.cursor()
            cursor.execute("Select * FROM times")       
            recent_entry = cursor.fetchall()[-1]
            # Gets time variables
            program_start_time = float(recent_entry[0]) 
            current_time = time()
            #Setting the last restart timestamp
            if recent_entry[1] == None:
                last_restart_timestamp = program_start_time
            else:
                last_restart_timestamp = float(recent_entry[1])
            # Setting the last restart datetime
            last_restart_datetime = localtime(last_restart_timestamp)
            last_restart_month = last_restart_datetime.tm_mon
            last_restart_year = last_restart_datetime.tm_year

            # Setting the current datetime
            current_datetime = localtime(current_time)
            current_month = current_datetime.tm_mon
            current_year = current_datetime.tm_year

            """ [2] Checks to see Certain wait conditions have been met | Returns 0 if False and 1 if True"""
            # [2.1] More than a x days have passed since the program has been updated
            if (current_time >= last_restart_timestamp + 60*60*24*self.restart_time):
                return 1
            # [2.2] It's a new month for the program
            elif (current_month != last_restart_month):
                return 1
            elif (current_year != last_restart_year):
                return 1
            else: # If conditions haven't been met return 0
                return 0

            # [2.3] It's a new month for the program

        else: pass

    # [2] Restarts the program if conditions are met
    def restart(self):
        # [2.1] Import variables
        check_time = self.time_check()
        
        # Checks to see if it's time torestart the program
        if check_time == 1: # Restart program
            # [2.2.1] Connect to Task Manager db file
            main_program_tasks = f"0-Run/RunTime_Tools/Data_Files/Task_Manager.db"
            connection = sqlite3.connect(main_program_tasks)
            cursor = connection.cursor()
            
            # [2.2.2] Loop through database of processes
            cursor.execute("Select * FROM Tasks")
            program_process_list = cursor.fetchall()
            connection.close() # Closing the database

            og_progrms_list = program_process_list.copy

            # [2.2.3] Filterng the list to remove essential processes from terminating
            filters = ["0-Run/RunTime_Tools/Restart_[Start(Main)].py"]
            captured_ls = []
            for n in range(len(filters)):
                try:
                    # Removal from main list
                    for i in range(len(program_process_list)):
                        if program_process_list[i][0] == filters[n]:
                            captured_ls.append(program_process_list[i])
                            del program_process_list[i]
                    

                except Exception as e:
                    pass
            
            # [2.2.4] Getting list of program names
            program_name_list = []
            for i in range(len(program_process_list)):
                program_name_list.append(program_process_list[i][0])


            # [2.2.5] Ending processes
            for i in range(len(program_process_list)):
                pid = program_process_list[i][1]
                os.kill(int(pid), SIGTERM)
            
            # [2.2.6] Restarting the processes
            #cursor.execute("DELETE FROM Tasks")
            os.remove(main_program_tasks) # Deleting old db file
            environment = ".venv\Scripts\python.exe" # For virtual environment #"python" - > Defaullt
            new_tasks_list = []
            # Starts the programs again
            for program in program_name_list:
                # Run the program using the subprocess module
                proc = subprocess.Popen([environment, program])
                new_tasks_list.append(proc)

            # [2.2.7] CREATES NEW DB FILE FOR PROGRAMS
            connection = sqlite3.connect(main_program_tasks) # Defining Connection and cursor
            cursor = connection.cursor()
            #Creating Table
            command1 = """CREATE TABLE IF NOT EXISTS
            Tasks(Process_Name TEXT, PID TEXT)"""
            cursor.execute(command1)

            # [2.2.7.1] Creating List of PIDs
            new_pid_ls = []
            for i in range(len(new_tasks_list)):
                new_pid_ls.append(new_tasks_list[i].pid)

            # [2.2.7.2] Adding essential programs back to the list of programs in Task Manager
            for i in range(len(captured_ls)):
                program_name_list.append(captured_ls[i][0])
                new_pid_ls.append(captured_ls[i][1])
            

            # [2.2.7.3] Adding information to the Task Manager db file
            for i in range(len(program_name_list)):
                cursor.execute(f"""INSERT INTO Tasks (Process_Name, PID) VALUES ("{program_name_list[i]}", "{new_pid_ls[i]}")""")

            connection.commit()     
            connection.close() #Closing the database 
            
        else:
            pass

        # Returning status of program depending on if it has been restarted or not
        if check_time == 1: # Program has been restarted
            return 1
        else: # Program HAS NOT been restarted
            return 0

    # [3] Documents restart timer
    def update_timer(self):
        restart_status = self.restart()
        
        # [3.1] Ammend update timer in db
        if restart_status == 1: 
            # [3.1.1] Opens database file
            main_time_file_name = f"0-Run/RunTime_Tools/Data_Files/Main_program_timings.db"
            connection = sqlite3.connect(main_time_file_name) #Defining Connection and cursor
            cursor = connection.cursor()

            # [3.1.2] Getting the recent time
            cursor.execute("Select * FROM times")       
            recent_entry = cursor.fetchall()[-1]
            program_start_time = recent_entry[0]

            # [3.1.3] Setting the update time
            current_timestamp = round(time())

            # [3.1.4] Updating the time in the database
            if recent_entry[1] == None:
                last_restart_timestamp = program_start_time #Setting the last restart timestamp
                update_db = (f"""UPDATE times SET Last_Updated="{current_timestamp}"
                            WHERE (Start_Timestamp = "{last_restart_timestamp}") """)

            else:
                last_restart_timestamp = (recent_entry[1]) #Setting the last restart timestamp  
                update_db = (f"""UPDATE times SET Last_Updated="{current_timestamp}"
                            WHERE (Last_Updated = "{last_restart_timestamp}") """)       

            cursor.execute(update_db)
            connection.commit()
            connection.close() #Closing the database

        else: # Do Nothing 
            pass

# Runs the fucnction
def run(restart_time, wait_time=10):
    while 1:
        try:
            main = restart_algo(restart_time)
            main.update_timer()
        except Exception as e:
            program_name = f"0-Run/RunTime_Tools/Restart_[Start(Main)].py"
            # RECORDING ERROR
            sys_path.append("00-Run_Log/Programs")
            from Log_Output import Record_Output
            Record_Output("", "Binance", e, program_name)
            
        sleep(wait_time)
        
'''
""" TESTING """
# [1] Declaring Variables
restart_time = 7

"""# [2] Run Functions
main = restart_algo(restart_time, wait_time=10)
#print(main.time_check())
main.update_timer()"""
'''



""" RUN PROGRAM"""
restart_time = 7
run(restart_time)