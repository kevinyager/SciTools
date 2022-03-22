#!/usr/bin/python3
# -*- coding: utf-8 -*-
#import os

print( "Content-type: text/html;charset=UTF-8\r\n\r\n")

import sys
#Code_PATH='D:/QPress/Stacker/control_software/19-Stacker/stacker'
#Code_PATH='/home/yager/Desktop/Stacker/stacker/'
Code_PATH='../stacker/'
Code_PATH in sys.path or sys.path.append(Code_PATH)

from Stacker import *


AUTH='Cah2zawipu3Gohw2eFo1aec4ohPhah8u' # Authentication token
stacker = Stacker(name='stackerHTTP', mode='client', authentication_token=AUTH, common=None, verbosity=0)
stacker.client_connect_to_server()
pos = stacker.pos()
#print(pos)
stacker.close()

now = time.time()


def get_color_danger_red(value, vmin=0, vmax=1, danger=0.1, saturation=0.55):
    '''Colors go from white to faint red.'''
    r, g, b = 1, 1, 1
    span = vmax-vmin
    extent = np.clip((value-vmin)/span, 0, 1)
    if extent>(1-danger):
        extent = (extent-(1-danger))/danger
        g = 1 - extent*saturation
        b = 1 - extent*saturation
    elif extent<danger:
        extent = extent/danger
        g = 1 - (1-extent)*saturation
        b = 1 - (1-extent)*saturation
        
    return r, g, b

def get_color_bpr(value, vmin=0, vmax=1, danger=0.1, saturation=0.55, ):
    '''Colors go from white to blue to purple to red.'''
    span = vmax-vmin

    extent = np.clip((value-vmin)/span, 0, 1)
    if extent<danger:
        extent /= danger
        r = 1-extent*saturation
        g = 1-extent*saturation
        b = 1
    else:
        extent = (extent-danger)/(1-danger)
        r = extent*saturation + (1-saturation)
        b = 1-extent*saturation
        g = 1-saturation

    #s = 'v={:.3f}/{:.3f} r{:.2f}g{:.2f}b{:.2f}'.format(value, vmax, r, g, b)
    return r, g, b

def rgb_to_html(r, g, b, max=255):
    return '#{:02X}{:02X}{:02X}'.format(int(r*max), int(g*max), int(b*max))
    

def get_td_pos(value, vmax=1, danger=0.1, vmin=0, age=None, age_time=5, extra=""):
    r, g, b = get_color_danger_red(value, vmin=vmin, vmax=vmax, danger=danger)
    if age is not None and age<age_time:
        blend = age/age_time
        rt, gt, bt = 0, 1, 0
        r, g, b = r*blend+rt*(1-blend), g*blend+gt*(1-blend), b*blend+bt*(1-blend)
    c = rgb_to_html(r, g, b)
    s = f'<td align="right" bgcolor="{c}" {extra}>{value:.3f}</td>'
    return s

def get_td_vel(value, vmax=1, vmin=0):
    r, g, b = get_color_bpr(value, vmin=vmin, vmax=vmax)
    c = rgb_to_html(r, g, b)
    s = f'<td align="right" bgcolor="{c}">{value:.3f}</td>'
    return s
    

# Debug
#for v in np.linspace(0, 10, num=50):
    #c, s = get_color_bpr(v, vmax=10, retvals=True)
    #print('<div style="background-color:{};">{} {}</div>'.format(c, s, c))
    #c = get_color_danger_red(v, vmin=0, vmax=10)
    #print('<div style="background-color:{};">{}</div>'.format(c, c))


#
print('<table style=->')

# table header
print('<tr class="border_bottom"><td></td><td></td><td align="center">pos/mm</td><td>&nbsp;&nbsp;</td><td align="center">vel</td><td>&nbsp;&nbsp;</td><td></td><td>pos/&deg;</td></tr>')

