import os, subprocess
import time, datetime

# Output the name of the current focused window (updates
# as you move the mouse around).
    

def window_name_loop(wait_time_min=0.05, wait_time_max=0.1):
    
    last_name = ""
    
    while True:
        
        #original_window_id = int(subprocess.check_output('xdotool getwindowfocus', shell=True))
        window_name = subprocess.check_output('xdotool getwindowfocus getwindowname', shell=True)
        window_name = window_name.decode('utf-8').strip()
        
        if window_name!=last_name:
            last_name = window_name
            wait_time = wait_time_min
            
            time_txt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            print(u'{} : {}'.format(time_txt, window_name))
            
        else:
            wait_time = wait_time_max
        time.sleep(wait_time)


window_name_loop()

