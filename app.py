import subprocess
import os
import time
from playsound import playsound

def run_script():
    try:
        filepath = os.path.abspath('scrapeemail.py')
        subprocess.run(['python',filepath], check=True)
    except subprocess.CalledProcessError as e:
        print("Error running script:", e)


if __name__ == "__main__":
    counter = 1
    while counter < 100:

        run_script()
        time.sleep(2)

        counter = counter + 1
        print(f"next run....  {counter}")
    
  