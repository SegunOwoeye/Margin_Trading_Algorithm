"""
THIS PROGRAM IS MEANT TO DO THE FOLLOWING:
- IF THE TIME IS WITHIN SECONDS OF A NEW time period, SUSPEND THE PROGRAM FOR 10 SECONDS
    -> Include this program at the end of every run cycle
"""

# Libraries
import time

# Main function
def Suspend_programs(interval="1h", wait=10, tolerance=5):
    c_time = time.localtime()
    hour_past = c_time.tm_hour
    minutes_past = c_time.tm_min
    seconds_past = c_time.tm_sec
    
    # Checks to see how long is left until the next the next time interval
    sleep_timer = interval.lower()
    if "m" in sleep_timer: 
        sleep_interval = int(sleep_timer.replace("m", ""))
        wait_time = (sleep_interval - minutes_past % sleep_interval) * 60 - seconds_past
    elif "h" in sleep_timer: 
        sleep_interval = int(sleep_timer.replace("h", ""))
        wait_time = (sleep_interval*60 - minutes_past % sleep_interval*60) * 60 - seconds_past
    elif "d" in sleep_timer: 
        sleep_interval = int(sleep_timer.replace("d", ""))
        wait_time = (24 - hour_past) * 3600 + (60 - minutes_past) * 60 - seconds_past
    else:
        pass


    # Verifies the time limit is within +/- tolerance seconds of the new time interval
    if "m" in sleep_timer: 
        if abs(60-wait_time) >= 60-tolerance:
            time.sleep(wait)
    elif "h" in sleep_timer: 
        if abs(60*60-wait_time) >= 60*60-tolerance:
            time.sleep(wait)
    elif "d" in sleep_timer: 
        if abs(60*60*24-wait_time) >= 60*60*24-tolerance:
            time.sleep(wait)

    #print(wait_time)

    
""" TESTING """

"""while 1:


    Suspend_programs(interval="1m")
    time.sleep(1)"""