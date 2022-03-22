#!/usr/bin/env python3


# This code requires the following library to be installed:
# https://github.com/abcminiuser/python-elgato-streamdeck
#         Python Stream Deck Library
#      Released under the MIT license
#
#   dean [at] fourwalledcubicle [dot] com
#         www.fourwalledcubicle.com
#
# With license:
#Permission to use, copy, modify, and distribute this software
#and its documentation for any purpose is hereby granted without
#fee, provided that the above copyright notice appear in all
#copies and that both that the copyright notice and this
#permission notice and warranty disclaimer appear in supporting
#documentation, and that the name of the author not be used in
#advertising or publicity pertaining to distribution of the
#software without specific, written prior permission.

#The author disclaims all warranties with regard to this
#software, including all implied warranties of merchantability
#and fitness.  In no event shall the author be liable for any
#special, indirect or consequential damages or any damages
#whatsoever resulting from loss of use, data or profits, whether
#in an action of contract, negligence or other tortious action,
#arising out of or in connection with the use or performance of
#this software.




import os
from PIL import Image, ImageDraw, ImageFont


# Test: Use local copy of code (installed of "pip3 install streamdeck" version)
#import sys
#code_PATH='/home/yager/doit/install_history/ElgatoStreamDeck/python-elgato-streamdeck-master/src/'
#code_PATH in sys.path or sys.path.append(code_PATH)

from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper

#import threading

#import keyboard
import subprocess
import time, datetime
import numpy as np

