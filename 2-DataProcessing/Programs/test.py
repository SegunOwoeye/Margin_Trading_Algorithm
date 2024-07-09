from time import localtime, sleep, strftime

def wait_for_next_interval():
  """
  This function pauses the script execution until the next 5-minute interval starting at 00.
  """
  current_time = localtime()
  minutes_past = current_time.tm_min
  seconds_past = current_time.tm_sec

  # Calculate the number of seconds to wait until the next 5-minute interval
  wait_time = (5 - minutes_past % 5) * 60 - seconds_past

  # Pause execution for the calculated wait time
  sleep(wait_time)

while True:
  # Your script logic here
  print("Executing script logic at", strftime("%H:%M:%S"))

  # Wait for the next 5-minute interval before continuing
  wait_for_next_interval()