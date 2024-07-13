# This section take in the chart interval and converts it into time in seconds

# WORKING
def convert(chart_interval):
    if "m" in chart_interval: # Minutes
        chart_interval = float(chart_interval.replace("m", ""))
        time = chart_interval * 60
        return time
    elif "h" in chart_interval.lower(): # HOURS
        chart_interval = float(chart_interval.replace("h", ""))
        time = chart_interval * 60 * 60
        return time
    elif "d" in chart_interval.lower(): # DAYS
        chart_interval = float(chart_interval.replace("d", ""))
        time = chart_interval * 60 * 60 * 24
        return time




""" TEST """
'''
# Variables
chart_interval = "1d"

# RUN
print(convert(chart_interval))'''