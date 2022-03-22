#!/usr/bin/python3
from Stacker import *
print('Stacker version {}'.format(STACKER_VERSION))

AUTH='Cah2zawipu3Gohw2eFo1aec4ohPhah8u' # Authentication token
common = Common(logdir='./logs/')
    
stacker = Stacker(name='StackerClient', mode='client', authentication_token=AUTH, common=common, verbosity=4, log_verbosity=3)
sam = stacker.sam
cam = stacker.cam
stmp = stacker.stmp



if __name__ == '__main__':
    stacker.client_connect_to_server()
    
    
