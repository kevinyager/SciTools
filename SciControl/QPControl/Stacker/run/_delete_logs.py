#!/usr/bin/python3
import os
from pathlib import Path

source_dir = '../'
log_dirs = [
    '/stacker/logs/',
    '/stacker/logs_stacker/',
    '/stackerDeck/logs/',
    '/stackerHTTP/cgi-bin/logs/',
    ]


for log_dir in log_dirs:
    p = Path(source_dir+log_dir)
    print('Removing logfiles from {}'.format(p))
    p = p.resolve()
    #print('  i.e.: {}'.format(p))
    
    for logfile in p.glob('*.log'):
        print('    Deleting: {}'.format(logfile))
        os.remove(logfile)
