#!/usr/bin/python
# -*- coding: utf-8 -*-
# vi: ts=4 sw=4




################################################################################
#  Code for querying and controlling beamline components that 'affect' the
# beam. (Beam energy, beam flux, etc.)
################################################################################
# Known Bugs:
#  N/A
################################################################################
# TODO:
#  Search for "TODO" below.
################################################################################


# Notes
################################################################################
# verbosity=0 : Output nothing
# verbosity=1 : Output only final (minimal) result
# verbosity=2 : Output 'regular' amounts of information/data
# verbosity=3 : Output all useful information
# verbosity=4 : Output marginally useful things (e.g. essentially redundant/obvious things)
# verbosity=5 : Output everything (e.g. for testing)



# These imports are not necessary if part of the startup sequence.
# If this file is called separately, some of these may be needed.
#import numpy as np
#from epics import caget, caput
#from time import sleep

#from ophyd import EpicsMotor, Device, Component as Cpt
#from ophyd.commands import * # For mov, movr

#define pilatus_name and _Epicsname, instead of pilatus300 or pilatus2M
#moved to 20-area-detectors.py
#pilatus_name = pilatus2M
#pilatus_Epicsname = '{Det:PIL2M}'


class BeamlineDetector(object):
    
    def __init__(self, detector, **md):
        
        self.detector = detector
        
        self.md = md
        
    
    def get_md(self, prefix='detector_', **md):
        '''Returns a dictionary of the current metadata.
        The 'prefix' argument is prepended to all the md keys, which allows the
        metadata to be grouped with other metadata in a clear way. (Especially,
        to make it explicit that this metadata came from the beamline.)'''
        
        md_return = self.md.copy()
    
        # Include the user-specified metadata
        md_return.update(md)

        # Add an optional prefix
        if prefix is not None:
            md_return = { '{:s}{:s}'.format(prefix, key) : value for key, value in md_return.items() }
    
        return md_return
    
            
            
class SMI_SAXS_Detector(BeamlineDetector):

    def setCalibration(self, direct_beam, distance, detector_position=None, pixel_size=0.172):
        
        self.direct_beam = direct_beam
        self.distance = distance
        if detector_position is None:
            self.detector_position = [SAXS.x.user_readback.value, SAXS.y.user_readback.value]
        else:
            self.detector_position = detector_position
        self.pixel_size = pixel_size
        
    
    def get_md(self, prefix='detector_SAXS_', **md):
        
        md_return = self.md.copy()
    
        x0, y0 = self.direct_beam
        position_defined_x, position_defined_y = self.detector_position
        position_current_x, position_current_y = SAXS.x.user_readback.value, SAXS.y.user_readback.value
        
            
        md_return['name'] = self.detector.name

        md_return['x0_pix'] = round( x0 + (position_current_x-position_defined_x)/self.pixel_size , 2 )
        md_return['y0_pix'] = round( y0 + (position_current_y-position_defined_y)/self.pixel_size , 2 )
        md_return['distance_m'] = self.distance
    
        PV = 'XF:12IDC-ES:2{Det:1M}ROI'
        for i in [1, 2, 3, 4]:
            md_return['ROI{}_X_min'.format(i)] = caget('{}{}:MinX'.format(PV, i))
            md_return['ROI{}_X_size'.format(i)] = caget('{}{}:SizeX'.format(PV, i))
            md_return['ROI{}_Y_min'.format(i)] = caget('{}{}:MinY'.format(PV, i))
            md_return['ROI{}_Y_size'.format(i)] = caget('{}{}:SizeY'.format(PV, i))
        
        # Include the user-specified metadata
        md_return.update(md)

        # Add an optional prefix
        if prefix is not None:
            md_return = { '{:s}{:s}'.format(prefix, key) : value for key, value in md_return.items() }
    
        return md_return
            
            
