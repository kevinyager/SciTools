from BLEX.Base import *
import sys
# Update this to point to the directory where you copied the base code
Code_PATH='D:/QPress/Stacker/control_software/Xeryon_actuator/Python Xeryon Library 2020'
Code_PATH in sys.path or sys.path.append(Code_PATH)

from Xeryon import *


class MotorXeryon(Base):
    def __init__(self, name='<MotorXeryon>', **kwargs):
        super().__init__(name=name, **kwargs) # Base

        self.controller = Xeryon("COM3", 115200) # Setup serial communication
        self.axisX      = self.controller.addAxis(Stage.XLS_312, "Z") # Add all axis and specify the correct stage

        self.controller.start()
        self.axisX.setUnits(Units.mm)
        #self.msg('target = {}; actual = {}'.format(axisX.getDPOS(), axisX.getEPOS() ))
        
        self.down_position = 0
        self.up_position = 10

    def get_position(self):
        return self.axisX.getEPOS()

    def set_position(self, position):
        self.axisX.setDPOS(position)
    
    def get_state(self, tolerance=0.1):
        position = self.get_position()
        if abs(position-self.down_position)<tolerance:
            return 'down'
        if abs(position-self.up_position)<tolerance:
            return 'up'
        else:
            return '?'

    def up(self):
        self.set_position(self.up_position)
        
    def down(self):
        self.set_position(self.down_position)
