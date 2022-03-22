#!/usr/bin/env python3

from keys_main import *
import subprocess

if False:
    import epics
    
else:
    # Testing mode
    class PV():
        def get(self):
            return 0
    class EpicsFake():
        def PV(self, PV_name):
            return PV()
    epics = EpicsFake()
    
    class Beamline():
        pass
    beamline = Beamline()
    def get_beamline():
        return beamline
    class Beam():
        def transmission(self, verbosity=3):
            return 0.87
        def is_on(self):
            return True
    beam = Beam()
    class Bim():
        def flux(self, verbosity=3):
            return 2.1e5
        def reading(self, verbosity=3):
            return 0
    beam.bim3 = Bim()
    beam.bim5 = Bim()
    beam.elements = [Bim()]
    
    
    
# For Complex Materials Scattering (CMS) beamline at NSLS-II    
########################################

def window_inject(text, identify=' : bsui', press_enter=True, extra_check=None):
    original_window_id = int(subprocess.check_output('xdotool getwindowfocus', shell=True))
    try:
        window_id = int(subprocess.check_output('xdotool search --name "{}"'.format(identify), shell=True))
        print(window_id)
        os.system('xdotool windowactivate {:d}'.format(window_id)) # Switch window
        window_name = subprocess.check_output('xdotool getwindowfocus getwindowname', shell=True)
        if extra_check is None or extra_check in window_name:
            os.system('xdotool type "{}"'.format(text)) # Inject text
            time.sleep(0.05)
            if press_enter:
                os.system('xdotool key KP_Enter')
                time.sleep(0.05)
      
    except:
        # Error! Desired window probably doesn't exist. So do nothing.
        print('Warning: error in window_inject.')
        
    os.system('xdotool windowactivate {:d}'.format(original_window_id)) # Switch back to original window

class RingCurrent(ValueRing):
    
    def __init__(self, beam=None, **kwargs):
        super().__init__(**kwargs)
        self.beam = beam
    
    def style(self, state):
        name = "empty"
        icon = "empty{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "mA"
        return name, icon, font, label
    
    def get_color(self):
        if self.value>300:
            return '#00FF00'
        elif self.value>50:
            return '#C8C800'
        else:
            return '#960000'    
    
    def get_value(self, vmin=0, vmax=500):
        return super().get_value(vmin=vmin, vmax=vmax)
    
    def action(self):
        #os.system('xdotool type "Ring current: {} mA"'.format(self.value))
        os.system('xdg-open https://status.nsls2.bnl.gov/')

    def refresh(self, deck, key, state):
        self.value = self.beam.elements[0].reading(verbosity=0)
        return self.value