class BeamlineElement(object):
    '''Defines a component of the beamline that (may) intersect the x-ray beam.'''
    
    def __init__(self, name, zposition, description="", pv=None, **args):
        
        self.name = name
        self.zposition = zposition
        self.description = description
        
        self.conversion_factor = 1
        
        self._pv_main = pv
        
        self.has_flux = True
        
        
    def state(self):
        """
        Returns the current state of the beamline element. Common states:
        out - Element is out of the way of the beam (and should not be blocking).
        in - Element is in the beam (but should not be blocking).
        block - Element is in the beam, and should be blocking the beam.
        undefined - Element is in an unexpected state.
        """
        
        return "out"

    
    def transmission(self, t=None, verbosity=0):
        """
        Returns the predicted transmission of this beamline element, based on 
        its current state.
        """
        
        if t is not None:
            print("WARNING: To change transmission, use 'setTransmission'.")
            print("WARNING: Beam transmission was not changed.")
            return
        
        tr_tot = 1.0
        
        if verbosity>=2:
            print('{:s} transmission = {:.6g}'.format(self.name, tr_tot))
        
        
        # Assume a generic beamline element doesn't block/perturb the beam
        return tr_tot
        
        
    def flux(self, verbosity=3):
        
        reading = self.reading(verbosity=0)
        flux = self.conversion_factor*reading # ph/s
        
        if verbosity>=2:
            print('flux = {:.4g} ph/s'.format(flux))
        
        return flux
    
    
        
        
class Shutter(BeamlineElement):
    
    # Example
    #          XF:11BMA-PPS{PSh}Enbl-Sts
    #  Status: XF:11BMA-PPS{PSh}Pos-Sts       0 for open, 1 for close
    #  Open:   XF:11BMA-PPS{PSh}Cmd:Opn-Cmd
    #  Close:  XF:11BMA-PPS{PSh}Cmd:Cls-Cmd
    
    def __init__(self, name, zposition, description="", pv=None, **args):
        
        super().__init__(name=name, zposition=zposition, description=description, pv=pv, **args)
        self.has_flux = False
        
    
    def state(self):
        """
        Returns the current state of the beamline element. Common states:
        out - Element is out of the way of the beam (and should not be blocking).
        in - Element is in the beam (but should not be blocking).
        block - Element is in the beam, and should be blocking the beam.
        undefined - Element is in an unexpected state.
        """
        
        state_n = caget(self._pv_main+'Pos-Sts')
        
        if state_n is 0:
            return "out"
        elif state_n is 1:
            return "block"
        else:
            return "undefined" 
        
        
    def open(self, verbosity=3):
        
        if verbosity>=3:
            print('Opening {:s}...'.format(self.name))
        
        # E.g. #XF:11BMB-VA{Slt:4-GV:1}Cmd:Opn-Cmd
        pv = self._pv_main + 'Cmd:Opn-Cmd'
        #caput(pv, 1) # TODO: Test this.
    
    def close(self, verbosity=3):
        
        if verbosity>=3:
            print('Closing {:s}...'.format(self.name))
            
        pv = self._pv_main + 'Cmd:Cls-Cmd'
        #caput(pv, 1) # TODO: Test this.

        



class GateValve(Shutter):
    
    # Example
    #  Status: XF:11BMB-VA{Slt:4-GV:1}Pos-Sts        1 for open, 0 for close
    #  Open:   XF:11BMB-VA{Slt:4-GV:1}Cmd:Opn-Cmd
    #  Close:  XF:11BMB-VA{Slt:4-GV:1}Cmd:Cls-Cmd
    
    
    def state(self):
        """
        Returns the current state of the beamline element. Common states:
        out - Element is out of the way of the beam (and should not be blocking).
        in - Element is in the beam (but should not be blocking).
        block - Element is in the beam, and should be blocking the beam.
        undefined - Element is in an unexpected state.
        """
        
        state_n = caget(self._pv_main+'Pos-Sts')
        
        if state_n is 1:
            return "out"
        elif state_n is 0:
            return "block"
        else:
            return "undefined"     
    

        

class Monitor(BeamlineElement):
    
    def quickReading(self, verbosity=3, delay=1.0):
        """
        Puts the diagnostic into the beam, takes a reading, and removes the
        diagnostic.
        """
        
        self.insert()
        time.sleep(delay)
        value = self.reading(verbosity=verbosity)
        
        self.retract()
        time.sleep(delay)
        
        return value
    