# Key
########################################
# This base class defines the style and action for a particular button
class Key():
    
    def __init__(self, icon_size='small', font_size=14, **kwargs):
        
        self.icon_size = icon_size
        self.font_size = font_size
        
        # When a key is pressed, we keep track of how long it was held down
        self.held = False
        self.held_start = 0
        self.held_time = 0
        
    def get_key_idx(self):
        
        for key_idx, key in self.parent_deck.key_map.items():
            if key==self:
                return key_idx
            
        return None
        
    
    def action(self):
        pass

    def release_action(self):
        pass
    
    def refresh(self, deck, key, state):
        return None


    # Generates a custom tile with run-time generated text and custom image via the
    # PIL module.
    def render_key_image(self, deck, icon_filename, font_filename, label_text, state=False):
        # Create new key image of the correct dimensions, black background
        image = PILHelper.create_image(deck)
        draw = ImageDraw.Draw(image)

        # Add image overlay, rescaling the image asset if it is too large to fit
        # the requested dimensions via a high quality Lanczos scaling algorithm
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
        label_pos = ((image.width - label_w) // 2, image.height - 20)
        draw.text(label_pos, text=label_text, font=font, fill="white")

        return PILHelper.to_native_format(deck, image)


    # Returns styling information for a key based on its position and state.
    def get_key_style(self, deck, key, state):
        # state = True # means button is pressed
        
        name, icon, font, label = self.style(state)

        return {
            "name": name,
            "icon": os.path.join(os.path.dirname(__file__), "Assets", icon),
            "font": os.path.join(os.path.dirname(__file__), "Assets", font),
            "label": label
        }

    # Creates a new key image based on the key index, style and current key state
    # and updates the image on the StreamDeck.
    def update_key_image(self, deck, key, state):
        # Determine what icon and label to use on the generated key
        key_style = self.get_key_style(deck, key, state)

        # Generate the custom key with the requested image and label
        image = self.render_key_image(deck, key_style["icon"], key_style["font"], key_style["label"], state=state)

        # Update requested key with the generated image
        deck.set_key_image(key, image)


    # Force an update of the key (useful for activating in contexts
    # where we don't have a pointer to the deck)
    def update(self, state=False):
        deck = self.parent_deck
        key = self.get_key_idx()
        self.update_key_image(deck, key, state)
        


            


# Key prototypes
########################################
class Empty(Key):
    def style(self, state):
        name = "empty"
        icon = "empty{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        #label = "Pressed" if state else "Key {}".format(self.get_key_idx())
        label = "Key {}".format(self.get_key_idx()) if state else ""
        return name, icon, font, label
    

class BigText(Key):
    
    def __init__(self, icon_size='big', font_size=20, **kwargs):
        super().__init__(icon_size=icon_size, font_size=font_size, **kwargs)
        self.state = False
    
    def get_color(self, state=False):
        #if self.state:
        if state:
            return "#00FF00"
        else:
            return "#FF0000"
    
    def style(self, state):
        name = "empty"
        icon = "empty{}.png".format("-Pressed" if state else "-Released")
        font = "Roboto-Regular.ttf"
        label = "Pressed" if state else "Key"
        return name, icon, font, label
    
    def render_key_image(self, deck, icon_filename, font_filename, label_text, show_icon=False, state=False):
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
        label_pos = ( (image.width - label_w) // 2, (image.height - label_h) //2 )
        draw.text(label_pos, text=label_text, font=font, fill="white", align="center")

        return PILHelper.to_native_format(deck, image)
    

class ValueRing(Key):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.value = 0
        self.gap_for_label = 40 # degrees
    
    def get_color(self, vmin=None, vmax=None, state=False):
        value = self.get_value(vmin=vmin, vmax=vmax)
        r = int( 255 - 255*value )
        g = int( 0 )
        b = int( 255*value )
        
        return "rgb({:d},{:d},{:d})".format(r,g,b)

    def get_value(self, vmin=None, vmax=None):
        if vmin==None:
            vmin = 0
        if vmax==None:
            vmax = 1
            
        return np.clip((self.value-vmin)/(vmax-vmin), vmin, vmax)

    def render_key_image(self, deck, icon_filename, font_filename, label_text, state=False):
        # Create new key image of the correct dimensions, black background
        image = PILHelper.create_image(deck)
        draw = ImageDraw.Draw(image)
        
        fill = self.get_color(state=state)
        
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

        label_extra = "{:.0f}".format(self.value)
        font = ImageFont.truetype(font_filename, 20)
        label_w, label_h = draw.textsize(label_extra, font=font)
        label_pos = ( (image.width - label_w) // 2, (image.height - label_h) // 2 )
        draw.text(label_pos, text=label_extra, font=font, fill="white")


        font = ImageFont.truetype(font_filename, 14)
        label_w, label_h = draw.textsize(label_text, font=font)
        label_pos = ((image.width - label_w) // 2, image.height - 20)
        draw.text(label_pos, text=label_text, font=font, fill="white")
        
        return PILHelper.to_native_format(deck, image)

    def refresh(self, deck, key, state):
        #self.value = ...
        return self.value





# State managers
########################################
# Simple functions that control the behavior of the deck

# Prints key state change information, updates rhe key image and performs any
# associated actions when a key is pressed.
def key_change_callback(deck, key, state, verbosity=3):
    if verbosity>=3:
        print("      Deck {} Key {} = {}".format(deck.id(), key, 'Pressed' if state else 'Released'), flush=True)
    
    try:
        key_object = deck.key_map[key]
        
        # Update the key image based on the new key state
        key_object.update_key_image(deck, key, state)

        # Check if the key is changing to the pressed state
        if state:
            # Key was just pressed
            key_object.held = True
            key_object.held_start = time.time()
            
            
            #key_style = key_object.get_key_style(deck, key, state)
            key_object.action()
            
            global last_press
            last_press = time.time()
            
        else:
            # Key was just released
            key_object.held = False
            key_object.held_time = time.time()-key_object.held_start
            
            key_object.release_action()
            
        
    except KeyError:
        if verbosity>=1:
            print("    No key defined for button {} on deck {}".format(key, deck.id()))
        

def swap_key_map(deck, key_map, insert_empties=True):
    
    deck._lock = True
    
    deck.key_map = key_map

    # Set initial key images
    for key in range(deck.key_count()):
        try:
            key_object = deck.key_map[key]
            key_object.parent_deck = deck
            key_object.update_key_image(deck, key, False)
        except KeyError:
            #print("    No key defined for button {} on deck {}".format(key, deck.id()))
            if insert_empties:
                key_object = Empty()
                deck.key_map[key] = key_object
                
                key_object.parent_deck = deck
                key_object.update_key_image(deck, key, False)
                
    deck._lock = False
                
                



# Deck running
########################################

class Monitor():
    
    def __init__(self, key_maps=None, names={}):
        self.key_maps = key_maps
        self.last_press = time.time()
        self.last_change = time.time()
        self.last_window_name = ""
        
        # A list of the triggers for changing the keymap. This is typically the
        # window name, so that the keymap updates to match the new application.
        self.names = names


    def loop(self, streamdecks, loop_time_min=0.1, loop_time_max=5.0, monitor_window=False, window_idx=0, verbosity=3):

        # Initialize monitoring values
        for index, deck in enumerate(streamdecks):
            deck.last_states = {}
            for key_idx, key_object in deck.key_map.items():
                val = key_object.refresh(deck, key_idx, False)
                key_object.update_key_image(deck, key_idx, False)
                deck.last_states[key_idx] = val

        
        while True:

            # Check for changes
            for index, deck in enumerate(streamdecks):
                if not deck._lock:
                    for key_idx, key_object in deck.key_map.items():
                        val = key_object.refresh(deck, key_idx, False)
                        if val!=deck.last_states[key_idx]:
                            key_object.update_key_image(deck, key_idx, False)
                            deck.last_states[key_idx] = val # Update the tracked value
                            self.last_change = time.time() # Reset the clock
                            
                            if verbosity>=5:
                                name, icon, font, label = key_object.style(False)
                                print("    Value change: key {} ({}) is now: {}".format(key_idx, name, key_object.value))
            
            if monitor_window:
                #original_window_id = int(subprocess.check_output('xdotool getwindowfocus', shell=True))
                try:
                    window_name = subprocess.check_output('xdotool getwindowfocus getwindowname', shell=True)
                    window_name = window_name.decode('utf-8').strip()
                    
                    if window_name!=self.last_window_name:
                        self.last_window_name = window_name
                        self.last_change = time.time() # Reset the clock
                        if verbosity>=4:
                            time_txt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                            print("    {} Window: {}".format(time_txt, window_name))
                            
                        self.change_keymap(streamdecks[window_idx], window_name)
                            
                except Exception as e:
                    # xdotool may give an error (if there is no active window)
                    # in which case, we can just skip this entirely
                    if verbosity>=4:
                        time_txt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                        print("    {} No window".format(time_txt))

                    
                

            time_since_last_change = min( time.time() - self.last_change , time.time() - self.last_press )

            if time_since_last_change<60:
                sleep_time = loop_time_min
            elif time_since_last_change>600:
                sleep_time = loop_time_max
            else:
                amt = (time_since_last_change-60)/(600-60)
                sleep_time = (loop_time_max-loop_time_min)*amt + (loop_time_min)*(1-amt)

            if verbosity>=5:
                print("Loop: {:.1f} s since last change; {:.1f} s since last press. Waiting {:.1f} s...".format(time.time()-self.last_change, time.time()-self.last_press, sleep_time))
            time.sleep(sleep_time)




    def monitor(self, reverse=False, monitor_window=False, window_idx=0, verbosity=3):
        streamdecks = DeviceManager().enumerate()
        
        if verbosity>=1:
            print("Found {} Stream Deck(s).\n".format(len(streamdecks)))

        for index, deck in enumerate(streamdecks):
            if verbosity>=1:
                print("Activating deck {} (id = {})".format(index, deck.id()))
            deck.open()
            deck.reset()

            # Set initial screen brightness to 30%
            deck.set_brightness(40)

            if index<len(self.key_maps):
                if reverse:
                    swap_key_map(deck, self.key_maps[len(self.key_maps)-index-1])
                else:
                    swap_key_map(deck, self.key_maps[index])

            # Register callback function for when a key state changes
            deck.set_key_callback(key_change_callback)


            #if index==len(streamdecks)-1:
                # Wait for user to kill the session
                #input("Press Enter to quit...")

                # Wait until all application threads have terminated (for this example,
                # this is when all deck handles are closed)
                #for t in threading.enumerate():
                    #if t is threading.currentThread():
                        #continue
                    #if t.is_alive():
                        #t.join()

        # Monitor loop
        try:
            self.loop(streamdecks, monitor_window=monitor_window, window_idx=window_idx, verbosity=verbosity)
                
        except KeyboardInterrupt:
            pass
        


        # Close everything
        for index, deck in enumerate(streamdecks):
            if verbosity>=1:
                print("Closing deck {} (id = {})".format(index, deck.id()))
            # Reset deck, clearing all button images
            deck.reset()
            # Close deck handle, terminating internal worker threads
            deck.close()


    def change_keymap(self, deck, new_name, verbosity=3):
        
        if verbosity>=5:
            print("        change_keymap: {}".format(new_name))
        for name, key_map in self.names.items():
            if verbosity>=6:
                print("          change_keymap: checking {}".format(name))
            if name in new_name:
                if verbosity>=4:
                    print("          change_keymap: switching to map for {}".format(name))
                swap_key_map(deck, key_map)
                return
            

#monitor = Monitor()



