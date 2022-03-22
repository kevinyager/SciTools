#!/usr/bin/env python3

#from keys_main import *
#from keys_apps import *
#from keys_beam import *
from keys_stacker import *

key_maps = [key_map_stacker_sam, key_map_stacker_stmp]
#key_maps = [key_map_stacker_sam, key_map_stacker_cam, key_map_stacker_stmp]
        

if __name__ == "__main__":
    #monitor_streamdecks(key_maps, reverse=True, monitor_window=True, verbosity=3)
    monitor = Monitor(key_maps)
    #monitor.names = { 'KWrite' : key_map_kwrite ,
                     #'Thunderbird' : key_map_thunderbird ,
                     #}
    monitor.monitor(reverse=False, monitor_window=False, window_idx=0, verbosity=4)
    
    
    
