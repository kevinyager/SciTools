#!/usr/bin/python3
from Base import *

import numpy as np
import matplotlib as mpl
mpl.use('Agg') # For headless
mpl.rcParams['mathtext.fontset'] = 'cm'
import pylab as plt

import os
import io
from PIL import Image


class TileMaker(Base):
    
    def __init__(self, name=None, verbosity=3):
        name = self.__class__.__name__ if name is None else name
        super().__init__(name=name, verbosity=verbosity)

    def plot(self, tile_position, size_pix=256, **kwargs):
        '''Return an image for this tile region.
        Return None if the tile is empty and should be ignored.'''
        img = Image.new(mode="RGBA", size=(size_pix,size_pix), color=(255,255,255))
        return img

    def empty(self, tile_position):
        '''Returns True if the given tile will be empty (devoid of content).
        You can use this to avoid plotting/saving empty tiles.'''
        
        #xi, yi, z_zoom = tile_position
        #num_e, num_t = self.num_tiles(tile_position)
        #x_start, x_end, y_start, y_end = self.region(tile_position)
        
        return False
        

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



    


class Inkscape(TileMaker):

    def __init__(self, infile, region_position, region_size, name=None, verbosity=3):
        name = self.__class__.__name__ if name is None else name
        super().__init__(name=name, verbosity=verbosity)
        
        self.infile = infile
        self.region_position = region_position
        self.region_size = region_size

    def compose_cmd(self, tile_position, size_pix, input_filename='input.svg', temp_filename="temp_export.png"):
        '''Create a string that is a valid commandline for executing the export.
        For instance, a typical command might be:
        inkscape --without-gui --export-area=-2488.10:-4649.36:5449.17:2317.17 --export-width=256 --export-png="out.png" papers.svg
        '''

        # Overall image area (i.e. the square that matches the z=0 view)
        x0t, y0t = self.region_position
        x1t, y1t = x0t+self.region_size, y0t+self.region_size

        
        s = 'inkscape --without-gui'
        
        #--export-area=x0:y0:x1:y1
        x_start, x_end, y_start, y_end = self.region(tile_position)
        x0 = x0t + self.region_size*x_start
        x1 = x0t + self.region_size*x_end
        y0 = y0t + self.region_size*(1 - y_end)
        y1 = y0t + self.region_size*(1 - y_start)
        s += ' --export-area={:.4f}:{:.4f}:{:.4f}:{:.4f}'.format(x0, y0, x1, y1)
        
        s += ' --export-width={:d}'.format(size_pix)
        s += ' --export-png="{}"'.format(temp_filename)
        s += ' {}'.format(input_filename)
        
        return s
        
    
    def plot(self, tile_position, size_pix=256, temp_filename='./tmp/temp_export.png', **kwargs):

        x_start, x_end, y_start, y_end = self.region(tile_position)
        self.msg('Inkscape export ({:.6f}-{:.6f}, {:.6f}-{:.6f})'.format(x_start, x_end, y_start, y_end), threshold=5, indent=5)
        
        cmd = self.compose_cmd(tile_position, size_pix, input_filename=self.infile, temp_filename=temp_filename)
        os.system(cmd)

        img = Image.open(temp_filename)
        
        return img


class Equation(TileMaker):
    
    def equation(self, X, Y):
        eq = np.square(np.cos(Y*5*2*np.pi))*np.exp( - np.square(X)/0.25 )
        eq += np.exp(- np.square(X-0.9)/0.05)*np.square(np.cos(X*100*2*np.pi))
        return eq
    
    
    def plot(self, tile_position, size_pix=256, ret_img=True, save=None, show=False, plot_range=[None,None,None,None], plot_buffers=[0,0,0,0], figsize=10, **kwargs):
        
        
        xi, yi, z_zoom = tile_position
        num_e, num_t = self.num_tiles(tile_position)
        
        # The range covered by this specific tile
        x_start, x_end, y_start, y_end = self.region(tile_position)
        self.msg('Equation plotting ({:.6f}-{:.6f}, {:.6f}-{:.6f})'.format(x_start, x_end, y_start, y_end), threshold=5, indent=5)
        x_axis = np.linspace(x_start, x_end, num=size_pix)
        y_axis = np.linspace(y_start, y_end, num=size_pix)
        X, Y = np.meshgrid(x_axis, y_axis)
        
        Z = self.equation(X, Y)
        
        
        self.fig = plt.figure( figsize=(figsize,figsize), facecolor='white' )
        left_buf, right_buf, bottom_buf, top_buf = plot_buffers
        fig_width = 1.0-right_buf-left_buf
        fig_height = 1.0-top_buf-bottom_buf
        self.ax = self.fig.add_axes( [left_buf, bottom_buf, fig_width, fig_height] )
        
        cmap = 'viridis'

        self.im = plt.imshow(Z, cmap=cmap, vmin=0, vmax=1, interpolation='nearest', origin='upper')
        
        #s = 'zoom = {:d}\n({:d}, {:d})'.format(z_zoom, xi, yi)
        #self.ax.text(size_pix/2, size_pix/2, s, size=100, color='white', horizontalalignment='center', verticalalignment='center')
        
        
        self.ax.axis('off')
        
        dpi = size_pix/figsize
        if save:
            plt.savefig(save, dpi=dpi, transparent=True)
        
        if show:
            #self._plot_interact()
            plt.show()
            
        if False: #ret_img_array:
            self.fig.canvas.draw()
            #img_array = np.fromstring(self.fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
            img_array = np.frombuffer(self.fig.canvas.tostring_rgb(), dtype=np.uint8)
            img_array = img_array.reshape(self.fig.canvas.get_width_height()[::-1] + (3,))
            
            plt.close(self.fig.number)
            
            return img_array
        
        if ret_img:
            buf = io.BytesIO()
            plt.savefig(buf, dpi=dpi, transparent=True)
            buf.seek(0)
            img = Image.open(buf).copy() # Make a copy so that we can close the IO buffer
            buf.close()
            
            plt.close(self.fig.number)
            return img
            
        plt.close(self.fig.number)
        

