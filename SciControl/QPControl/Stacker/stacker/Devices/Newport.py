from BLEX.Base import *

import serial
# To list ports:
# python -m serial.tools.list_ports
# Minicom:
# python -m serial.tools.miniterm COM4
# Port names:
#   Windows: COM1, ...
#   Linux: /dev/ttyUSB0 , /dev/bus/usb/002/017 



class SerialDevice(Base):
    
    def __init__(self, name="SerialDevice", serial_device='/dev/ttyUSB0', baud=9600, command_terminator='\r\n', com_wait_time=0.05, poling_wait_time=0.05, **kwargs):
        
        super().__init__(name=name, **kwargs)

        self.command_terminator = command_terminator
        self.com_wait_time = com_wait_time
        self.poling_wait_time = poling_wait_time
        
        self.open_connection( serial_device=serial_device, baud=baud )


    def open_connection(self, serial_device='/dev/ttyUSB0', baud=9600 ):
        
        self.serial_device = serial_device
        self.ser = serial.Serial( self.serial_device, baud )
        
        msg = "Serial connection for {} on {}".format(self.__class__.__name__, self.serial_device)
        self.msg(msg, 3, 1)
        
        
    # Getting data from device
    ########################################
    def wait(self, wait_time=None):
        
        wait_time = self.com_wait_time if wait_time is None else wait_time
        time.sleep( wait_time )
        
        
    def readline(self):
        self.wait()
        line = self.ser.readline()
        self.wait()
        
        return line
        
        
    def readfloat(self):
        line = self.readline()
        return float(line)
    
    
    # Sending commands to device
    ########################################
    def send_null(self):
        self.command("\x00")
        
    
    def command(self, cmd):
        self.wait()
        cmd = cmd + self.command_terminator
        self.ser.write( cmd.encode() )
        self.wait()

        
    # Getting data from device
    ########################################
    def read(self, cmd):
        self.wait()
        cmd = cmd + self.command_terminator
        self.ser.write( cmd.encode() )
        self.wait()
        
        line = self.ser.readline()
        self.wait()
        
        return line             
        
    def read_msg(self, cmd, threshold=3, indent=1, **kwargs):
        line = self.read(cmd).strip()
        self.msg(line, threshold=threshold, indent=indent, **kwargs)


    # House-keeping
    ########################################
    def close(self):
        self.ser.close()
        
    def __del__(self):
        self.close()

        
    # End class SerialDevice(Base)
    ########################################
    
    
class ControllerNewport(SerialDevice):
    
    def __init__(self, name="controllerNewport", serial_device='/dev/ttyUSB0', baud=921600, command_terminator='\r\n', com_wait_time=0.05, poling_wait_time=0.1, **kwargs):
        
        super().__init__(name=name, serial_device=serial_device, baud=baud, command_terminator=command_terminator, com_wait_time=com_wait_time, poling_wait_time=poling_wait_time, **kwargs)
        
        #self.msg( self.query('1 ID'), 2, 2 )
    
    
    def open_connection(self, serial_device='/dev/ttyUSB0', baud=921600):
        
        self.serial_device = serial_device
        self.ser = serial.Serial(self.serial_device, baud, timeout=1, parity=serial.PARITY_NONE, bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE, rtscts=True, dsrdtr=True)        
        
        msg = "Serial connection for {} on {}".format(self.__class__.__name__, self.serial_device)
        self.msg(msg, 3, 1)
        
        
    def query(self, cmd):
        
        self.wait()
        cmd = cmd + ' ? ' + self.command_terminator
        self.ser.write( cmd.encode() )
        self.wait()
        
        line = self.ser.readline()
        self.wait()
        
        return line
        
        
    def query_msg(self, cmd, threshold=3, indent=1, **kwargs):
        line = self.query(cmd)
        self.msg(line, threshold=threshold, indent=indent, **kwargs)
        
    # End class ControllerNewport(SerialDevice)
    ########################################
        

        