# SMIBeam
################################################################################
class SMIBeam(object):
    """
    This class represents the 'beam' at the beamline. This collects together aspects
    of querying or changing beam properties, including the energy (or wavelength), 
    the beam intensity (or measuring flux), and so forth.
    """
    
    def __init__(self):
        
        self._SHUTTER_CLOSED_VOLTAGE = 7
        
    
    # Experimental Shutter
    ########################################
    
    # caput('XF:12IDC-ES:2{PSh:ES}pz:sh:open',1)  # OPEN
    # caput('XF:12IDC-ES:2{PSh:ES}pz:sh:close',1) # CLOSE
    # caget('XF:12IDA-BI:2{EM:BPM1}DAC3') # STATUS
    #  7 V is CLOSE
    #  0 V is OPEN    
    
    
    def is_on(self, tolerance=0.1, verbosity=3):
        '''Returns true if the beam is on (experimental shutter open).'''
    
        voltage = caget('XF:12IDA-BI:2{EM:BPM1}DAC3') # STATUS
        if abs(voltage-self._SHUTTER_CLOSED_VOLTAGE)<tolerance:
            # Closed
            if verbosity>=4:
                print('Beam off (shutter closed).')
            
            return False
            
        else:
            # Open
            if verbosity>=4:
                print('Beam on (shutter open).')
            
            return True
        
        
    def on(self, wait_time=0.1, verbosity=3):
        
        if self.is_on(verbosity=0):
            if verbosity>=4:
                print('Beam on (shutter already open.)')
                
        else:
            
            # Trigger the shutter to open
            caput('XF:12IDC-ES:2{PSh:ES}pz:sh:open',1)  # OPEN
            time.sleep(wait_time)
                

            if verbosity>=4:
                if self.is_on(verbosity=0):
                    print('Beam on (shutter opened).')
                else:
                    print("Beam off (shutter didn't open).")        
                    
    def off(self, wait_time=0.1, verbosity=3):
        
        if self.is_on(verbosity=0):
            
            caput('XF:12IDC-ES:2{PSh:ES}pz:sh:close',1) # CLOSE
            time.sleep(wait_time)
            
        else:
            if verbosity>=4:
                print('Beam off (shutter already closed).')
            
            
        


    # Attenuator/Filter Box
    ########################################
    # Notes:
    # 2 sets of filters.  
    # For high energy: 1-1, to 1-4, to 1-12
    # For low energy: 2-1, to 2-4, to 2-12

    # Insert filter: 
        # caput('XF:12IDC-OP:2{Fltr:1-8}Cmd:Opn-Cmd', 1)  # Insert
    # Withdraw fiter:    
        # caput('XF:12IDC-OP:2{Fltr:1-8}Cmd:Cls-Cmd', 1)  # Remove
    # Status: 
        # caget('XF:12IDC-OP:2{Fltr:1-8}Pos-Sts')
        # 0 means it's removed
        # 1 means it's inserted
        
        
        
    def foilState(self, box=1, verbosity=3):
        
        current_state = [0, 0, 0, 0] # 1, 2, 4, 8

        for i in range(4):
            foil_num = 5+i
            PV = 'XF:12IDC-OP:2{{Fltr:{}-{}}}Pos-Sts'.format(box, foil_num)
            current_state[i] = True if caget(PV)==1 else False
        
        return current_state
        
        
    def insertFoils(self, num_foils, box=1, wait_time=0.2, verbosity=3):
        # WARNING: This is currently hard-coded to actuate the 14-18 keV foils
        # TODO: Generalize this function to handle all foils
        
        current_state = self.foilState(box=box, verbosity=verbosity)
        target_state = self._determineFoils(num_foils)
        
        if verbosity>=4:
            print('current state: {}'.format(current_state))
            print('target state: {}'.format(target_state))
            
        # First insert foils
        #  swith False to True
        for i, state in enumerate(target_state):
            if state==True and current_state[i]==False:
                self._actuateFoil(box, 5+i, True, verbosity=verbosity)
                
        
        # Then remove foils not needed
        #  switch True to False
        for i, state in enumerate(target_state):
            if state==False and current_state[i]==True:
                self._actuateFoil(box, 5+i, False, verbosity=verbosity)
                
                
                
        # Double check that it worked
        current_state = self.foilState(box=box, verbosity=verbosity)
        if current_state!=target_state:
            if verbosity>=1:
                print('WARNING: Foils did not actuate correctly')
                print('current state: {}'.format(current_state))
                print('target state: {}'.format(target_state))
                
                
        
        

        
    def _actuateFoil(self, box, foil_num, state, wait_time=1.0, max_retries=10, verbosity=3):
        
        PV_status = 'XF:12IDC-OP:2{{Fltr:{}-{}}}Pos-Sts'.format(box, foil_num)
        
        if state:
            # Insert
            PV = 'XF:12IDC-OP:2{{Fltr:{}-{}}}Cmd:Opn-Cmd'.format(box, foil_num)
            if verbosity>=4:
                print('    Inserting box,foil = ({}, {}), PV={}'.format(box, foil_num, PV))
            
        else:
            # Remove
            PV = 'XF:12IDC-OP:2{{Fltr:{}-{}}}Cmd:Cls-Cmd'.format(box, foil_num)
            if verbosity>=4:
                print('    Removing box,foil = ({}, {}), PV={}'.format(box, foil_num, PV))
            
            
        itry = 0
        while itry<max_retries and caget(PV_status)!=state:
            if verbosity>=5:
                print('    itry {}'.format(itry))
            caput(PV, 1)
            itry += 1
            time.sleep(wait_time)
            
        
        
        
        
        

    def _determineFoils(self, num_foils, verbosity=3):
        
        target_state = [ False, False, False, False ]
        
        num_foils = np.clip(num_foils, 0, 15)
        
        if num_foils>=8:
            target_state = self._determineFoils(num_foils-8)
            target_state[3] = True
            
        elif num_foils>=4:
            target_state = self._determineFoils(num_foils-4)
            target_state[2] = True
            
        elif num_foils>=2:
            target_state = self._determineFoils(num_foils-2)
            target_state[1] = True

        elif num_foils>=1:
            target_state = self._determineFoils(num_foils-1)
            target_state[0] = True
            
            
        return target_state
        




    # End class SMIBeam(object)
    ########################################
    