# For debugging:
#print('<tr><td>stage</td><td>axis</td><td align="center">pos/mm</td><td>&nbsp;-&nbsp;</td><td align="center">vel</td><td>&nbsp;-&nbsp;</td><td>axis</td><td>pos/°</td></tr>')


# Camera
age = now - pos['cam']['z__timestamp']
print('<tr class="border_top"><td style="font-weight: bold;">cam.</td><td>z</td>{}<td></td>{}<td></td><td></td><td></td></tr>'.format(
    get_td_pos(pos['cam']['z'], vmin=-12, vmax=-2, age=age),
    get_td_vel(pos['cam']['zvel'], vmax=10)
    ))


# Stamp
trans_limit, rot_limit = 10, 8
age_x = now - pos['stmp']['x__timestamp']
age_roll = now - pos['stmp']['roll__timestamp']
print('<tr class="border_top"><td style="font-weight: bold;">stmp.</td><td>x</td>{}<td></td>{}<td></td><td>roll</td>{}</tr>'.format(
    get_td_pos(pos['stmp']['x'], vmin=-trans_limit, vmax=+trans_limit, age=age_x), 
    get_td_vel(pos['stmp']['xvel'], vmax=5),
    get_td_pos(pos['stmp']['roll'], vmin=-rot_limit, vmax=+rot_limit, age=age_roll), 
    ))

age_y = now - pos['stmp']['y__timestamp']
age_pitch = now - pos['stmp']['pitch__timestamp']
print('<tr><td></td><td>y</td>{}<td></td><td align="right"></td><td></td><td>pitch</td>{}</tr>'.format(
    get_td_pos(pos['stmp']['y'], vmin=-trans_limit, vmax=+trans_limit, age=age_y), 
    get_td_pos(pos['stmp']['pitch'], vmin=-rot_limit, vmax=+rot_limit, age=age_pitch)
    ))

age_hz = now - pos['stmp']['hz__timestamp']
age_yaw = now - pos['stmp']['yaw__timestamp']
print('<tr><td></td><td>hz</td>{}<td></td><td align="right"></td><td></td><td style="color: #CCCCCC;">yaw</td>{}</tr>'.format(
    get_td_pos(pos['stmp']['hz'], vmin=-trans_limit, vmax=+trans_limit, age=age_hz),
    get_td_pos(pos['stmp']['yaw'], vmin=-rot_limit, vmax=+rot_limit, age=age_yaw, extra='style="color: #CCCCCC;"')
    ))

age = now - pos['stmp']['z__timestamp']
print('<tr><td></td><td>z</td>{}<td></td><td align="right"></td><td></td><td></td><td></td></tr>'.format(
    get_td_pos(pos['stmp']['z'], vmin=-10, vmax=10, age=age)
    ))

# Sample
for axis in ['x', 'y']:
    age = now - pos['sam'][axis+'__timestamp']
    first = '<tr class="border_top"><td style="font-weight: bold;">sam.</td>' if axis=='x' else '<tr><td></td>'
    print('{}<td>{}</td>{}<td></td>{}<td></td><td></td><td></td></tr>'.format(
        first,
        axis,
        get_td_pos(pos['sam'][axis], vmin=-25, vmax=+25, age=age),
        get_td_vel(pos['sam'][f'{axis}vel'], vmax=4)
        ))

age = now - pos['sam']['phi__timestamp']
print('<tr><td></td><td></td><td align="right"></td><td></td>{}<td></td><td>phi</td>{}</tr>'.format(
    get_td_vel(pos['sam']['phivel'], vmax=10),
    get_td_pos(pos['sam']['phi'], vmin=-145, vmax=+110, age=age),
    ))

print('</table>')
    


#print('<div style="font-size: 14px;"><br/>')
#print('logs: <a href="server.log">server</a> - <a href="control.log">control</a> - <a href="deck.log">deck</a>')
#print('</div>')

print('<div style="font-size: 14px;"><br/>')
print('Stacker code version {}<br>'.format(STACKER_VERSION))
print(stacker.now())
print('</div>')

