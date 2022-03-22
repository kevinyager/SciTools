#import sys
#sys.path.insert(1, '../') # To import BLEX if you want to run this file directly
from BLEX.Base import *

import serial 


class InstecThermalChuck(Base):
    
    def __init__(self, name="Instec", serial_device='COM5', baud=38400, command_terminator='\r\n', com_wait_time=0.05, poling_wait_time=0.05, **kwargs):
        super().__init__(name=name, **kwargs)

        self.command_terminator = command_terminator
        self.com_wait_time = com_wait_time
        self.poling_wait_time = poling_wait_time
        
        self.open_connection(serial_device=serial_device, baud=baud)
        
        self.ident()
        
        if False: # Re-open the connection
            self.ser.close()
            self.open_connection(serial_device=serial_device, baud=baud, flush=False)


    def open_connection(self, serial_device='COM5', baud=38400, flush=True):
        
        self.serial_device = serial_device
        self.ser = serial.Serial( port=self.serial_device, baudrate=baud )
        
        time.sleep(0.5)
        if flush:
            self.ser.flushInput()
            self.ser.flushOutput()
        
        msg = "Serial connection for {} on {}".format(self.__class__.__name__, self.serial_device)
        self.msg(msg, 3, 1)
        
        
        
    def wait(self, wait_time=None):
        
        wait_time = self.com_wait_time if wait_time is None else wait_time
        time.sleep( wait_time )

    def readline(self):
        self.wait()
        line = self.ser.readline().decode()
        self.wait()
        return line
        
    def readfloat(self):
        line = self.readline().decode()
        return float(line)
                
    def command(self, cmd):
        self.wait()
        cmd = cmd + self.command_terminator
        self.ser.write( cmd.encode() )
        self.wait()                
        
    def read(self, cmd):
        self.wait()
        cmd = cmd + self.command_terminator
        self.ser.write( cmd.encode() )
        self.wait()
        
        line = self.ser.readline().decode()
        self.wait()
        
        return line

    def read_msg(self, cmd, threshold=3, indent=1, **kwargs):
        line = self.read(cmd).strip()
        self.msg(line, threshold=threshold, indent=indent, **kwargs)
        
                
    def ident(self, cmd="*IDN?\r\n"):
        return self.read_msg("*IDN?")

    def get_coolheatstate(self):
        return int(self.read("TEMP:CHSWitch?"))

    def set_coolheatstate(self, state):
        self.command("TEMP:CHSWitch {:d}".format(state))

    def set_purge(self, t1=None, t2=None):
        t1 = '' if t1 is None else ' {:.2f}'.format(t1)
        t2 = '' if t2 is None else ',{:.2f}'.format(t2)
        cmd = 'TEMP:PURGe{}{}'.format(t1, t2)
        self.command(cmd)

    def vacuum_on(self):
        #self.set_purge(0, 365*24*60*60)
        self.command("TEMP:OUT4 1")
    def vacuum_off(self):
        #self.set_purge(0, 0)
        self.command("TEMP:OUT4 0")

    def get_setpoint(self):
        return float(self.read("TEMP:SPOint?"))

    
    def get_position(self):
        return float(self.read("TEMP:CTEM?"))

    def set_position(self, position):
        #T_current =  float(self.read("TEMP:CTEM?"))
        self.command("TEMP:HOLD {:.2f}".format(position))
        



#if __name__ == '__main__':
    #instec = InstecThermalChuck(name="Instec", serial_device='COM5')
    