beam = SMIBeam()


class Beamline(object):
    '''Generic class that encapsulates different aspects of the beamline.
    The intention for this object is to have methods that activate various 'standard'
    protocols or sequences of actions.'''

    def __init__(self, **kwargs):
        
        self.md = {}
        self.current_mode = 'undefined'
        
        
    def mode(self, new_mode):
        '''Tells the instrument to switch into the requested mode. This may involve
        moving detectors, moving the sample, enabling/disabling detectors, and so
        on.'''
        
        getattr(self, 'mode'+new_mode)()
        
        
    def get_md(self, prefix=None, **md):
        '''Returns a dictionary of the current metadata.
        The 'prefix' argument is prepended to all the md keys, which allows the
        metadata to be grouped with other metadata in a clear way. (Especially,
        to make it explicit that this metadata came from the beamline.)'''
        
        # Update internal md
        #self.md['key'] = value

        md_return = self.md.copy()
    
        # Add md that may change
        md_return['mode'] = self.current_mode
    
        # Include the user-specified metadata
        md_return.update(md)

        # Add an optional prefix
        if prefix is not None:
            md_return = { '{:s}{:s}'.format(prefix, key) : value for key, value in md_return.items() }
    
        return md_return
            
        
    def comment(self, text, logbooks=None, tags=None, append_md=True, **md):
        
        text += '\n\n[comment for beamline: {}]'.format(self.__class__.__name__)
        
        if append_md:
        
            # Global md
            md_current = { k : v for k, v in RE.md.items() }
            
            # Beamline md
            md_current.update(self.get_md())
            
            # Specified md
            md_current.update(md)
            
            text += '\n\n\nMetadata\n----------------------------------------'
            for key, value in sorted(md_current.items()):
                text += '\n{}: {}'.format(key, value)
        
        logbook.log(text, logbooks=logbooks, tags=tags)
        
        
    def log_motors(self, motors, verbosity=3, **md):
      
        log_text = 'Motors\n----------------------------------------\nname | position | offset | direction |\n'
      
        for motor in motors:
            offset = float(caget(motor.prefix+'.OFF'))
            direction = int(caget(motor.prefix+'.DIR'))
            log_text += '{} | {} | {} | {} |\n'.format(motor.name, motor.user_readback.value, offset, direction)
      
      
        md_current = { k : v for k, v in RE.md.items() }
        md_current.update(md)
        log_text += '\nMetadata\n----------------------------------------\n'
        for k, v in sorted(md_current.items()):
            log_text += '{}: {}\n'.format(k, v)
            
        if verbosity>=3:
            print(log_text)
            
        self.comment(log_text)
            

    def detselect(self, detector_object, roi=None, suffix='_stats1_total'):
        """Switch the active detector and set some internal state"""
        
        roi_lookups = [ [1, pil1mroi1], [2, pil1mroi2], [3, pil1mroi3], [4, pil1mroi4] ]

        if isinstance(detector_object, (list, tuple)):
            self.detector = detector_object
        else:
            self.detector = [detector_object]
            
        if roi is None:
            self.PLOT_Y = self.detector[0].name + suffix
        else:
            self.PLOT_Y = 'pil1mroi{}'.format(roi)
            
            for check_name, det in roi_lookups:
                if roi==check_name:
                    self.detector.append(det)
            
        self.TABLE_COLS = [self.PLOT_Y]

        return self.detector