class MotorNewport(Base):
    def __init__(self, controller, stage_id, name='<MotorNewport>', active=True, default_acceleration=200.0, **kwargs):
        super().__init__(name=name, **kwargs) # Base
        
        self.controller = controller
        self.stage_id = stage_id
        self.active = active
        self.default_acceleration = default_acceleration
        
        self.poling_wait_time = self.controller.poling_wait_time
        
    # IO
    ########################################
    def read(self, cmd):
        return self.controller.read(cmd)
   
    def query(self, cmd):
       return self.controller.query(cmd)

    def query_msg(self, cmd, threshold=3, indent=1, **kwargs):
        self.controller.query_msg(cmd, threshold=threshold, indent=indent, **kwargs)

    def command(self, cmd):
        return self.controller.command(cmd)        


    # Stage status
    ########################################
    def get_position(self, **kwargs):
        
        #line = self.query('1 PA')
        cmd = '{:d} TP'.format(self.stage_id)
        line = self.read(cmd).strip()
        try:
            position = float(line)
        except ValueError:
            self.msg_error('Failed to parse stage position ({:s})'.format(line))
            position = -99999999.9999
            
        return position

        
    def get_velocity(self, **kwargs):
        cmd = '{:d}VA?'.format(self.stage_id)
        line = self.read(cmd).strip()
        return float(line)

        
    def identification_string(self):
        
        firmware = self.query( 'VE' ).strip()
        cmd = '{:d} ID'.format(self.stage_id)
        stage = self.query(cmd).strip()
        
        id_str = '%s; firmware: %s; axis: %s' % (self.__class__.__name__, firmware, stage)
        
        return id_str
        
        
    def identification_msg(self, threshold=3, indent=0):
        self.msg( self.identification_string() , threshold=threshold, indent=indent )
            
        
    def check_error(self):
        """Checks the error stage of the stage. Returns True if there is an error, False if everything is okay."""
        
        status = int(self.query('TE'))
        if status!=0:
            self.msg_error( 'Stage issued error-code {:d}'.format(status) )
            return True
        else:
            return False
        
        
    def motion_done(self):
        """Reads the status of the stage motion. Returns True if motion is complete, False otherwise."""
        
        cmd = '{:d} MD'.format(self.stage_id)
        status = int(self.query(cmd))
        if status==1:
            return True
        else:
            return False
        
        
    def motion_wait(self):
        """Blocks until the stage motion is complete."""
        
        self.msg( 'Waiting for Newport stage {:d} to stop moving...'.format(self.stage_id), 5, 0)
        
        searching = True
        #self.timing_start()
        while(searching):
            #search_time = self.timing_end()
            searching = not self.motion_done()
            
            position = self.get_position()
            
            self.msg('moving... position = {:.4f} mm'.format(position), 5, 1)
                
            time.sleep(self.poling_wait_time)            


    # Stage motion
    ########################################
    def set_position(self, position, velocity=None, **kwargs):
        self.move_absolute_wait_stop(position, velocity=velocity)
    
    def move_absolute(self, position, velocity=None):
        """WARNING: When this function returns, the stage is still in motion!"""

        self.set_velocity(velocity)
        
        if velocity is not None:
            self.msg('moving to {:.2f} mm (@ {:.4f} mm/s)'.format(position, velocity), threshold=4, indent=1)
        else:
            self.msg('moving to {:.2f} mm'.format(position), threshold=4, indent=1)
            
        if(self.active):
            cmd = '{:d} PA {:.4f}'.format(self.stage_id, position)
            self.command(cmd)
            
            
    def move_absolute_wait_stop(self, position, velocity=None, delay_at_end=0.0):
        
        self.move_absolute(position, velocity=velocity)
        
        self.motion_wait()
        
        time.sleep(delay_at_end)


    def set_velocity(self, velocity):
        if velocity is not None:
            self.msg('changing velocity to {:.4f} mm/s'.format(velocity), threshold=4, indent=2)
            cmd = '{:d} VA {:.4f}'.format(self.stage_id, velocity)
            self.command(cmd)
        

        
    # Stage complex motion
    ########################################
    def move_relative(self, distance, velocity=5.0):
        """WARNING: When this function returns, the stage is still in motion!"""

        cmd = '{:d} VA {:.4f}'.format(self.stage_id, velocity)
        self.command(cmd)
        
        self.msg('moving {:.2f} mm (@ {:.4f mm/s)'.format(distance, velocity), threshold=4, indent=2)
        if self.active:
            cmd = '{:d} PR {:.4f}'.format(self.stage_id, distance)
            self.command(cmd)

            
    def move_relative_wait_time(self, distance, velocity=5.0, delay_at_end=0.0):
        
        self.move_relative(distance, velocity=velocity)
            
        move_time = abs(distance/velocity)
        time.sleep(move_time+delay_at_end)

        
    def move_relative_wait_position(self, distance, velocity=5.0, tolerance=0.01, delay_at_end=0.0):
        
        target = self.get_position() + distance
        move_time = abs(distance/velocity)
        
        self.move_relative(distance, velocity=velocity)
        
        searching = True
        start = time.time()
        while( searching ):
            
            search_time = time.time()-start
            
            position = self.get_position()
            if abs(position-target)<tolerance:
                searching = False

            self.msg( '%.1fs; target = %.3fmm; position = %.3fmm' % (search_time, target, position) , threshold=10, indent=1)
            if search_time>(move_time*1.1):
                self.msg( '%.1fs; target = %.3fmm; position = %.3fmm; MOVE IS TAKING TOO LONG' % (search_time, target, position) , threshold=4, indent=1)
                
            time.sleep(self.poling_wait_time)
            
        time.sleep(delay_at_end)

        
    def move_relative_wait_stop(self, distance, velocity=5.0, delay_at_end=0.0):
        
        self.move_relative(distance, velocity=velocity)
        
        self.motion_wait()
        
        time.sleep(delay_at_end)
        
        
    def accel_ramp(self, length, v_final, delay_at_end=0.0):
        
        acceleration = (v_final**2)/(2.0*length)
        
        self.msg('accelerating from 0 mm/s to %.4f mm/s over %.2f mm (accel %.4f mm/s^2)' % (v_final, length, acceleration), threshold=4, indent=2)
        
        cmd = '{:d} AC {:.6f}'.format(self.stage_id, acceleration)
        self.command(cmd)
        self.move_relative_wait_stop(length, velocity=v_final, delay_at_end=delay_at_end)
        
        # Return to normal status
        cmd = '{:d} AC {:.6f}'.format(self.stage_id, self.default_acceleration)
        self.command(cmd)        

    # End class MotorNewport(Base)
    ########################################