class Generator(Base):
    
    def __init__(self, stack, output_dir='./', size_pix=256, name='Generator', verbosity=3):
        
        super().__init__(name=name, verbosity=verbosity)
        self.size_pix = size_pix
        self.stack = stack
        self.output_dir = output_dir
        
    
    def generate(self, z_initial=0, z_final=5, force=True):
        
        tiles_total = np.sum([(2**z_zoom)**2 for z_zoom in range(z_initial, z_final+1)])
        self.msg('Will generate {:d} tiles for {:d} zoom levels'.format(tiles_total, z_final-z_initial+1))

        self.timing_start()
        tile_current = 0
        for z_zoom in range(z_initial, z_final+1):
            num_e = 2**z_zoom
            num_t = num_e*num_e
            
            self.msg('ZoomDepth z = {:d}; generating {:d}??{:d} = {:d} tiles'.format(z_zoom, num_e, num_e, num_t), 2, 0)
            
            newdir = Path(self.output_dir, '{:d}'.format(z_zoom))
            newdir.mkdir(exist_ok=True)
            
            
            for x in range(0, num_e):
                self.msg('x = {:d}/{:d} (z_zoom = {:d}/{:d})'.format(x, num_e, z_zoom, z_final), indent=1)
                for y in range(0, num_e):
                    self.msg('(x, y) = ({:d}, {:d})'.format(x, y), 3, 2)
                    
                    # Print progress message
                    tile_current += 1
                    self.timing_progress_msg(tile_current, tiles_total, threshold=3, indent=4, every=25)

                    self.generate_tile(x, y, z_zoom, force=force)
                    
                    if tile_current%10==0:
                        # Do a very short wait, to give time for a Ctrl+C to be caught
                        self.msg('sleep', 6, 6)
                        time.sleep(0.1)

    
    def generate_tile(self, x, y, z_zoom, force=True):
        outdir = Path(self.output_dir, '{:d}'.format(z_zoom), '{:d}'.format(x))
        outdir.mkdir(exist_ok=True)
        
        outfile = Path(outdir, '{:d}.png'.format(y))
        
        if not force and outfile.is_file():
            self.msg('skipping ({:d}, {:d}) since file exists: {}'.format(x, y, outfile), 4, 3)
            return
        
        #if len(self.stack)>1:
        if True:
            # Build up the image based on the stack of plotting objects
            img = None
            for layer in self.stack:
                img_current = layer.plot(tile_position=[x,y,z_zoom], size_pix=self.size_pix)
                if img_current is not None:
                    if img is None:
                        img = self.blank_img()
                    img_current.convert('RGBA')
                    #img.paste(img_current, (0, 0), img_current)
                    img = Image.alpha_composite(img, img_current)
                
        else:
            img = self.stack[0].plot(tile_position=[x,y,z_zoom], size_pix=self.size_pix)
        
        
        if img is not None: # Don't save empty tiles
            img.save(outfile)
        
        
        self.msg('Saved tile ({:d}, {:d}) to: {}'.format(x, y, outfile), 4, 3)
        

    def blank_img(self):
        '''Return a blank PIL image object.
        We make it fully white, but also fully transparent.'''
        #return Image.new(mode="RGBA", size=(self.size_pix,self.size_pix), color=(255,255,255,0))

        # White background
        return Image.new(mode="RGBA", size=(self.size_pix,self.size_pix), color=(255,255,255,255))

        

if __name__ == '__main__':
    

    region_w, region_h = 5184, 3456
    region_size = max(region_w, region_h)

    region_position = [ 0, 0 - 0.5*(region_size-region_h) ]

    VERBOSITY = 5
    stack = [
        #Equation(verbosity=VERBOSITY),
        Inkscape(infile='../../layout06.svg', region_position=region_position, region_size=region_size, verbosity=VERBOSITY),
    ]    

    
    g = Generator(stack, output_dir='../tiles/', verbosity=VERBOSITY)
    g.generate(z_initial=0, z_final=7, force=True)


