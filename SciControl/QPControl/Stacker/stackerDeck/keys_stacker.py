#!/usr/bin/env python3

from keys_main import *
#import subprocess

LONG_PRESS = 0.8

# Connect to QPress Stacker
########################################

import sys
#Code_PATH='D:/QPress/Stacker/control_software/19-Stacker/stacker'
#Code_PATH='/home/yager/Desktop/stacker/'
Code_PATH='../stacker/'
Code_PATH in sys.path or sys.path.append(Code_PATH)

from Stacker import *
print('Stacker version {}'.format(STACKER_VERSION))

common = Common(logdir='./logs/')
AUTH='Cah2zawipu3Gohw2eFo1aec4ohPhah8u' # Authentication token    
stacker = Stacker(name='stackerDeck', mode='client', authentication_token=AUTH, common=common, verbosity=4, log_verbosity=2)
stacker.client_connect_to_server()

stacker.sam._step_sizing_translation = 1.0
stacker.sam._step_sizing_rotation = 10.0

#stacker.cam._step_sizing_translation = 0.1

stacker.stmp._step_sizing_translation = 0.1
stacker.stmp._step_sizing_rotation = 0.2

stacker.sam.use_cache = True
stacker.cam.use_cache = True
stacker.stmp.use_cache = True



    

# Key definitions
########################################
# To determine a keystroke name:
#  xev -event keyboard
# Some nice arrow icons:
#  http://icons.deanishe.net/preview/fontawesome    



# Main motion keys
########################################

class sam_Left(Key):
    def style(self, state):
        name = "sam_Left"
        icon = "arrows/left{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        #npos = stacker.sam.x() - stacker.sam._step_sizing_translation
        #label = "x={:.2f}".format(npos) if state else "-x"
        label = '-x'
        return name, icon, font, label
    def action(self):
        stacker.sam.xr(-stacker.sam._step_sizing_translation)

class sam_Right(Key):
    def style(self, state):
        name = "sam_Right"
        icon = "arrows/right{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        #npos = stacker.sam.x() + stacker.sam._step_sizing_translation
        #label = "x={:.2f}".format(npos) if state else "+x"
        label = '+x'
        return name, icon, font, label
    def action(self):
        stacker.sam.xr(+stacker.sam._step_sizing_translation)

class sam_Up(Key):
    def style(self, state):
        name = "sam_Up"
        icon = "arrows/up{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        #npos = stacker.sam.x() + stacker.sam._step_sizing_translation
        #label = "y={:.2f}".format(npos) if state else "+y"
        label = '+y'
        return name, icon, font, label
    def action(self):
        stacker.sam.yr(+stacker.sam._step_sizing_translation)

class sam_Down(Key):
    def style(self, state):
        name = "sam_Down"
        icon = "arrows/down{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        #npos = stacker.sam.x() - stacker.sam._step_sizing_translation
        #label = "y={:.2f}".format(npos) if state else "-y"
        label = '-y'
        return name, icon, font, label
    def action(self):
        stacker.sam.yr(-stacker.sam._step_sizing_translation)

class sam_CCW(Key):
    def style(self, state):
        name = "sam_CCW"
        icon = "arrows/ccw_b{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        #npos = stacker.sam.phi() - stacker.sam._step_sizing_rotation
        #label = "phi={:.2f}".format(npos) if state else "-phi"
        label = '-phi'
        return name, icon, font, label
    def action(self):
        stacker.sam.phir(-stacker.sam._step_sizing_rotation)
class sam_CW(Key):
    def style(self, state):
        name = "sam_CW"
        icon = "arrows/cw_b{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        #npos = stacker.sam.phi() + stacker.sam._step_sizing_rotation
        #label = "phi={:.2f}".format(npos) if state else "+phi"
        label = '+phi'
        return name, icon, font, label
    def action(self):
        stacker.sam.phir(+stacker.sam._step_sizing_rotation)


class gotoMark(BigText):
    def __init__(self, stage, mark_name, icon_size='big', font_size=20, **kwargs):
        super().__init__(icon_size=icon_size, font_size=font_size, **kwargs)
        self.stage = stage
        self.mark_name = mark_name
        self.exists = self.mark_name in self.stage.marks()
        
    def get_color(self, state=False):
        if state:
            return "#00FF00"
        else:
            if self.exists:
                return "#0000FF"
            else:
                return "#000044"

    def style(self, state):
        name = "empty"
        icon = "empty{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "set\nmark..." if state else "goto\n{}".format(self.mark_name)
        return name, icon, font, label

    def action(self):
        pass
    def release_action(self):
        if self.held_time>LONG_PRESS:
            self.stage.mark(self.mark_name)
            self.exists = True
            self.update()
        else:
            if self.mark_name in self.stage.marks():
                self.exists = True
                self.stage.goto(self.mark_name)
                self.update()

        

                

class gotoOrigin(gotoMark):
    def __init__(self, stage, mark_name='origin', icon_size='big', font_size=20, **kwargs):
        super().__init__(stage=stage, mark_name=mark_name, icon_size=icon_size, font_size=font_size, **kwargs)
        self.exists = True
    
    def style(self, state):
        name = "empty"
        icon = "empty{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "goto\nOrigin"
        return name, icon, font, label

    def release_action(self):
        if self.held_time>LONG_PRESS:
            self.stage.setOrigin()
        else:
            self.stage.gotoOrigin()

class gotoOriginSam(gotoOrigin):
    def __init__(self, mark_name='origin', icon_size='big', font_size=20, **kwargs):
        super().__init__(stage=stacker.sam, mark_name=mark_name, icon_size=icon_size, font_size=font_size, **kwargs)
    
    def release_action(self):
        if self.held_time>LONG_PRESS:
            self.stage.setOrigin()
        else:
            self.stage.xvel(1)
            self.stage.yvel(1)
            self.stage.gotoOrigin()

class gotoOriginXY(gotoOrigin):
    def style(self, state):
        name = "empty"
        icon = "empty{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "goto\n(0,0)"
        return name, icon, font, label

    def release_action(self):
        if self.held_time>LONG_PRESS:
            self.stage.setOrigin(['x', 'y'])
        else:
            self.stage.xvel(1)
            self.stage.yvel(1)
            self.stage.gotoOrigin(['x', 'y'])

class sam_UpDown(Key):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state_up = False # False means down
    
    def style(self, state):
        name = "sam_UpDown"
        if self.state_up:
            icon = "arrows/chevron-circle-down-purple{}.png".format("-Pressed" if state else "-Released")
            label = "down"
        else:
            icon = "arrows/chevron-circle-up-purple{}.png".format("-Pressed" if state else "-Released")
            label = "up"
        font = "Roboto-Regular.ttf"
        
        return name, icon, font, label
    def action(self):
        if self.state_up:
            stacker.sam.down()
            self.state_up = False
        else:
            stacker.sam.up()
            self.state_up = True

