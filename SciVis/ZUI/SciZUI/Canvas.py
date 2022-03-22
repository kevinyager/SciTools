#!/usr/bin/python3

from SciZUI.Base import *


from PIL import Image
#import scipy.misc # Deprecated for image handling
import imageio
    #image = scipy.misc.imread(infile) # Deprecated
    #image = imageio.imread(infile)


class ImageCanvas(Base):
    
    def __init__(self, infile=None, name=None, verbosity=3, **kwargs):
        
        if name is None:
            if infile is not None:
                name = 'Im({})'.format(infile.name)
            else:
                name = self.__class__.__name__
        
        super().__init__(name=name, verbosity=verbosity)
        
        self.info = {}
        
        if infile is None:
        
            #self.width, self.height = 1280, 720 # 720p (HD)
            self.width, self.height = 3840, 2160 # 4k resolution (UHD)
            #self.width, self.height = 7680, 2160 # 4k resolution (UHD) double-wide
            
            #self.width, self.height = 5000, int(5000/1.4142) # A4 aspect ratio
            
            #self.width, self.height = 7680, 4320 # 8k resolution
            #self.width, self.height = 7680, 5760 # 8k horizontal; 4:3 aspect
            
            self.image = self.blank_image(fill=255)
            
        else:
            self.image = self.imread(infile)
            h, w, c = self.image.shape
            self.width, self.height = w, h
            
            self.info['name'] = Path(infile).name
            self.info['infile'] = str(infile)
            self.info['path'] = Path(infile).resolve()
            
        self.info['width'] = self.width
        self.info['height'] = self.height


    def blank_image(self, fill=255):
        
        # Create a blank image
        if isinstance(fill, (int,float)):
            image = np.ones((self.height, self.width, 3))*fill
            
        else:
            image = np.zeros((self.height, self.width, 3))
            image[:,:,0] = fill[0]
            image[:,:,1] = fill[1]
            image[:,:,2] = fill[2]
            
        return image
    
    
    def imread(self, infile):    
        #image = scipy.misc.imread(infile) # Deprecated
        image = imageio.imread(str(infile))
        if image.ndim==2:
            # Convert single-channel (grayscale) to 3-channel
            image = np.stack((image,)*3, axis=-1)
        #h, w, c = image.shape
        #aspect_ratio = w/h
        
        return image
    
    
    def imresize(self, image, size, handle_float=False):
        '''Replacement for deprecated scipy.misc.imresize function.'''
        #image = scipy.misc.imresize(image, size) # Deprecated
        
        h, w, c = image.shape
        if isinstance(size, (int, float)):
            hn = int(h*size)
            wn = int(w*size)
        elif len(size)==2:
            hn, wn = size
        else:
            self.print('Error in imresize.')
        
        if handle_float:
            # Convert from floating-point (0.0 to 1.0 scale) to regular
            # integer (0 to 255 scale).
            image = np.copy(image)*255
            image = np.array( Image.fromarray( image.astype(np.uint8) ).resize((wn,hn)) )
            image = image/255
        else:
            image = np.array( Image.fromarray( image.astype(np.uint8) ).resize((wn,hn)) )
            #image = resize(image, output_shape=(hn,wn), preserve_range=True) # Doesn't work
                            
        return image
    
    
    def resize(self, size):
        '''Resize the current canvas (self.image).'''
        self.image = self.imresize(self.image, size)


    def load_image(self, infile, height=None, width=None):
        '''Load an image from disk, resizing by default to fit within our
        current canvas (self.image size).
        Handle special-cases (like grayscale) so that the output 
        is numpy array of expected format.'''
            
        image = self.imread(infile)
        
        if image.ndim==2:
            # Convert single-channel (grayscale) to 3-channel
            image = np.stack((image,)*3, axis=-1)
        h, w, c = image.shape
        
        if height is None and width is None:
            size = self.height/h
        elif width is not None:
            size = width/w
        else:
            size = height/h
        
        image = self.imresize(image, size=size)
        h, w, c = image.shape
        #aspect_ratio = w/h
        
        return image, h, w     


    def add_border(self, canvas, region, border_width):
        '''Add a border to the provided sub-region of the provided canvas.'''
        
        xo, yo, w, h = region
        bw = int( max(border_width, 1) )
        border_element = [127, 127, 127] # Grey
        
        canvas[ 0+yo:h+yo, 0+xo:0+xo+bw, : ] = border_element # Left col
        canvas[ 0+yo:h+yo, w+xo-bw:w+xo, : ] = border_element # Right col
        canvas[ 0+yo:0+yo+bw, 0+xo:w+xo, : ] = border_element # Top row
        canvas[ h+yo-bw:h+yo, 0+xo:w+xo, : ] = border_element # Bottom row


    def border(self, border_width):
        '''Add a border to the current canvas (self.image).'''
        xo, yo = 0, 0
        h, w, c = self.image.shape
        self.add_border(self.image, [xo, yo, w, h], border_width)
        
        
    def add_info_layout_item(self, infile, region):
        xo, yo, w, h = region
        self.info['layout'].append({
            'name': infile.name,
            'infile': str(infile),
            'path': Path(infile).resolve(),
            'xo': xo, 
            'yo': yo,
            'width': w,
            'height': h,
            })
    

    def save(self, outfile):
        '''Save the current canvas (self.image) to disk.'''
        
        outfile = str(outfile.resolve())
        
        imageio.imsave(outfile, self.image.astype(np.uint8))
    


class SVGCanvas(Base):
    
    def __init__(self, infile=None, name=None, verbosity=3, **kwargs):
        
        if name is None:
            if infile is not None:
                name = 'Im({})'.format(infile.name)
            else:
                name = self.__class__.__name__
        
        super().__init__(name=name, verbosity=verbosity)
        
        self.info = {}
        
        if infile is None:
            # TODO
            self.svg = self.blank_svg()
            
        else:
            with open(infile, 'r') as file:
                self.svg = file.read()
            
            self.info['name'] = Path(infile).name
            self.info['infile'] = str(infile)
            self.info['path'] = Path(infile).resolve()
        
        
    def replace(self, old, new):
        self.svg = self.svg.replace(old, new)
        
        
    def save(self, outfile):
        with open(outfile, 'w') as file:
            file.write(self.svg)
        
        
