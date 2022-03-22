#!/usr/bin/env python3 
#import os
# Web server
from http.server import HTTPServer, SimpleHTTPRequestHandler

from pathlib import Path
import re
tile_re = re.compile('^/maps/([a-zA-Z0-9_]+)/tiles/(\d+)/(\d+)/(\d+)\.png$')




class TileCoordinates():
    def __init__(self):
        self.remaps = {
            'Mandelbrot': {'z':3, 'x':5, 'y':4},
            'MandelbrotUF': {'z':3, 'x':5, 'y':5},
            'Atlas_of_Materials': {'z':2, 'x':1, 'y':1}
            }
        
        for name, pos in self.remaps.items():
            tile_position = [ pos['x'], pos['y'], pos['z'] ]
            x_start, x_end, y_start, y_end = self.region(tile_position)
            self.remaps[name]['x_start'] = x_start
            self.remaps[name]['x_end'] = x_end
            self.remaps[name]['y_start'] = y_start
            self.remaps[name]['y_end'] = y_end
            
        self.generate_list = ['Mandelbrot', 'MandelbrotUF']
    
    def num_tiles(self, tile_position):
        xi, yi, z_zoom = tile_position
        num_e = 2**z_zoom
        num_t = num_e*num_e
        
        return num_e, num_t

        
    def region(self, tile_position):
        '''Returns the range for this particular tile, in relative units.'''
        
        xi, yi, z_zoom = tile_position
        num_e, num_t = self.num_tiles(tile_position)
        
        # The range covered by this specific tile
        x_span = 1.0/num_e
        x_start = 0.0 + xi*x_span
        x_end = x_start + x_span
        
        y_span = 1.0/num_e
        y_start = 0.0 + yi*y_span
        y_end = y_start + y_span
        
        return x_start, x_end, y_start, y_end
    
    def intersects(self, xc, yc, box):
        x_start, x_end, y_start, y_end = box
        return xc>x_start and xc<x_end and yc>y_start and yc<y_end
    
    def check_intersections(self, xc, yc):
        for name, pos in self.remaps.items():
            box = [ pos['x_start'], pos['x_end'], pos['y_start'], pos['y_end'] ]
            if self.intersects(xc, yc, box):
                return name
            
        return None
    
    def check_exists(self, name, tile_position):
        if name in self.generate_list:
            xi, yi, z_zoom = tile_position
            
            file_path = './maps/{}/tiles/{}/{}/{}.png'.format(name, z_zoom, xi, yi)
            tile_path = Path(Path.cwd(), file_path)
            if not tile_path.is_file():
                print('    Generating: {}'.format(file_path))
                import sys
                code_path = str( Path(Path.cwd(), '../') )
                code_path in sys.path or sys.path.append(code_path)
                code_path = str( Path(Path.cwd(), './maps/{}/'.format(name)) )
                code_path in sys.path or sys.path.append(code_path)
                from generate import generate_tiles
                
                output_dir = Path(Path.cwd(), './maps/{}/tiles/'.format(name))
                stack = [generate_tiles.Mandelbrot(verbosity=5)]
                g = generate_tiles.Generator(stack, output_dir=output_dir, verbosity=5)
                g.generate_tile(xi, yi, z_zoom, force=False)
                
            
        
        
    
    def remap(self, tile_position):
        xi, yi, z_zoom = tile_position
        num_e, num_t = self.num_tiles(tile_position)
        x_start, x_end, y_start, y_end = self.region(tile_position)
        xc, yc = (x_start+x_end)/2, (y_start+y_end)/2
        
        name = self.check_intersections(xc, yc)
        if name is None:
            return 'MultiMap', xi, yi, z_zoom
        
        # Apply coordinate transformation
        pos = self.remaps[name]
        zd = z_zoom-pos['z']
        z_zoom -= pos['z']
        xi = xi - pos['x']*( 2**zd )
        yi = yi - pos['y']*( 2**zd )
        
        self.check_exists(name, [xi, yi, z_zoom])
        
        return name, xi, yi, z_zoom
        

tile_coordinates = TileCoordinates()    

class HTTPHandler(SimpleHTTPRequestHandler):
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)    
    
    def do_GET(self):
        
        m = tile_re.match(self.path)
        if m:
            name, z, x, y = m.groups()
            z, x, y = int(z), int(x), int(y)
            
            if name=='MultiMap':
                name, x, y, z = tile_coordinates.remap([x, y, z])
                self.path = '/maps/{}/tiles/{}/{}/{}.png'.format(name, z, x, y)
                
            # Return the file now specified by self.path
            return super().do_GET()
            
        elif self.path.startswith('/images/'):
            return super().do_GET()
        
        #else:
            #self.send_error(404)
            #return
        
        # Normal behavior (return file or dir listing)
        return SimpleHTTPRequestHandler.do_GET(self)


#os.chdir('.')
print('Creating HTTPServer...')
server_object = HTTPServer(server_address=('', 2345), RequestHandlerClass=HTTPHandler)
print('Starting HTTPServer...')
server_object.serve_forever()


