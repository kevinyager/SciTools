#!/usr/bin/env python3

from keys_main import *
import subprocess
 


class TBird_Check(Key):
    def style(self, state):
        name = "Check"
        icon = "mail/check{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "" if state else "Check"
        return name, icon, font, label
    def action(self):
        os.system('xdotool key "Shift+F5"')
 

class TBird_MoveAgain(Key):
    def style(self, state):
        name = "MoveAgain"
        icon = "mail/move{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "Move Again"
        return name, icon, font, label
    def action(self):
        os.system('xdotool key "Ctrl+Shift+M"')



class TBird_MoveSpecial(Key):
    def __init__(self, sequence, label=None, **kwargs):
        super().__init__(**kwargs)
        self.sequence = sequence
        self.label = label
            
    def style(self, state):
        name = "MoveSpecial"
        icon = "mail/move{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        if self.label:
            label = self.label
        else:
            label = "Moving" if state else "Move"
        return name, icon, font, label
    def action(self):
        os.system('xdotool key "Menu"')
        os.system('xdotool key "M"')
        for i in range(2):
            os.system('xdotool key "Down"')
        os.system('xdotool key "Right"')
        # Local Folders >

        for istep, num_presses in enumerate(self.sequence):
            for i in range(num_presses):
                os.system('xdotool key "Down"')
            os.system('xdotool key "Right"')
        
        os.system('xdotool key "Return"')
        
        
class TBird_ToggleHTML(Key):
    def style(self, state):
        name = "ToggleHTML"
        icon = "mail/html{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = ""
        return name, icon, font, label
    
    def action(self):
        # WARNING: Not working
        os.system('xdotool key "Alt+E"')
        time.sleep(0.1)
        os.system('xdotool key "A"')
        time.sleep(0.5)
        
        os.system('xdotool key "Home"')
        time.sleep(0.2)
        os.system('xdotool key "Down"')
        os.system('xdotool key "Down"')
        os.system('xdotool key "Down"')
        
        time.sleep(0.1)
        
        os.system('xdotool key "Alt+C"')
        
        #os.system('xdotool key "Return"')

 
 
# Key maps
########################################
# Assign Key() objects to the various buttons on the StreamDeck

#  0  1  2  3  4
#  5  6  7  8  9
# 10 11 12 13 14


key_map_thunderbird = {
    0 : TBird_Check() ,
    5 : Timer() ,
    10 : Clock() ,
    11 : TBird_ToggleHTML(icon_size="big") ,
    1 : TBird_MoveSpecial([7,6,4], label="2019 review") ,
    4 : TBird_MoveSpecial([4], label="Manage") ,
    14 : TBird_MoveAgain() ,
    }


key_map_kwrite = {
    5 : Timer() ,
    10 : Clock() ,
    }