class sam_HoldRelease(Key):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state_holding = False
    
    def style(self, state):
        name = "sam_HoldRelease"
        if self.state_holding:
            icon = "arrows/chevron-circle-up-purple{}.png".format("-Pressed" if state else "-Released")
            label = "release"
        else:
            icon = "arrows/chevron-circle-down-purple{}.png".format("-Pressed" if state else "-Released")
            label = "hold"
        font = "Roboto-Regular.ttf"
        
        return name, icon, font, label
    def action(self):
        if self.state_holding:
            stacker.sam.release()
            self.state_holding = False
        else:
            stacker.sam.hold()
            self.state_holding = True

# No longer being used:
class sam_phi_ValueRing(ValueRing):
    #def __init__(self, **kwargs):
        #super().__init__(**kwargs)

    def style(self, state):
        name = "empty"
        icon = "empty{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "deg"
        return name, icon, font, label

    def get_value(self, vmin=-180, vmax=+180):
        return super().get_value(vmin=vmin, vmax=vmax)

    def action(self):
        stacker.sam.phiabs(0)

    def refresh(self, deck, key, state):
        ret = stacker.sam.phi__cache()
        if isinstance(ret, (int, float)):
            self.value = ret
        return self.value




class sam_phi_OriRing(ValueRing):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.value = 0

    def style(self, state):
        name = "empty"
        icon = "empty{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "phi"
        return name, icon, font, label

    def get_value(self, vmin=-180, vmax=+180):
        if self.value is None:
            return 0
        return super().get_value(vmin=vmin, vmax=vmax)

    def get_color(self, vmin=-180, vmax=+180):
        #value = self.get_value(vmin=vmin, vmax=vmax)
        
        if self.value is None:
            return "rgb({:d},{:d},{:d})".format(255,200,0) # Orange
        
        r, g, b = 0, 255, 252 # Default 'rotation blue'
        if self.value<=-120 or self.value>=+100:
            r, g, b = 255, 0, 0 # Red
        elif self.value<=-90 or self.value>=+90:
            r, g, b = 255, 255, 0 # Yellow
        #print(self.value, value, r, g, b)
        
        return "rgb({:d},{:d},{:d})".format(r,g,b)

    def render_key_image(self, deck, icon_filename, font_filename, label_text, state=False):
        # Create new key image of the correct dimensions, black background
        image = PILHelper.create_image(deck)
        draw = ImageDraw.Draw(image)
        
        fill = self.get_color()
        
        draw.rectangle( [(0, 0), (image.width, image.height)], fill=fill)
        
        inset = 5
        bbox = [inset, inset, image.width-inset, image.height-inset]
        #a = self.gap_for_label
        a = 0
        b = 10 # width of marker
        span = ( 90-a -(-270+a) )
        vangle = self.get_value()*span
        draw.pieslice(bbox, -270+a, 90-a, fill="black")
        draw.pieslice(bbox, -270+a+vangle-b, -270+a+vangle+b, fill="white")
        inset = 17
        bbox = [inset, inset, image.width-inset, image.height-inset]
        draw.ellipse(bbox, fill=fill)

        label_extra = "None" if self.value is None else "{:.1f}".format(self.value)
        font = ImageFont.truetype(font_filename, 12)
        label_w, label_h = draw.textsize(label_extra, font=font)
        label_pos = ( (image.width - label_w) // 2, (image.height - label_h) // 2 )
        draw.text(label_pos, text=label_extra, font=font, fill="black")


        font = ImageFont.truetype(font_filename, 14)
        label_w, label_h = draw.textsize(label_text, font=font)
        label_pos = ((image.width - label_w) // 2, image.height - 20)
        draw.text(label_pos, text=label_text, font=font, fill="white")
        
        return PILHelper.to_native_format(deck, image)

    def action(self):
        stacker.sam.phiabs(0)

    def refresh(self, deck, key, state):
        #return_value = stacker.sam.pos__cache()
        #self.value = return_value['phi']
        ret = stacker.sam.phi__cache()
        if isinstance(ret, (int, float)):
            self.value = ret
        
        return self.value



class sam_pos(BigText):
    def __init__(self, font_size=16, **kwargs):
        super().__init__(font_size=font_size, **kwargs)
        self.value = 0
        self.positions = {'x': -99, 'y': -99, 'phi': -360}
        
    def get_color(self, state=False):
        return "#000000"

    def style(self, state):
        name = "empty"
        icon = "empty{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        #label = "Pressed" if state else "Key {}".format(self.get_key_idx())
        label = "x {x:.3f}\ny {y:.3f}\nphi {phi:.2f}".format(**self.positions)
        return name, icon, font, label
    
    
    def action(self):
        #stacker.sam.gotoOrigin()
        pass

    def refresh(self, deck, key, state):
        ret = stacker.sam.pos__cache()
        if isinstance(ret, dict):
            self.positions = ret
        self.value += 1
        
        return self.value




# Select speed (step size and velocity)
########################################

class ToggleGroup():
    def __init__(self, n):
        self.n = n
        self.current = 0

    def activate(self, idx):
        if idx<0 or idx>self.n:
            print('ERROR: invalid idx {} to ToggleGroup.activate'.format(idx))
        self.current = idx

        
class sam_SpeedGroup(ToggleGroup):
    # 4 - very fast
    # 3 - fast
    # 2 - normal
    # 1 - slow
    # 0 - very slow
    def __init__(self, n=5):
        self.n = n
        self.current = 2
        self.buttons = []
        
        self.speed = {
            'vslow': 0.0025, # 2.5 micron
            'slow' : 0.010, # 10 microns
            'normal' : 0.05,
            'fast' : 0.5,
            'vfast' : 2,
            }
        self.velocity = {
            'vslow': 0.1,
            'slow' : 0.1,
            'normal' : 1,# 1 mm/2
            'fast' : 1,
            'vfast' : 1,
            }        
        #self.speed_camera = {
            #'vslow': 0.0016,
            #'slow' : 0.0035,
            #'normal' : 0.035,
            #'fast' : 0.014,
            #'vfast' : 0.14,
            #}
        self.speed_rot = {
            'vslow': 0.1, 
            'slow' : 1.0,
            'normal' : 5.0,
            'fast' : 30,
            'vfast' : 90,
            }
        self.velocity_rot = {
            'vslow': 0.5, 
            'slow' : 0.5,
            'normal' : 5.0,
            'fast' : 5,
            'vfast' : 5,
            }        
        
    def activate(self, name):
        if name=='vslow':
            ibutton = 0
        elif name=='slow':
            ibutton = 0
        elif name=='normal' or name=='vnormal':
            ibutton = 1
        elif name=='fast':
            ibutton = 2
        elif name=='vfast':
            ibutton = 2
        else:
            print('ERROR: invalid name ({}) to sam_SpeedGroup.activate'.format(name))
            
        for i, button in enumerate(self.buttons):
            if i==ibutton:
                button.selected = True
            else:
                button.selected = False
                button.very_state = False
            if hasattr(button, 'parent_deck'):
                button.update()
            
        stacker.sam._step_sizing_translation = self.speed[name]
        stacker.sam._step_sizing_rotation = self.speed_rot[name]
        
        stacker.sam.xvel(self.velocity[name])
        stacker.sam.yvel(self.velocity[name])
        stacker.sam.phivel(self.velocity_rot[name])

            
        


class key_Speed(BigText):
    def __init__(self, parent, name='<none>', **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.parent = parent
        self.selected = False
        self.very_state = False
    
    def get_color(self, state=False):
        return "#000000"

    def style(self, state):
        name = "sam_Speed"
        if self.selected:
            if self.very_state:
                icon = "toggle/tselected2.png"
            else:
                icon = "toggle/tselected.png"
        else:
            icon = "empty{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "v. {}".format(self.name) if self.very_state else self.name
        
        return name, icon, font, label

    #def render_key_image(self, deck, icon_filename, font_filename, label_text, show_icon=True, state=False):
        #return super().render_key_image(deck=deck, icon_filename=icon_filename, font_filename=font_filename, label_text=label_text, show_icon=show_icon, state=state)
    
    def render_key_image(self, deck, icon_filename, font_filename, label_text, show_icon=True, state=False):
        # Create new key image of the correct dimensions, black background
        image = PILHelper.create_image(deck)
        draw = ImageDraw.Draw(image)
        
        draw.rectangle( [(0, 0), (image.width, image.height)], fill=self.get_color(state=state))

        if show_icon:
            icon = Image.open(icon_filename).convert("RGBA")
            if self.icon_size=='big':
                icon.thumbnail((image.width, image.height), Image.LANCZOS)
            else:
                icon.thumbnail((image.width, image.height - 20), Image.LANCZOS)
            icon_pos = ((image.width - icon.width) // 2, 0)
            image.paste(icon, icon_pos, icon)

        # Load a custom TrueType font and use it to overlay the key index, draw key
        # label onto the image
        font = ImageFont.truetype(font_filename, self.font_size)
        label_w, label_h = draw.textsize(label_text, font=font)
        #label_pos = ( (image.width - label_w) // 2, (image.height - label_h) //2 ) # Center
        label_pos = ( (image.width - label_w)//2 , int( (image.height - label_h)*0.15 ) ) # Top
        draw.text(label_pos, text=label_text, font=font, fill="white", align="center")
        
        
        label_text = self.get_speed_text()
        font = ImageFont.truetype(font_filename, 14)
        label_w, label_h = draw.textsize(label_text, font=font)
        label_pos = ( (image.width - label_w)//2 , int( (image.height - label_h)*0.75 ) ) # Bottom
        draw.text(label_pos, text=label_text, font=font, fill="white", align="center")

        return PILHelper.to_native_format(deck, image)

    def get_speeds(self):
        if self.very_state:
            trans, rot = self.parent.speed['v'+self.name], self.parent.speed_rot['v'+self.name]
        else:
            trans, rot = self.parent.speed[self.name], self.parent.speed_rot[self.name]
        return trans, rot
    
    def get_speed_text(self):
        trans, rot = self.get_speeds()
        if trans<0.1:
            label_text = "{}µm".format(trans*1000)
        else:
            label_text = "{}mm".format(trans)
        
        label_text += "\n{}°".format(rot)
        return label_text

    def action(self):
        self.selected = True
    def release_action(self):
        if self.held_time>LONG_PRESS and self.name!='normal':
            self.very_state = True
            self.parent.activate('v{}'.format(self.name))
        else:
            self.very_state = False
            self.parent.activate(self.name)


class key_SpeedT(key_Speed):
    def get_speeds(self):
        if self.very_state:
            trans = self.parent.speed['v'+self.name]
        else:
            trans = self.parent.speed[self.name]
        return trans
    def get_speed_text(self):
        trans = self.get_speeds()
        if trans<0.1:
            label_text = "step = \n{}µm".format(trans*1000)
        else:
            label_text = "step = \n{}mm".format(trans)
        return label_text

class key_SpeedR(key_Speed):
    def get_speeds(self):
        if self.very_state:
            rot = self.parent.speed_rot['v'+self.name]
        else:
            rot = self.parent.speed_rot[self.name]
        return rot
    def get_speed_text(self):
        rot = self.get_speeds()
        if rot<0.1:
            label_text = "step = \n{}m°".format(rot*1000)
        else:
            label_text = "step = \n{}°".format(rot)
        return label_text            


sam_speed_group = sam_SpeedGroup()
sam_speed_group.buttons.append( key_Speed(name='slow', parent=sam_speed_group) )
sam_speed_group.buttons.append( key_Speed(name='normal', parent=sam_speed_group) )
sam_speed_group.buttons.append( key_Speed(name='fast', parent=sam_speed_group) )
#sam_speed_group.buttons[1].selected = True
sam_speed_group.activate('normal')



# Sample velocity control (sub-menu)
########################################
velocity_step = 2.0


class sam_xvelUp(Key):
    def style(self, state):
        name = "sam_xvelUp"
        icon = "arrows/triangle-up{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        #nvel = stacker.sam.xvel()*velocity_step
        #label = "xvel={:.2f}".format(nvel) if state else "+xvel"
        label = '+xvel'
        return name, icon, font, label
    def action(self):
        nvel = stacker.sam.xvel()
        if isinstance(nvel, (int, float)):
            stacker.sam.xvel(nvel*velocity_step)
class sam_xvelDown(Key):
    def style(self, state):
        name = "sam_xvelDown"
        icon = "arrows/triangle-down{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        #nvel = stacker.sam.xvel()/velocity_step
        #label = "xvel={:.2f}".format(nvel) if state else "-xvel"
        label = '-xvel'
        return name, icon, font, label
    def action(self):
        nvel = stacker.sam.xvel()
        if isinstance(nvel, (int, float)):
            stacker.sam.xvel(nvel/velocity_step)

class sam_yvelUp(Key):
    def style(self, state):
        name = "sam_yvelUp"
        icon = "arrows/triangle-up{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        #nvel = stacker.sam.yvel()*velocity_step
        #label = "yvel={:.2f}".format(nvel) if state else "+yvel"
        label = '+yvel'
        return name, icon, font, label
    def action(self):
        nvel = stacker.sam.yvel()
        if isinstance(nvel, (int, float)):
            stacker.sam.yvel(nvel*velocity_step)
class sam_yvelDown(Key):
    def style(self, state):
        name = "sam_yvelDown"
        icon = "arrows/triangle-down{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        #nvel = stacker.sam.yvel()/velocity_step
        #label = "yvel={:.2f}".format(nvel) if state else "-yvel"
        label = '-yvel'
        return name, icon, font, label
    def action(self):
        nvel = stacker.sam.yvel()
        if isinstance(nvel, (int, float)):
            stacker.sam.yvel(nvel/velocity_step)



class sam_xyvelUp(Key):
    def style(self, state):
        name = "sam_xyvelUp"
        icon = "arrows/triangle-up{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        #nvel = stacker.sam.xvel()*velocity_step
        #label = "xvel={:.2f}".format(nvel) if state else "+xvel"
        label = '+xyvel'
        return name, icon, font, label
    def action(self):
        nvel = stacker.sam.xvel()
        if isinstance(nvel, (int, float)):
            stacker.sam.xvel(nvel*velocity_step)
            stacker.sam.yvel(nvel*velocity_step)
class sam_xyvelDown(Key):
    def style(self, state):
        name = "sam_xyvelDown"
        icon = "arrows/triangle-down{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        #nvel = stacker.sam.xvel()/velocity_step
        #label = "xvel={:.2f}".format(nvel) if state else "-xvel"
        label = '-xyvel'
        return name, icon, font, label
    def action(self):
        nvel = stacker.sam.xvel()
        if isinstance(nvel, (int, float)):
            stacker.sam.xvel(nvel/velocity_step)
            stacker.sam.yvel(nvel/velocity_step)


class sam_phivelUp(Key):
    def style(self, state):
        name = "sam_phivelUp"
        icon = "arrows/triangle-up-b{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        #nvel = stacker.sam.phivel()*velocity_step
        #label = "phivel={:.2f}".format(nvel) if state else "+phivel"
        label = '+phivel'
        return name, icon, font, label
    def action(self):
        nvel = stacker.sam.phivel()
        if isinstance(nvel, (int, float)):
            stacker.sam.phivel(nvel*velocity_step)
class sam_phivelDown(Key):
    def style(self, state):
        name = "sam_phivelDown"
        icon = "arrows/triangle-down-b{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        #nvel = stacker.sam.phivel()/velocity_step
        #label = "phivel={:.2f}".format(nvel) if state else "-phivel"
        label = '-phivel'
        return name, icon, font, label
    def action(self):
        nvel = stacker.sam.phivel()
        if isinstance(nvel, (int, float)):
            stacker.sam.phivel(nvel/velocity_step)




class sam_vel_ValueRing(ValueRing):
    def __init__(self, motor_name, vmin=0, vmax=1, vtypical=0.5, **kwargs):
        super().__init__(**kwargs)
        self.motor_name = motor_name
        self.vmin, self.vmax = vmin, vmax
        self.vtypical = vtypical
        

    def style(self, state):
        name = "empty"
        icon = "empty{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "°/s" if self.motor_name=='phi' else "mm/s"
        if self.value<0.1:
            label = "m°/s" if self.motor_name=='phi' else "µm/s"
        return name, icon, font, label

    def get_color(self, vmin=None, vmax=None, state=False):
        value = self.get_value(vmin=vmin, vmax=vmax)
        value = np.clip(value, 0, 1)
        r, g, b = 0, 0, 0
        if value<0.1:
            b = (value/0.1)
        else:
            extent = (value-0.1)/0.9
            r = extent
            b = 1-extent
        
        return "rgb({:d},{:d},{:d})".format(int(r*255),int(g*255),int(b*255))
    
    def get_value(self, vmin=None, vmax=None):
        if vmin==None:
            vmin = self.vmin
        if vmax==None:
            vmax = self.vmax
        return super().get_value(vmin=vmin, vmax=vmax)

    
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

        if self.value is None:
            label_extra = "None"
        elif self.value<0.1:
            label_extra = "{:.0f}".format(self.value*1000)
        else:
            label_extra = "{:.1f}".format(self.value)
        font = ImageFont.truetype(font_filename, 16)
        label_w, label_h = draw.textsize(label_extra, font=font)
        label_pos = ( (image.width - label_w) // 2, (image.height - label_h) // 2 )
        draw.text(label_pos, text=label_extra, font=font, fill="white")


        font = ImageFont.truetype(font_filename, 14)
        label_w, label_h = draw.textsize(label_text, font=font)
        label_pos = ((image.width - label_w) // 2, image.height - 20)
        draw.text(label_pos, text=label_text, font=font, fill="white")
        
        return PILHelper.to_native_format(deck, image)

    def action(self):
        if self.motor_name=='x':
            nvel = stacker.sam.xvel(self.vtypical)
            nvel = stacker.sam.yvel(self.vtypical)
            if isinstance(nvel, (int, float)):
                self.value = nvel
        elif self.motor_name=='y':
            nvel = stacker.sam.yvel(self.vtypical)
            if isinstance(nvel, (int, float)):
                self.value = nvel
        elif self.motor_name=='phi':
            nvel = stacker.sam.phivel(self.vtypical)
            if isinstance(nvel, (int, float)):
                self.value = nvel
        
    def refresh(self, deck, key, state):
        if self.motor_name=='x':
            nvel = stacker.sam.xvel__cache()
            if isinstance(nvel, (int, float)):
                self.value = nvel
        elif self.motor_name=='y':
            nvel = stacker.sam.yvel__cache()
            if isinstance(nvel, (int, float)):
                self.value = nvel
        elif self.motor_name=='phi':
            nvel = stacker.sam.phivel__cache()
            if isinstance(nvel, (int, float)):
                self.value = nvel
        
        return self.value




# Menus
########################################
class SamMenu(Key):
    def __init__(self, menu_name='Menu', **kwargs):
        super().__init__(**kwargs)
        self.menu_name = menu_name
    
    def style(self, state):
        name = "Menu"
        icon = "grid{}.png".format("-Pressed" if state else "-Released")
        #<div>Icons made by <a href="https://www.flaticon.com/authors/elegant-themes" title="Elegant Themes">Elegant Themes</a> from <a href="https://www.flaticon.com/" 			    title="Flaticon">www.flaticon.com</a> is licensed by <a href="http://creativecommons.org/licenses/by/3.0/" 			    title="Creative Commons BY 3.0" target="_blank">CC 3.0 BY</a></div>
        font = "Roboto-Regular.ttf"
        label = self.menu_name
        return name, icon, font, label
    def action(self):
        swap_key_map(self.parent_deck, key_map_sam_menu)
class SamMenuCam(SamMenu):
    def action(self):
        swap_key_map(self.parent_deck, key_map_stacker_cam)

class SwapToSamMain(Key):
    def style(self, state):
        name = "Back"
        icon = "undo{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "Back"
        return name, icon, font, label
    def action(self):
        swap_key_map(self.parent_deck, key_map_stacker_sam)




# Camera controls
########################################

class cam_UpDown(Key):
    def __init__(self, direction, speed='normal', **kwargs):
        super().__init__(**kwargs)
        self.direction = direction
        self.speed = speed
        if self.speed=='fast':
            self.step_size = 1
        elif self.speed=='slow':
            self.step_size = 0.0016
        else:
            # Normal
            self.step_size = 0.05
        
        if self.direction=='down':
            self.step_size *= -1
    
    def style(self, state):
        name = "cam_UpDown"
        s = ''
        if self.speed=='fast':
            s = 'Big'
        elif self.speed=='slow':
            s = 'Small'
        if self.direction=='up':
            icon = "arrows/up{}-purple{}.png".format(s, "-Pressed" if state else "-Released")
        else:
            icon = "arrows/down{}-purple{}.png".format(s, "-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        #npos = stacker.sam.x() - stacker.sam._step_sizing_translation
        #label = "x={:.2f}".format(npos) if state else "-x"
        label = '+' if self.direction=='up' else ''
        if abs(self.step_size)>=0.5:
            label = '{}{:.1f}mm'.format(label, self.step_size)
        else:
            label = '{}{:.1f}µm'.format(label, self.step_size*1000)
        
        
        
        return name, icon, font, label
    def action(self):
        stacker.cam.zr(self.step_size)

class cam_pos(BigText):
    def __init__(self, font_size=16, **kwargs):
        super().__init__(font_size=font_size, **kwargs)
        self.value = 0
        self.positions = {'z': -99}
        
    def get_color(self, state=False):
        return "#000000"

    def style(self, state):
        name = "empty"
        icon = "empty{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        #label = "Pressed" if state else "Key {}".format(self.get_key_idx())
        label = "cam.z\n{z:.3f}".format(**self.positions)
        return name, icon, font, label
    
    
    def action(self):
        pass
        #stacker.sam.gotoOrigin()

    def refresh(self, deck, key, state):
        ret = stacker.cam.pos__cache()
        if isinstance(ret, dict):
            self.positions = ret
        self.value += 1
        
        return self.value


class followMarkCam(gotoMark):
    def __init__(self, mark_name, icon_size='big', font_size=20, **kwargs):
        super().__init__(mark_name=mark_name, icon_size=icon_size, font_size=font_size, **kwargs)
        self.selected = False

    def get_color(self, state=False):
        return "#000000"


    def style(self, state):
        name = "followMarkCam"
        if self.selected:
            icon = "toggle/tselected_green.png"
        else:
            icon = "empty{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "set\nmark..." if state else "follow\n{}".format(self.mark_name)
        
        return name, icon, font, label

    #def render_key_image(self, deck, icon_filename, font_filename, label_text, show_icon=True, state=False):
        #super().render_key_image(deck=deck, icon_filename=icon_filename, font_filename=font_filename, label_text=label_text, show_icon=show_icon, state=state)
    def render_key_image(self, deck, icon_filename, font_filename, label_text, show_icon=True, state=False):
        # Create new key image of the correct dimensions, black background
        image = PILHelper.create_image(deck)
        draw = ImageDraw.Draw(image)
        
        draw.rectangle( [(0, 0), (image.width, image.height)], fill=self.get_color(state=state))

        if show_icon:
            icon = Image.open(icon_filename).convert("RGBA")
            if self.icon_size=='big':
                icon.thumbnail((image.width, image.height), Image.LANCZOS)
            else:
                icon.thumbnail((image.width, image.height - 20), Image.LANCZOS)
            icon_pos = ((image.width - icon.width) // 2, 0)
            image.paste(icon, icon_pos, icon)

        # Load a custom TrueType font and use it to overlay the key index, draw key
        # label onto the image
        font = ImageFont.truetype(font_filename, self.font_size)
        label_w, label_h = draw.textsize(label_text, font=font)
        label_pos = ( (image.width - label_w) // 2, (image.height - label_h) //2 ) # Center
        #label_pos = ( (image.width - label_w)//2 , int( (image.height - label_h)*0.15 ) ) # Top
        draw.text(label_pos, text=label_text, font=font, fill="white", align="center")
        
        return PILHelper.to_native_format(deck, image)

    def action(self):
        pass
    def release_action(self):
        if self.selected:
            stacker.cam.unfollow()
            self.selected = False
        else:
            if self.held_time>LONG_PRESS:
                stacker.cam.mark(self.mark_name)
            stacker.cam.follow(self.mark_name)
            self.selected = True
        self.update()


# Stamp controls
########################################

class stmp_DirToggle(Key):
    def __init__(self, use=None, **kwargs):
        super().__init__(**kwargs)
        self.value = 0
        self.use = use
        

class stmp_Left(stmp_DirToggle):
    def style(self, state):
        name = "stmp_Left"
        font = "Roboto-Regular.ttf"
        if self.use.using=='xy':
            icon = "arrows/left{}.png".format("-Pressed" if state else "-Released")
            label = '-x'
        else:
            icon = "rotation/pitch_pos{}.png".format("-Pressed" if state else "-Released")
            label = '+pitch'
        return name, icon, font, label
    def action(self):
        if self.use.using=='xy':
            stacker.stmp.xr(-stacker.stmp._step_sizing_translation)
        else:
            stacker.stmp.pitchr(+stacker.stmp._step_sizing_rotation)

class stmp_Right(stmp_DirToggle):
    def style(self, state):
        name = "stmp_Right"
        font = "Roboto-Regular.ttf"
        if self.use.using=='xy':
            icon = "arrows/right{}.png".format("-Pressed" if state else "-Released")
            label = '+x'
        else:
            icon = "rotation/pitch_neg{}.png".format("-Pressed" if state else "-Released")
            label = '-pitch'
        return name, icon, font, label
    def action(self):
        if self.use.using=='xy':
            stacker.stmp.xr(+stacker.stmp._step_sizing_translation)
        else:
            stacker.stmp.pitchr(-stacker.stmp._step_sizing_rotation)

class stmp_Up(stmp_DirToggle):
    def style(self, state):
        name = "stmp_Up"
        font = "Roboto-Regular.ttf"
        if self.use.using=='xy':
            icon = "arrows/up{}.png".format("-Pressed" if state else "-Released")
            label = '+y'
        else:
            icon = "rotation/roll_pos{}.png".format("-Pressed" if state else "-Released")
            label = '+roll'
        return name, icon, font, label
    def action(self):
        if self.use.using=='xy':
            stacker.stmp.yr(+stacker.stmp._step_sizing_translation)
        else:
            stacker.stmp.rollr(+stacker.stmp._step_sizing_rotation)

class stmp_Down(stmp_DirToggle):
    def style(self, state):
        name = "stmp_Down"
        font = "Roboto-Regular.ttf"
        if self.use.using=='xy':
            icon = "arrows/down{}.png".format("-Pressed" if state else "-Released")
            label = '-y'
        else:
            icon = "rotation/roll_neg{}.png".format("-Pressed" if state else "-Released")
            label = '-roll'
        return name, icon, font, label
    def action(self):
        if self.use.using=='xy':
            stacker.stmp.yr(-stacker.stmp._step_sizing_translation)
        else:
            stacker.stmp.rollr(-stacker.stmp._step_sizing_rotation)


class stmp_RollPos(Key):
    def style(self, state):
        name = "stmp_Left"
        icon = "rotation/roll_pos{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = '+roll'
        return name, icon, font, label
    def action(self):
        stacker.stmp.rollr(+stacker.stmp._step_sizing_rotation)
class stmp_RollNeg(Key):
    def style(self, state):
        name = "stmp_Left"
        icon = "rotation/roll_neg{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = '-roll'
        return name, icon, font, label
    def action(self):
        stacker.stmp.rollr(-stacker.stmp._step_sizing_rotation)
class stmp_PitchPos(Key):
    def style(self, state):
        name = "stmp_Left"
        icon = "rotation/pitch_pos{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = '+pitch'
        return name, icon, font, label
    def action(self):
        stacker.stmp.pitchr(+stacker.stmp._step_sizing_rotation)
class stmp_PitchNeg(Key):
    def style(self, state):
        name = "stmp_Left"
        icon = "rotation/pitch_neg{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = '-pitch'
        return name, icon, font, label
    def action(self):
        stacker.stmp.pitchr(-stacker.stmp._step_sizing_rotation)





class stmp_TransRotUse(BigText):
    def __init__(self, icon_size='big', font_size=30, **kwargs):
        super().__init__(icon_size=icon_size, font_size=font_size, **kwargs)
        self.using = 'xy' # or 'tilt'
        
        self.keys = [
            stmp_Left(use=self),
            stmp_Right(use=self),
            stmp_Up(use=self),
            stmp_Down(use=self),
            ]
        
    def get_color(self, state=False):
        if self.using=='xy':
            return "#000000"
        else:
            return "#00c9c6"
    
    def style(self, state):
        name = "stmp_TransRotUse"
        icon = "empty{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto/Roboto-Bold.ttf"
        label = '[xy]\ntilt' if self.using=='xy' else 'xy\n[tilt]'
        return name, icon, font, label
    def action(self):
        if self.using=='xy':
            self.using = 'tilt'
        else:
            self.using = 'xy'
        # Flag all the keys for a refresh
        for key in self.keys:
            key.value += 1
            key.update()
            
stmp_transrotuse = stmp_TransRotUse()



class stmp_UpDown(Key):
    def __init__(self, direction, speed='normal', use=None, **kwargs):
        super().__init__(**kwargs)
        self.direction = direction
        self.speed = speed
        self.use = use
        if self.speed=='fast':
            self.step_size = 10
        elif self.speed=='slow':
            self.step_size = 0.01
        else:
            # Normal
            self.step_size = 1
        
        if self.direction=='down':
            self.step_size *= -1
            
        self.value = 0

    def refresh(self, deck, key, state):
        return self.value
    
    def style(self, state):
        name = "stmp_UpDown"
        s = ''
        if self.speed=='fast':
            s = 'Big'
        elif self.speed=='slow':
            s = 'Small'
        if self.direction=='up':
            icon = "arrows/up{}-purple{}.png".format(s, "-Pressed" if state else "-Released")
        else:
            icon = "arrows/down{}-purple{}.png".format(s, "-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        if self.use.using=='z':
            label = '+z' if self.direction=='up' else '-z'
        else:
            label = '+hz' if self.direction=='up' else '-hz'
        return name, icon, font, label
    def action(self):
        if self.use.using=='z':
            stacker.stmp.zr(self.step_size*stacker.stmp._step_sizing_translation)
        else:
            stacker.stmp.hzr(self.step_size*stacker.stmp._step_sizing_translation)

class stmp_UpDownUse(BigText):
    def __init__(self, icon_size='big', font_size=30, **kwargs):
        super().__init__(icon_size=icon_size, font_size=font_size, **kwargs)
        self.using = 'z'
        
        self.keys = [
            stmp_UpDown(direction='up', speed='fast', use=self),
            stmp_UpDown(direction='up', speed='normal', use=self),
            stmp_UpDown(direction='down', speed='normal', use=self),
            ]
        
        
    def get_color(self, state=False):
        if self.using=='z':
            return "#7c00ac"
        else:
            return "#a421d5"
    def style(self, state):
        name = "stmp_UpDown"
        icon = "empty{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto/Roboto-Bold.ttf"
        label = '[z]\nhz' if self.using=='z' else 'z\n[hz]'
        return name, icon, font, label
    def action(self):
        if self.using=='z':
            self.using = 'hz'
        else:
            self.using = 'z'
        # Flag all the keys for a refresh
        for key in self.keys:
            key.value += 1
            
stmp_updownuse = stmp_UpDownUse()









class gotoOriginStmp(gotoOrigin):
    
    def __init__(self, mark_name='origin', icon_size='big', font_size=20, **kwargs):
        super().__init__(stage=stacker.stmp, mark_name=mark_name, icon_size=icon_size, font_size=font_size, **kwargs)
    
    def release_action(self):
        if self.held_time>LONG_PRESS:
            stacker.stmp.setOrigin(['x', 'y', 'hz', 'roll', 'pitch', 'yaw', 'z'])
        else:
            stacker.stmp.xvel(1.0)
            stacker.stmp.gotoOrigin()
            


class stmp_pos(BigText):
    def __init__(self, font_size=16, **kwargs):
        super().__init__(font_size=font_size, **kwargs)
        self.value = 0
        self.positions = {'x': -99, 'y': -99, 'z': -99, 'hz': -99, 'roll': -360, 'pitch': -360, 'yaw': -360}
        
    def get_color(self, state=False):
        return "#000000"

    def style(self, state):
        name = "empty"
        icon = "empty{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        #label = "Pressed" if state else "Key {}".format(self.get_key_idx())
        label = "x {x:.3f}\ny {y:.3f}\nz {z:.3f}\nhz {hz:.3f}".format(**self.positions)
        return name, icon, font, label
    
    
    def action(self):
        #stacker.stmp.gotoOrigin()
        pass

    def refresh(self, deck, key, state):
        ret = stacker.stmp.pos__cache()
        if isinstance(ret, dict):
            self.positions = ret
        self.value += 1
        
        return self.value

class stmp_posrot(stmp_pos):
    def style(self, state):
        name = "empty"
        icon = "empty{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        #label = "Pressed" if state else "Key {}".format(self.get_key_idx())
        label = "roll {roll:.2f}\npitch {pitch:.2f}\n(yaw {yaw:.2f})".format(**self.positions)
        return name, icon, font, label    


class stmp_velUp(Key):
    def style(self, state):
        name = "stmp_velUp"
        icon = "arrows/triangle-up{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = '+vel'
        return name, icon, font, label
    def action(self):
        nvel = stacker.stmp.xvel()
        if isinstance(nvel, (int, float)):
            stacker.stmp.xvel(nvel*velocity_step)
            stacker.stmp.zvel(nvel*velocity_step)
class stmp_velDown(Key):
    def style(self, state):
        name = "stmp_velDown"
        icon = "arrows/triangle-down{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        #nvel = stacker.sam.xvel()/velocity_step
        #label = "xvel={:.2f}".format(nvel) if state else "-xvel"
        label = '-vel'
        return name, icon, font, label
    def action(self):
        nvel = stacker.stmp.xvel()
        if isinstance(nvel, (int, float)):
            stacker.stmp.xvel(nvel/velocity_step)
            stacker.stmp.zvel(nvel/velocity_step)

class stmp_vel_ValueRing(sam_vel_ValueRing):
    def action(self):
        nvel = stacker.stmp.xvel(self.vtypical)
        if isinstance(nvel, (int, float)):
            self.value = nvel
    def refresh(self, deck, key, state):
        nvel = stacker.stmp.xvel__cache()
        if isinstance(nvel, (int, float)):
            self.value = nvel
        return self.value

class stmp_SpeedGroup(ToggleGroup):
    def __init__(self, n=6):
        self.n = n
        self.current = 2
        self.buttons = []
        
        self.speed = {
            'vslow': 0.001, # 2.5 micron
            'slow' : 0.002, # 10 microns
            'normal' : 0.05,
            'quick' : 0.2,
            'vquick' : 0.5,
            'fast' : 1,
            'vfast' : 2,
            }
        self.velocity = {
            'vslow': 0.1,
            'slow' : 0.1,
            'normal' : 0.5,
            'quick': 1,# 1 mm/2
            'vquick': 1,# 1 mm/2
            'fast' : 1,
            'vfast' : 1,
            }        
        #self.speed_rot = {
            #'vslow': 0.01, 
            #'slow' : 0.10,
            #'normal' : 0.4,
            #'quick' : 1.0,
            #'vquick' : 1.0,
            #'fast' : 5,
            #'vfast' : 30,
            #}
    
        
    def activate(self, name):
        if name=='slow' or name=='vslow':
            ibutton = 0
        elif name=='normal' or name=='vnormal':
            ibutton = 1
        elif name=='quick' or name=='vquick':
            ibutton = 2
        elif name=='fast' or name=='vfast':
            ibutton = 3
        else:
            print('ERROR: invalid name ({}) to stmp_SpeedGroup.activate'.format(name))
            
        for i, button in enumerate(self.buttons):
            if i==ibutton:
                button.selected = True
            else:
                button.selected = False
                button.very_state = False
            if hasattr(button, 'parent_deck'):
                button.update()
            
        stacker.stmp._step_sizing_translation = self.speed[name]
        #stacker.stmp._step_sizing_rotation = self.speed_rot[name]
        
        # The hexapod shares a common motion system,
        # so we only need to set the velocity once
        stacker.stmp.xvel(self.velocity[name])
        #stacker.stmp.yvel(self.velocity[name])
        #stacker.stmp.hzvel(self.velocity[name])
        #stacker.stmp.rollvel(self.velocity_rot[name])
        #stacker.stmp.pitchvel(self.velocity_rot[name])
        #stacker.stmp.yawvel(self.velocity_rot[name])
        
        stacker.stmp.zvel(self.velocity[name]) # Newport stage

stmp_speed_group = stmp_SpeedGroup()
stmp_speed_group.buttons.append( key_SpeedT(name='slow', parent=stmp_speed_group) )
stmp_speed_group.buttons.append( key_SpeedT(name='normal', parent=stmp_speed_group) )
stmp_speed_group.buttons.append( key_SpeedT(name='quick', parent=stmp_speed_group) )
stmp_speed_group.buttons.append( key_SpeedT(name='fast', parent=stmp_speed_group) )
stmp_speed_group.activate('normal')


class stmp_SpeedGroupRot(stmp_SpeedGroup):
    def __init__(self):
        self.buttons = []
        self.speed_rot = {
            'vslow': 0.01,
            'slow' : 0.1,
            'normal' : 0.5,
            'fast' : 1.0,
            'vfast' : 2.0,
            }     
    def activate(self, name):
        if name=='slow' or name=='vslow':
            ibutton = 0
        elif name=='normal' or name=='vnormal':
            ibutton = 1
        elif name=='fast' or name=='vfast':
            ibutton = 2
        else:
            print('ERROR: invalid name ({}) to stmp_SpeedGroupRot.activate'.format(name))
            
        for i, button in enumerate(self.buttons):
            if i==ibutton:
                button.selected = True
            else:
                button.selected = False
                button.very_state = False
            if hasattr(button, 'parent_deck'):
                button.update()
            
        stacker.stmp._step_sizing_rotation = self.speed_rot[name]


stmp_speed_group_rot = stmp_SpeedGroupRot()
stmp_speed_group_rot.buttons.append( key_SpeedR(name='slow', parent=stmp_speed_group_rot) )
stmp_speed_group_rot.buttons.append( key_SpeedR(name='normal', parent=stmp_speed_group_rot) )
stmp_speed_group_rot.buttons.append( key_SpeedR(name='fast', parent=stmp_speed_group_rot) )
stmp_speed_group_rot.activate('normal')


class stmp_SpeedGroupVel(stmp_SpeedGroup):
    def __init__(self):
        self.buttons = []
        self.velocity = {
            'vslow': 0.0005,
            'slow' : 0.002,
            'normal' : 0.05,
            'quick': 0.1,
            'vquick': 0.5,
            'fast' : 1,
            'vfast' : 20,
            }        

    def activate(self, name):
        if name=='slow' or name=='vslow':
            ibutton = 0
        elif name=='normal' or name=='vnormal':
            ibutton = 1
        elif name=='quick' or name=='vquick':
            ibutton = 2
        elif name=='fast' or name=='vfast':
            ibutton = 3
        else:
            print('ERROR: invalid name ({}) to stmp_SpeedGroupVel.activate'.format(name))
            
        for i, button in enumerate(self.buttons):
            if i==ibutton:
                button.selected = False
            else:
                button.selected = False
                button.very_state = False
            if hasattr(button, 'parent_deck'):
                button.update()
            
        stacker.stmp.xvel(self.velocity[name])
        stacker.stmp.zvel(self.velocity[name]) # Newport stage


class key_SpeedV(key_Speed):
    def get_speeds(self):
        if self.very_state:
            trans = self.parent.velocity['v'+self.name]
        else:
            trans = self.parent.velocity[self.name]
        return trans
    def get_speed_text(self):
        trans = self.get_speeds()
        if trans<0.1:
            label_text = "vel = \n{}µm/s".format(trans*1000)
        else:
            label_text = "vel = \n{}mm/s".format(trans)
        return label_text


stmp_speed_group_vel = stmp_SpeedGroupVel()
stmp_speed_group_vel.buttons.append( key_SpeedV(name='slow', parent=stmp_speed_group_vel) )
stmp_speed_group_vel.buttons.append( key_SpeedV(name='normal', parent=stmp_speed_group_vel) )
stmp_speed_group_vel.buttons.append( key_SpeedV(name='quick', parent=stmp_speed_group_vel) )
stmp_speed_group_vel.buttons.append( key_SpeedV(name='fast', parent=stmp_speed_group_vel) )


class stmp_HoldRelease(Key):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state_holding = False
    
    def style(self, state):
        name = "stmp_HoldRelease"
        if self.state_holding:
            icon = "arrows/chevron-circle-up-purple{}.png".format("-Pressed" if state else "-Released")
            label = "release"
        else:
            icon = "arrows/chevron-circle-down-purple{}.png".format("-Pressed" if state else "-Released")
            label = "hold"
        font = "Roboto-Regular.ttf"
        
        return name, icon, font, label
    def action(self):
        if self.state_holding:
            stacker.stmp.release()
            self.state_holding = False
        else:
            stacker.stmp.hold()
            self.state_holding = True





# Key maps
########################################
# Assign Key() objects to the various buttons on the StreamDeck

#  0  1  2  3  4
#  5  6  7  8  9
# 10 11 12 13 14

key_map_stacker_sam = {
    0 : SamMenu(menu_name='Velocity'),
    5 : SamMenuCam(menu_name='Camera'),
    10 : sam_HoldRelease(),

    # Speed control
    1 : sam_speed_group.buttons[2],
    6 : sam_speed_group.buttons[1],
    11 : sam_speed_group.buttons[0],
    
    # Motion arrows
    7 : sam_Left(),
    9 : sam_Right(),
    3 : sam_Up(),
    13 : sam_Down(),
    2 : sam_CCW(),
    4 : sam_CW(),

    # Other motion
    #8: sam_phi_OriRing() ,
    #8 : sam_pos() ,
    8 : gotoOriginSam(),
    12 : gotoMark(stage=stacker.sam, mark_name='A'),
    14 : gotoMark(stage=stacker.sam, mark_name='B'),
    }

key_map_sam_menu = {
    0 : SwapToSamMain(),
    5 : Clock(),
    10 : Timer(),
    #2 : sam_xvelUp(),
    #7 : sam_vel_ValueRing('x', vmin=0, vmax=4, vtypical=1),
    #12 : sam_xvelDown(),
    3 : sam_xyvelUp(),
    8 : sam_vel_ValueRing('x', vmin=0, vmax=4, vtypical=1),
    13 : sam_xyvelDown(),
    4 : sam_phivelUp(),
    9 : sam_vel_ValueRing('phi', vmin=0, vmax=10, vtypical=5),
    14 : sam_phivelDown(),
    
    }


key_map_stacker_cam = {
    0 : SwapToSamMain(),
    8 : cam_pos(),
    
    #1: followMarkCam(mark_name='stamp'),
    6: gotoMark(stage=stacker.cam, mark_name='sample'),
    11: gotoMark(stage=stacker.cam, mark_name='sub'),
    
    2 : cam_UpDown(direction='up', speed='fast'),
    3 : cam_UpDown(direction='up', speed='normal'),
    4 : cam_UpDown(direction='up', speed='slow'),
    12 : cam_UpDown(direction='down', speed='fast'),
    13 : cam_UpDown(direction='down', speed='normal'),
    14 : cam_UpDown(direction='down', speed='slow'),
    
    }


#  0  1  2  3  4  5  6  7
#  8  9 10 11 12 13 14 15
# 16 17 18 19 20 21 22 23
# 24 25 26 27 28 29 30 31

# SP layout 2021-08-04
key_map_stacker_stmp = {
    
    
    2 : stmp_updownuse.keys[0],
    10 : stmp_updownuse.keys[1],
    26 : stmp_updownuse.keys[2],
    18 : stmp_updownuse,
    
    6: stmp_HoldRelease(),
    # Marks
    15 : gotoMark(stage=stacker.stmp, mark_name='A'),
    23 : gotoMark(stage=stacker.stmp, mark_name='B'),
    31 : gotoMark(stage=stacker.stmp, mark_name='C'),
    
    5 : stmp_velUp(),
    4 : stmp_vel_ValueRing('hex', vmin=0, vmax=5, vtypical=0.5),
    3 : stmp_velDown(),
    
    # Speed control: velocity
    0 : stmp_speed_group_vel.buttons[3],
    8 : stmp_speed_group_vel.buttons[2],
    16 : stmp_speed_group_vel.buttons[1],
    24 : stmp_speed_group_vel.buttons[0],
    # Speed control: steps
    1 : stmp_speed_group.buttons[3],
    9 : stmp_speed_group.buttons[2],
    17 : stmp_speed_group.buttons[1],
    25 : stmp_speed_group.buttons[0],
    # Speed control: rot steps
    14 : stmp_speed_group_rot.buttons[2],
    22 : stmp_speed_group_rot.buttons[1],
    30 : stmp_speed_group_rot.buttons[0],
    
    # Motion arrows
    20 : stmp_transrotuse,
    12 : stmp_transrotuse.keys[2],
    19 : stmp_transrotuse.keys[0],
    21 : stmp_transrotuse.keys[1],
    28 : stmp_transrotuse.keys[3],
    
    # Rotation
    #5 : stmp_PitchPos(),
    #7 : stmp_PitchNeg(),
    #15 : stmp_RollPos(),
    #31 : stmp_RollNeg(),
    
    # Other
    7 : gotoOrigin(stage=stacker.stmp),
    }    

if False:
    # KY layout 2021-08-03
    key_map_stacker_stmp = {
        #16 : Clock() ,
        #24 : Timer() ,
        
        1: stmp_HoldRelease(),
        
        0 : stmp_updownuse.keys[0],
        8 : stmp_updownuse.keys[1],
        16 : stmp_updownuse,
        24 : stmp_updownuse.keys[2],
        
        
        # Marks
        10 : gotoMark(stage=stacker.stmp, mark_name='A'),
        18 : gotoMark(stage=stacker.stmp, mark_name='B'),
        26 : gotoMark(stage=stacker.stmp, mark_name='C'),
        
        11 : stmp_velUp(),
        19 : stmp_vel_ValueRing('hex', vmin=0, vmax=5, vtypical=0.5),
        27 : stmp_velDown(),
        
        # Speed control
        4 : stmp_speed_group.buttons[3],
        12 : stmp_speed_group.buttons[2],
        20 : stmp_speed_group.buttons[1],
        28 : stmp_speed_group.buttons[0],
        
        # Motion arrows
        14 : stmp_Up(),
        21 : stmp_Left(),
        23 : stmp_Right(),
        30 : stmp_Down(),
        
        # Rotation
        5 : stmp_PitchPos(),
        7 : stmp_PitchNeg(),
        15 : stmp_RollPos(),
        31 : stmp_RollNeg(),
        
        # Other
        22 : gotoOriginStmp(''),
        #22 : stmp_pos(),
        #29 : stmp_posrot(),
        
        }