class SMI_Beamline(Beamline):
    
    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)
        
        self.beam = beam
        self.current_mode = 'undefined'
        self.bsx_pos = 1.2
        
        self.SAXS = SMI_SAXS_Detector(pil1M)
        self.detectors_measure = [pil1M, rayonix]
        
    
    def on(self, verbosity=3):

        caput('XF:12IDA-PPS:2{PSh}Cmd:Opn-Cmd', 1)
        time.sleep(4)
        feedback('on')


    def off(self, verbosity=3):

        feedback('off')
        time.sleep(1)

        caput('XF:12IDA-PPS:2{PSh}Cmd:Cls-Cmd', 1)
        time.sleep(1)


    def ventChamber(self, wait_time=0.2, verbosity=3):
        
        # "Auto Bleed to air"
        caput('XF:12IDC-VA:2{Det:1M-GV:7}Cmd:Cls-Cmd', 1)
        time.sleep(wait_time)
        caput('XF:12IDC-VA:2{Mir:BDM-GV:6}Cmd:Cls-Cmd', 1)
        time.sleep(wait_time)
        caput('XF:12IDC-VA:2{Det:300KW-IV:1}Cmd:Cls-Cmd', 1)
        time.sleep(wait_time)
        caput('XF:12IDC-VA:2{Det:300KW-TMP:1}OnOff', 0)
        time.sleep(wait_time)
        caput('XF:12IDC-PU{PCHW-Vlv:Supply}Cmd:Cls-Cmd', 1)
        time.sleep(wait_time)
        caput('XF:12IDC-PU{N2-Vlv:Supply}Cmd:Opn-Cmd', 1)

        time.sleep(wait_time+3)
        
        caput(' XF:12IDC-VA:2{Det:300KW-VVSoft:WAXS}Cmd:Opn-Cmd',1) # Open WAXS soft vent


    def pumpChamber(self, wait_time=0.2, verbosity=3):
        
        # "Auto Evacuate"
        caput('XF:12IDC-VA:2{Det:300KW-VVSoft:WAXS}Cmd:Cls-Cmd', 1) # $(Sys){Det:300KW-VVSoft:WAXS}Cmd:Cls-Cmd
        time.sleep(wait_time)
        
        caput('XF:12IDC-VA:2{Det:300KW-VV:WAXS}Cmd:Cls-Cmd', 1) # $(Sys){Det:300KW-VV:WAXS}Cmd:Cls-Cmd
        time.sleep(wait_time)
        
        caput('XF:12IDC-PU{Air-Vlv:Supply}Cmd:Cls-Cmd', 1)
        time.sleep(wait_time)
        caput('XF:12IDC-PU{N2-Vlv:Supply}Cmd:Cls-Cmd', 1)
        time.sleep(wait_time)
        caput('XF:12IDC-VA:2{Det:300KW-IV:1}Cmd:Opn-Cmd', 1) # $(Sys){Det:300KW-IV:1}Cmd:Opn-Cmd
        time.sleep(wait_time)
        caput('XF:12IDC-PU{PCHW-Vlv:Supply}Cmd:Opn-Cmd', 1)
        time.sleep(wait_time)
        caput('XF:12IDC-VA:2{Det:300KW-TMP:1}OnOff', 1)
        

    def modeAlignment(self, verbosity=3):
        
        if RE.state!='idle':
            RE.abort()
        
        self.current_mode = 'undefined'
        self.beam.off()
        
        # Put in attenuators
        self.beam.insertFoils(8)
        
        # Move beamstop
        pil1m_bs.x.move(self.bsx_pos+5)
        
        self.setReflectedBeamROI()
        self.setDirectBeamROI()
        self.detselect(self.SAXS.detector, roi=4)
        self.SAXS.detector.cam.acquire_time.set(0.5)
        self.SAXS.detector.cam.acquire_period.set(0.6)
        
        self.SAXS.detector.cam.file_name.set('align')
        self.SAXS.detector.cam.file_number.set(1)

        
        self.current_mode = 'alignment'


    def modeMeasurement(self, verbosity=3):

        if RE.state!='idle':
            RE.abort()
        
        self.current_mode = 'undefined'
        self.beam.off()
        
        pil1m_bs.x.move(self.bsx_pos)
        
        # Remove attenuators
        self.beam.insertFoils(0)
        
        self.detselect(self.detectors_measure)
        
        self.current_mode = 'measurement'



    def setDirectBeamROI(self, size=[12,6], verbosity=3):
        '''Update the ROI (stats4) for the direct beam on the SAXS
        detector. This (should) update correctly based on the current SAXSx, SAXSy.
        
        The size argument controls the size (in pixels) of the ROI itself
        (in the format [width, height]). A size=[12,6] is reasonable.
        '''
        
        detector = self.SAXS

        # These positions are updated based on current detector position
        det_md = detector.get_md()
        x0 = det_md['detector_SAXS_x0_pix']
        y0 = det_md['detector_SAXS_y0_pix']
        
        
        PV = 'XF:12IDC-ES:2{Det:1M}'
        caput('{}ROI4:MinX'.format(PV), int(x0-size[0]/2))
        caput('{}ROI4:SizeX'.format(PV), int(size[0]))
        caput('{}ROI4:MinY'.format(PV), int(y0-size[1]/2))
        caput('{}ROI4:SizeY'.format(PV), int(size[1]))
        


    def setReflectedBeamROI(self, total_angle=0.16, size=[12,4], verbosity=3):
        '''Update the ROI (stats3) for the reflected beam on the SAXS
        detector. This (should) update correctly based on the current SAXSx, SAXSy.
        
        The size argument controls the size (in pixels) of the ROI itself
        (in the format [width, height]). A size=[12,4] is reasonable.'''
        
        detector = self.SAXS

        # These positions are updated based on current detector position
        det_md = detector.get_md()
        x0 = det_md['detector_SAXS_x0_pix']
        y0 = det_md['detector_SAXS_y0_pix']
        
        d = detector.distance*1000.0 # mm
        pixel_size = detector.pixel_size # mm
        
        y_offset_mm = np.tan(np.radians(total_angle))*d
        y_offset_pix = y_offset_mm/pixel_size
        
        y_pos = int( y0 - size[1]/2 - y_offset_pix )

        PV = 'XF:12IDC-ES:2{Det:1M}'
        caput('{}ROI3:MinX'.format(PV), int(x0-size[0]/2))
        caput('{}ROI3:SizeX'.format(PV), int(size[0]))
        caput('{}ROI3:MinY'.format(PV), int(y_pos))
        caput('{}ROI3:SizeY'.format(PV), int(size[1]))
        
        


    # End class SMI_Beamline(Beamline)
    ########################################


smi = SMI_Beamline()


def get_beamline():
    return smi


