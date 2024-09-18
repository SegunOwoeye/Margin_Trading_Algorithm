from tqdm import tqdm
import time
def long_running_task():
    for i in tqdm(range(100)):
        time.sleep(0.1)  # Simulate a 0.1-second task

long_running_task()
