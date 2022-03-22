from BLEX.Base import *

from pipython import GCSDevice, pitools



class MotorPI_Linear(Base):
    def __init__(self, SN, axis='1', name='<MotorPI_linear>', active=True, **kwargs):
        super().__init__(name=name, **kwargs) # Base
        
        self.SN = SN
        self.axis = axis
        self.active = active
        
        self.connect(SN)
        
    def connect(self, SN):
        self.pidevice = GCSDevice()
        self.pidevice.ConnectUSB(serialnum=SN)
        
        self.msg('Connected to PI device: {}'.format(self.pidevice.qIDN().strip()), 3, 1)
        if self.pidevice.HasqVER():
            self.msg('version info:\n{}'.format(self.pidevice.qVER().strip()), 3, 2)
        
    def get_position(self):
        positions = self.pidevice.qPOS()
        position = positions[self.axis]
        return position
    
    def set_position(self, position):
        if self.active:
            self.pidevice.MOV(self.axis, position)
            pitools.waitontarget(self.pidevice, axes=self.axis)

    def get_velocity(self):
        velocity = self.pidevice.qVEL()[self.axis]
        return velocity
        
    def set_velocity(self, velocity):
        self.msg('Changing velocity to {:4f}'.format(velocity), 4, 2)
        self.pidevice.VEL(self.axis, velocity)
        
        
        
class ControllerPI_Hexapod(Base):
    def __init__(self, controller_name, IP, port=50000, name='<MotorPI_hexapod_controller>', active=True, **kwargs):
        super().__init__(name=name, **kwargs) # Base
        
        self.connect(controller_name=controller_name, IP=IP, port=port)
        
        # Translations
        self.X = MotorPI_Hexapod(self, axis='X', name='hex_X', common=self._common, verbosity=self.verbosity)
        self.Y = MotorPI_Hexapod(self, axis='Y', name='hex_Y', common=self._common, verbosity=self.verbosity)
        self.Z = MotorPI_Hexapod(self, axis='Z', name='hex_Z', common=self._common, verbosity=self.verbosity)
        
        # Rotations
        # U rotates about X-axis (RHR about +X)
        self.U = MotorPI_Hexapod(self, axis='U', name='hex_rotU', common=self._common, verbosity=self.verbosity)
        # V rotates about Y-axis (RHR about +Y)
        self.V = MotorPI_Hexapod(self, axis='V', name='hex_rotV', common=self._common, verbosity=self.verbosity)
        # W rotates about Z-axis (RHR about +Z)
        self.W = MotorPI_Hexapod(self, axis='W', name='hex_rotW', common=self._common, verbosity=self.verbosity)
        
        

    def connect(self, controller_name, IP, port=50000):
        self.pidevice = GCSDevice(controller_name)
        self.pidevice.ConnectTCPIP(ipaddress=IP)

        self.msg('Connected to PI device: {}'.format(self.pidevice.qIDN().strip()), 3, 1)
        if self.pidevice.HasqVER():
            self.msg('version info:\n{}'.format(self.pidevice.qVER().strip()), 3, 2)

    def get_velocity(self):
        return self.pidevice.qVLS()

    def set_velocity(self, velocity):
        self.pidevice.VLS(velocity)
        


class MotorPI_Hexapod(Base):
    def __init__(self, controller, axis, name='<MotorPI_hexapod_axis>', active=True, **kwargs):
        super().__init__(name=name, **kwargs) # Base
        self.controller = controller
        self.axis = axis
        self.active = active
        
    def get_position(self):
        positions = self.controller.pidevice.qPOS()
        position = positions[self.axis]
        return position
    
    def set_position(self, position):
        if self.active:
            self.controller.pidevice.MOV(self.axis, position)
            pitools.waitontarget(self.controller.pidevice, axes=self.axis)
            
    def get_velocity(self):
        return self.controller.get_velocity()
    
    def set_velocity(self, velocity):
        self.msg('Changing velocity to {:4f}'.format(velocity), 4, 2)
        self.controller.set_velocity(velocity)