class LogValueRing(ValueRing):
    
    def get_color(self, vmin=0, vmax=1):
        #value = np.clip((self.value-vmin)/(vmax-vmin), vmin, vmax)
        value = self.get_value()
        r = int( 0 )
        g = int( 255*value )
        b = int( 0 )
        
        return "rgb({:d},{:d},{:d})".format(r,g,b)
    
    def get_value(self, lvmin=-10, lvmax=0):
        # self.value [1e-10 ... 1.0]
        v = np.log10(self.value) # [-10 ... 0]
        v = (v-lvmin)/(lvmax-lvmin) # [0 ... 1]
        v = np.clip(v, 0, 1)
        return v
    
    def render_key_image(self, deck, icon_filename, font_filename, label_text, state=False):
        # Create new key image of the correct dimensions, black background
        image = PILHelper.create_image(deck)
        draw = ImageDraw.Draw(image)
        
        fill = self.get_color()
        
        draw.rectangle( [(0, 0), (image.width, image.height)], fill=fill)
        
        inset = 5
        bbox = [inset, inset, image.width-inset, image.height-inset]
        a = self.gap_for_label
        span = ( 90-a -(-270+a) )
        vangle = self.get_value()*span
        draw.pieslice(bbox, -270+a, 90-a, fill="black")
        draw.pieslice(bbox, -270+a, -270+a+vangle, fill="white")
        inset = 17
        bbox = [inset, inset, image.width-inset, image.height-inset]
        draw.ellipse(bbox, fill=fill)

        label_extra = "{:.0g}".format(self.value)
        font = ImageFont.truetype(font_filename, 14)
        label_w, label_h = draw.textsize(label_extra, font=font)
        label_pos = ( (image.width - label_w) // 2, (image.height - label_h) // 2 )
        draw.text(label_pos, text=label_extra, font=font, fill="white")


        font = ImageFont.truetype(font_filename, 14)
        label_w, label_h = draw.textsize(label_text, font=font)
        label_pos = ((image.width - label_w) // 2, image.height - 20)
        draw.text(label_pos, text=label_text, font=font, fill="white")

        return PILHelper.to_native_format(deck, image) 

class Transmission(LogValueRing):
    def __init__(self, beam=None, **kwargs):
        super().__init__(**kwargs)
        self.beam = beam
    
    def style(self, state):
        name = "empty"
        icon = "empty{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "trans"
        return name, icon, font, label
    
    def get_value(self, lvmin=-7, lvmax=0):
        return super().get_value(lvmin=lvmin, lvmax=lvmax)
    
    def action(self):
        window_inject('beam.transmission()')

    def refresh(self, deck, key, state):
        self.value = self.beam.transmission(verbosity=0)
        return self.value

class IonChamber(LogValueRing):
    def __init__(self, beam=None, **kwargs):
        super().__init__(**kwargs)
        self.beam = beam
    
    def style(self, state):
        name = "empty"
        icon = "empty{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "ic"
        return name, icon, font, label
    
    def get_value(self, lvmin=0, lvmax=14):
        return super().get_value(lvmin=lvmin, lvmax=lvmax)
    
    def action(self):
        window_inject('beam.fluxes()')

    def refresh(self, deck, key, state):
        self.value = self.beam.bim3.flux(verbosity=0)
        return self.value

class Diamond(LogValueRing):
    def __init__(self, beam=None, **kwargs):
        super().__init__(**kwargs)
        self.beam = beam
    
    def style(self, state):
        name = "empty"
        icon = "empty{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "diam"
        return name, icon, font, label
    
    def get_value(self, lvmin=0, lvmax=14):
        return super().get_value(lvmin=lvmin, lvmax=lvmax)
    
    def action(self):
        window_inject('beam.fluxes()')

    def refresh(self, deck, key, state):
        self.value = self.beam.bim5.flux(verbosity=0)
        return self.value

class ChamberPressure(LogValueRing):
    def __init__(self, beamline=None, **kwargs):
        super().__init__(**kwargs)
        self.beamline = beamline
    
    def style(self, state):
        name = "empty"
        icon = "empty{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "torr"
        return name, icon, font, label
    
    def get_color(self, vmin=0, vmax=1):
        value = self.get_value()
        r = int( 0 )
        g = int( 0 )
        b = int( 255*value )
        
        return "rgb({:d},{:d},{:d})".format(r,g,b)    
    
    def get_value(self, lvmin=-5, lvmax=3):
        return super().get_value(lvmin=lvmin, lvmax=lvmax)
    
    def action(self):
        window_inject('cms.chamberPressure()')

    def refresh(self, deck, key, state):
        #self.beamline.?
        return None # TODO

class BeamElement(BigText):
    
    def __init__(self, beam=None, **kwargs):
        super().__init__(**kwargs)
        self.beam = beam
    
    def action(self):
        # Toggle
        if self.state:
            self.off()
        else:
            self.on()
    
    def on(self):
        pass
    def off(self):
        pass
    def refresh(self, deck, key, state):
        #self.state = False
        return self.state
    
class BeamElementPV(BeamElement):    
    # PV Examples:
    # FE Shutter XF:11BM-PPS{Sh:FE}Sts:FailOpn-Sts
    # Photon Shutter XF:11BMA-PPS{PSh}Sts:FailOpn-Sts
    #          XF:11BMA-PPS{PSh}Enbl-Sts
    #  Status: XF:11BMA-PPS{PSh}Pos-Sts       0 for open, 1 for close
    #  Open:   XF:11BMA-PPS{PSh}Cmd:Opn-Cmd
    #  Close:  XF:11BMA-PPS{PSh}Cmd:Cls-Cmd
    def __init__(self, PVbase, status='Pos-Sts', on='Cmd:Opn-Cmd', off='Cmd:Cls-Cmd', beam=None, icon_size='big', **kwargs):
        super().__init__(beam=beam, icon_size=icon_size, **kwargs)
        
        self.PVbase = PVbase
        self.PVstatus = status
        self.PVon = on
        self.PVoff = off

        self.PVdevice_status = epics.PV(self.PVbase+self.PVstatus)
        self.PVdevice_on = epics.PV(self.PVbase+self.PVon)
        self.PVdevice_off = epics.PV(self.PVbase+self.PVoff)
        
    def on(self):
        self.PVdevice_on.put(1)
        time.sleep(1)

    def off(self):
        self.PVdevice_off.put(1)
        time.sleep(1)

    def refresh(self, deck, key, state):
        self.state = ( self.PVdevice_status.get()==0 )
        return self.state

    
class FEShutter(BeamElementPV):
    def __init__(self, PVbase='XF:11BM-PPS{Sh:FE}', **kwargs):
        super().__init__(PVbase=PVbase, **kwargs)
    
    def style(self, state):
        name = "FEShutter"
        icon = "empty{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "FE\nShutter"
        return name, icon, font, label
    

    
class PhotonShutter(BeamElementPV):
    def __init__(self, PVbase='XF:11BMA-PPS{PSh}', **kwargs):
        super().__init__(PVbase=PVbase, **kwargs)
    
    def style(self, state):
        name = "PhotonShutter"
        icon = "empty{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "Photon\nShutter"
        return name, icon, font, label


class ExperimentalShutter(BeamElement):
    def style(self, state):
        name = "ExperimentalShutter"
        icon = "empty{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "Exp.\nShutter"
        return name, icon, font, label
    
    def on(self):
        self.beam.on()
    def off(self):
        self.beam.off()
    def refresh(self, deck, key, state):
        self.state = self.beam.is_on()
        return self.state
    
class FS4(BeamElement):
    def style(self, state):
        name = "FS4"
        icon = "empty{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "fs4"
        return name, icon, font, label

    def get_color(self):
        if self.state:
            return "#00FF00"
        else:
            return "#FFFF00"
    
    def on(self):
        pass
    def off(self):
        pass
    def refresh(self, deck, key, state):
        return None # TODO


class GateValve(BeamElement):
    def style(self, state):
        name = "GateValve"
        icon = "empty{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "GV"
        return name, icon, font, label
    
    def on(self):
        pass
    def off(self):
        pass
    def refresh(self, deck, key, state):
        return None # TODO

    
class CMSHelp(Key):
    def style(self, state):
        name = "Help"
        #icon = "empty{}.png".format("-Pressed" if state else "-Released")
        icon = "beamline/CMS{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = ""
        return name, icon, font, label
    
    def get_color(self):
        return "#0000FF"
    
    def action(self):
        os.system('xdg-open http://gisaxs.com/CS/index.php/CMS')

    def refresh(self, deck, key, state):
        return None
        
        
        
class ChamberToggle(BigText):
    def __init__(self, beamline=None, font_size=18, **kwargs):
        super().__init__(font_size=font_size, **kwargs)
        self.beamline = beamline
        self.pumped_name = 'pumped' 
        self.value = 'vented'

    def get_color(self):
        if self.value==self.pumped_name:
            return "#0000FF"
        else:
            return "#000000"

    def style(self, state):
        name = "Chamber Toggle"
        icon = "empty{}.png".format("-Pressed" if state else "-Released")
        
        font = "Roboto-Regular.ttf"
        if self.value==self.pumped_name:
            label = "Vent\nChamber"
        else:
            label = "Pump\nChamber"
        return name, icon, font, label

    def action(self):
        if self.value==self.pumped_name:
            self.beamline.ventChamber()
        else:
            self.beamline.pumpChamber()

    def refresh(self, deck, key, state):
        # TODO: determine current state
        self.value = 'pumped'
        return self.value
    
    
class BeamlineModeToggle(Key):
    def __init__(self, beamline=None, **kwargs):
        super().__init__(**kwargs)
        self.beamline = beamline
        self.mode_alignment_name = 'alignment'
        self.value = 'alignment'
    
    def style(self, state):
        name = "Beamline Mode"
        
        font = "Roboto-Regular.ttf"
        if self.valueself.mode_alignment_name:
            icon = "beamline/measure.png"
            label = "Measure"
        else:
            icon = "beamline/align.png"
            label = "Align"
        return name, icon, font, label
    
    def action(self, extra_check='startup'):
        if self.value==self.mode_alignment_name:
            window_inject('cms.modeMeasurement()', extra_check=extra_check)
        else:
            window_inject('cms.modeAlignment()', extra_check=extra_check)

    def refresh(self, deck, key, state):
        # TODO: determine current state
        #self.value = self.beamline.mode
        self.value = 'measurement'
        return self.value
    
        
        

# Key maps
########################################
# Assign Key() objects to the various buttons ont he StreamDeck

#  0  1  2  3  4
#  5  6  7  8  9
# 10 11 12 13 14
 
key_map_beam = {
    # Row 1
    0 : GateValve() , # TODO
    1 : FS4() , # TODO
    2 : ExperimentalShutter(beam=beam) ,
    3 : PhotonShutter() ,
    4 : FEShutter() ,
    # Row 2
    5 : ChamberPressure(beamline=get_beamline()) ,
    6 : Diamond(beam=beam) ,
    7 : Transmission(beam=beam) ,
    8 : IonChamber(beam=beam) ,
    9 : RingCurrent(beam=beam) ,
    # Row 3
    10 : ChamberToggle(beamline=get_beamline()) , # TODO
    #11 : ,
    12 : BeamlineModeToggle(beamline=get_beamline()) , # TODO
    13 : Timer() ,
    14 : CMSHelp(icon_size='big') ,
    }




if True:
    # Run in the bsui environment:
    # %run -i /nsls2/xf11bm/software/ui/deck/main/keys_beam.py
    
    monitor = Monitor([key_map_beam, key_map_empty])
    monitor.monitor(reverse=False, monitor_window=False, verbosity=3)
    
    
    
    
    
  
