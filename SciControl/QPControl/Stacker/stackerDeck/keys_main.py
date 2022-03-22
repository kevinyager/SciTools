#!/usr/bin/env python3


from prototypes import *
import subprocess



# Key definitions
########################################
# To determine a keystroke name:
#  xev -event keyboard
# Some nice arrow icons:
#  http://icons.deanishe.net/preview/fontawesome

        
class DUp(Key):
    def style(self, state):
        name = "DUp"
        icon = "arrows/up{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "" if state else "Up"
        return name, icon, font, label
    def action(self):
        os.system('xdotool key "Super_L+Up"')

class DDown(Key):
    def style(self, state):
        name = "DDown"
        icon = "arrows/down{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "" if state else "Down"
        return name, icon, font, label
    def action(self):
        os.system('xdotool key "Super_L+Down"')

class DLeft(Key):
    def style(self, state):
        name = "DLeft"
        icon = "arrows/left{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "" if state else "Left"
        return name, icon, font, label
    def action(self):
        os.system('xdotool key "Super_L+Left"')

class DRight(Key):
    def style(self, state):
        name = "DRight"
        icon = "arrows/right{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "" if state else "Right"
        return name, icon, font, label
    def action(self):
        os.system('xdotool key "Super_L+Right"')

class DMain(Key):
    def style(self, state):
        name = "DMain"
        icon = "circle{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "Main"
        return name, icon, font, label
    def action(self):
        os.system('xdotool key "Ctrl+F2"')

class DA1(BigText):
    def style(self, state):
        name = "DA1"
        icon = "circle{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "A1"
        return name, icon, font, label
    def get_color(self, state=False):
        return "#000088"
    def action(self):
        os.system('xdotool key "Ctrl+F1"')

class DD1(BigText):
    def style(self, state):
        name = "DD1"
        icon = "circle{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "D1"
        return name, icon, font, label
    def get_color(self, state=False):
        return "#000088"
    def action(self):
        os.system('xdotool key "Ctrl+F4"')

class DA4(BigText):
    def style(self, state):
        name = "DA4"
        icon = "circle{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "A4"
        return name, icon, font, label
    def get_color(self, state=False):
        return "#000088"
    def action(self):
        os.system('xdotool key "Ctrl+F5"')

class DD4(BigText):
    def style(self, state):
        name = "DD4"
        icon = "circle{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "D4"
        return name, icon, font, label
    def get_color(self, state=False):
        return "#000088"
    def action(self):
        os.system('xdotool key "Ctrl+F6"')
        
class Refresh(Key): # F5
    def style(self, state):
        name = "Refresh"
        icon = "refresh{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "Refreshing" if state else "Refresh"
        return name, icon, font, label
    def action(self):
        window_name = subprocess.check_output('xdotool getwindowfocus getwindowname', shell=True).decode('utf-8')
        if 'Inkscape' in window_name:
            os.system('xdotool keydown alt key f; sleep 0.01; xdotool keyup alt')
            time.sleep(0.01)
            os.system('xdotool key v')
        else:
            os.system('xdotool key "F5"')

class MaximizeVertical(Key):
    def style(self, state):
        name = "MaximizeVertical"
        icon = "arrows/double_v{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "Maximize"
        return name, icon, font, label
    def action(self):
        os.system('wmctrl -r :ACTIVE: -b toggle,maximized_vert')


class Close(Key):
    def style(self, state):
        name = "Close"
        icon = "exit{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "Closing" if state else "Close"        
        return name, icon, font, label
    def action(self):
        os.system('xdotool key "Alt+F4"')



