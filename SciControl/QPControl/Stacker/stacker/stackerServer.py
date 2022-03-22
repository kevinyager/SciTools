#!/usr/bin/python3
from Stacker import *
print('Stacker version {}'.format(STACKER_VERSION))


AUTH='Cah2zawipu3Gohw2eFo1aec4ohPhah8u' # Authentication token
common = Common(logdir='./logs_stacker/', log_verbosity=1)

stacker = Stacker(name='StackerServer', mode='testing', authentication_token=AUTH, common=common, connect_PI=True, connect_Instec=True, verbosity=4, log_verbosity=1)
sam = stacker.sam
cam = stacker.cam
stmp = stacker.stmp


if __name__ == '__main__':
    stacker.server_listen() # Default is local connections
    #stacker.server_listen(ip='130.199.242.246', port=5551) # To enable remote control
