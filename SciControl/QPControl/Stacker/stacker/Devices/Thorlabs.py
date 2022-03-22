from BLEX.Base import *

#import os
#import time
from ctypes import *


class MotorThorlabs_Linear(Base):
    def __init__(self, SN, name='<MotorThorlabs_linear>', active=True, EncCnt=34304, **kwargs):
        super().__init__(name=name, **kwargs) # Base
        
        self.SN = SN
        self.active = active
        self.EncCnt = float(EncCnt)
        
        self.connect(self.SN)
        
        self.messageType = c_ushort()
        self.messageID = c_ushort()
        self.messageData = c_ulong()
        
    def connect(self, SN):
        
        # Connect to Kinesis DLL
        self.lib = cdll.LoadLibrary(r"C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.KCube.DCServo.dll")

        # Build device list
        self.lib.TLI_BuildDeviceList()
        
        # Set up serial number variable
        self.serialNumber = c_char_p( SN.encode() )
        
        # Set up device
        self.lib.CC_Open(self.serialNumber)
        #r = lib.CC_StartPolling(self.serialNumber, c_int(200)) # returns 1 (error)
        #print("return value: {}".format(r))
        
        self.lib.CC_EnableChannel(self.serialNumber)
        time.sleep(0.5)

        self.lib.CC_ClearMessageQueue(self.serialNumber)
        
        self.msg('Connected to Thorlabs')
        
        
    def get_message(self):
        
        self.lib.CC_GetNextMessage(self.serialNumber, byref(self.messageType), byref(self.messageID), byref(self.messageData))
        
        message_txt = 'CC_GetNextMessage: ID={}, Type={}, Data={}'.format(self.messageID.value, self.messageType.value, self.messageData.value)
        self.msg(message_txt, 5, 1)
        
        return self.messageData.value
         
        
    def get_position(self):
        
        self.lib.CC_RequestPosition(self.serialNumber)
        raw_pos = self.lib.CC_GetPosition(self.serialNumber)
        position = raw_pos/self.EncCnt
        self.msg('raw_pos = {}; position = {}'.format(raw_pos, position), 5, 2)
        
        return position
        
    
    def set_position(self, position, wait=False, waitTimeout=10):
        
        raw_pos = int(position*self.EncCnt)
        self.msg('target = {}; raw_pos = {}'.format(position, raw_pos), 5, 2)
    
        start_time = time.time()
        r = self.lib.CC_MoveToPosition(self.serialNumber, raw_pos)
        if r!=0:
            self.msg_error('CC_MoveToPosition return value: {}'.format(r), 1, 2)
    
        if wait:
            moved = False
            while(not moved):
                self.lib.CC_GetNextMessage(self.serialNumber, byref(self.messageType), byref(self.messageID), byref(self.messageData))
                if messageID.value == 1 and messageType.value == 2:
                    moved = True
                    self.msg("Move complete after {:.1f}s".format(time.time()-start_time), 5, 2)
                if (time.time()-start_time) > waitTimeout:
                    self.msg("Move taking longer than {:.1f}s".format(waitTimeout), 2, 2)
                    break
                
                
    def __del__(self):
        self.lib.CC_ClearMessageQueue(self.serialNumber)
        self.lib.CC_StopPolling(self.serialNumber)
        self.lib.CC_Close(self.serialNumber)
        
                        