class Clock(Key):
    
    def render_key_image(self, deck, icon_filename, font_filename, label_text, date=True, seconds=False, state=False):
        # Create new key image of the correct dimensions, black background
        image = PILHelper.create_image(deck)
        draw = ImageDraw.Draw(image)

        # Add image overlay, rescaling the image asset if it is too large to fit
        # the requested dimensions via a high quality Lanczos scaling algorithm
        icon = Image.open(icon_filename).convert("RGBA")
        icon.thumbnail((image.width, image.height - 20), Image.LANCZOS)
        icon_pos = ((image.width - icon.width) // 2, 0)
        image.paste(icon, icon_pos, icon)

        # Load a custom TrueType font and use it to overlay the key index, draw key
        # label onto the image
        font = ImageFont.truetype(font_filename, 20)
        label_w, label_h = draw.textsize(label_text, font=font)
        label_pos = ((image.width - label_w) // 2, (image.height - label_h) // 2 + 6)
        draw.text(label_pos, text=label_text, font=font, fill="white")
        
        if date: 
            label_extra = time.strftime("%Y-%m-%d")
            font = ImageFont.truetype(font_filename, 10)
            label_w, label_h = draw.textsize(label_extra, font=font)
            label_pos = ((image.width - label_w) // 2, 12)
            draw.text(label_pos, text=label_extra, font=font, fill="white")
        
        if seconds:
            #label_extra = time.strftime(r'%S')
            label_extra = datetime.datetime.now().strftime("%S.%f")[:-3]
            font = ImageFont.truetype(font_filename, 10)
            label_w, label_h = draw.textsize(label_extra, font=font)
            label_pos = ((image.width - label_w) // 2, image.height - 20)
            draw.text(label_pos, text=label_extra, font=font, fill="white")

        return PILHelper.to_native_format(deck, image)
    
    
    def style(self, state):
        name = "Clock"
        icon = "empty{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        #label = "{}".format(time.strftime("%Y-%m-%d\n%H:%M:%S"))
        label = time.strftime("%H:%M")
        return name, icon, font, label
    
    def action(self):
        time_txt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        os.system('xdotool type "{}"'.format(time_txt))
    
    def refresh(self, deck, key, state):
        self.update_key_image(deck, key, state)
        return None
    

class Timer(Key):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.running = False
        self.total_time = 0
        self.start_time = 0
        
    def time_split(self, t):
        days = t // (24 * 3600)
        t = t % (24 * 3600)
        hours = t // 3600
        t %= 3600
        minutes = t // 60
        t %= 60
        seconds = t
        
        return int(days), int(hours), int(minutes), seconds
    
    def style(self, state):
        name = "Timer"
        icon = "empty{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "Timer"
        return name, icon, font, label

    def render_key_image(self, deck, icon_filename, font_filename, label_text, state=False):
        # Create new key image of the correct dimensions, black background
        image = PILHelper.create_image(deck)
        draw = ImageDraw.Draw(image)

        # Add image overlay, rescaling the image asset if it is too large to fit
        # the requested dimensions via a high quality Lanczos scaling algorithm
        icon = Image.open(icon_filename).convert("RGBA")
        icon.thumbnail((image.width, image.height - 20), Image.LANCZOS)
        icon_pos = ((image.width - icon.width) // 2, 0)
        image.paste(icon, icon_pos, icon)

        # Load a custom TrueType font and use it to overlay the key index, draw key
        # label onto the image
        font = ImageFont.truetype(font_filename, 14)
        label_w, label_h = draw.textsize(label_text, font=font)
        label_pos = ((image.width - label_w) // 2, image.height - 20)
        draw.text(label_pos, text=label_text, font=font, fill="white")


        display_time = self.get_time()
        days, hours, minutes, seconds = self.time_split(display_time)
            

        # Hours
        if days>0:
            label_extra = "{:d}d {:d}h".format(days, hours)
        else:
            label_extra = "{:d}h".format(hours)
        font = ImageFont.truetype(font_filename, 14)
        label_w, label_h = draw.textsize(label_text, font=font)
        label_pos = ((image.width - label_w) // 2, (image.height - label_h) // 2 - 19 )
        draw.text(label_pos, text=label_extra, font=font, fill="white")
            
        # Minutes
        label_extra = "{:d}m".format(minutes)
        font = ImageFont.truetype(font_filename, 14)
        label_w, label_h = draw.textsize(label_text, font=font)
        label_pos = ((image.width - label_w) // 2, (image.height - label_h) // 2 - 6 )
        draw.text(label_pos, text=label_extra, font=font, fill="white")
        
        # Seconds
        label_extra = "{:.2f}s".format(seconds)
        font = ImageFont.truetype(font_filename, 14)
        label_w, label_h = draw.textsize(label_text, font=font)
        label_pos = ((image.width - label_w) // 2, (image.height - label_h) // 2 + 7)
        draw.text(label_pos, text=label_extra, font=font, fill="white")
        
        return PILHelper.to_native_format(deck, image)
    
    def get_time(self):
        if self.running:
            display_time = time.time()-self.start_time
        else:
            display_time = self.total_time
        return display_time
    
    def action(self):
        if self.running:
            self.running = False
            self.total_time = time.time() - self.start_time
        else:
            self.running = True
            self.start_time = time.time()

    def refresh(self, deck, key, state):
        self.update_key_image(deck, key, state)
        return None 


class HoldTimer(Timer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def style(self, state):
        name = "HoldTimer"
        icon = "empty{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "Hold"
        return name, icon, font, label

    def get_time(self):
        return self.held_time

    def action(self):
        pass
        

# Menus
########################################
class Menu(Key):
    def style(self, state):
        name = "Menu"
        icon = "grid{}.png".format("-Pressed" if state else "-Released")
        #<div>Icons made by <a href="https://www.flaticon.com/authors/elegant-themes" title="Elegant Themes">Elegant Themes</a> from <a href="https://www.flaticon.com/" 			    title="Flaticon">www.flaticon.com</a> is licensed by <a href="http://creativecommons.org/licenses/by/3.0/" 			    title="Creative Commons BY 3.0" target="_blank">CC 3.0 BY</a></div>
        font = "Roboto-Regular.ttf"
        label = "Menu" if state else "Menu"
        return name, icon, font, label
    def action(self):
        swap_key_map(self.parent_deck, key_map_menu)

class SwapToMain(Key):
    def style(self, state):
        name = "Back"
        icon = "undo{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "Back"
        return name, icon, font, label
    def action(self):
        swap_key_map(self.parent_deck, key_map_desktop)


class Testing(Key):
    def style(self, state):
        name = "Testing"
        icon = "circle{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "Pressed" if state else "Testing"
        print(self.get_key_idx())
        return name, icon, font, label
    def action(self):
        swap_key_map(self.parent_deck, key_map_application)
        
        
# Key maps
########################################
# Assign Key() objects to the various buttons on the StreamDeck

#  0  1  2  3  4
#  5  6  7  8  9
# 10 11 12 13 14

key_map_desktop = {
    0 : DA1() ,
    2 : DD1() ,
    10 : DA4() ,
    12 : DD4() ,
    1 : DUp() ,
    11 : DDown() ,
    5 : DLeft() ,
    7 : DRight() ,
    6 : DMain() ,
    3 : Clock() ,
    13 : Timer() ,
    9 : Refresh() ,
    4 : MaximizeVertical() ,
    14 : Close() ,
    8 : Menu() ,
    }

key_map_application = {
    0 : DUp() ,
    }


key_map_menu = {
    0 : SwapToMain() ,
    4 : Clock() ,
    9 : Timer() ,
    }

key_map_empty = {
    0 : Clock() ,
    }
