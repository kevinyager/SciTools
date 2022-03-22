#!/usr/bin/python
# -*- coding: utf-8 -*-
# vi: ts=4 sw=4

################################################################################
#  Code for defining a 'Sample' object, which keeps track of its state, and 
# simplifies the task of aligning, measuring, etc.
################################################################################


import time
import re
import os
import shutil


from BLEX.Base import *        

class CoordinateSystem(Base):
    """
    A generic class defining a coordinate system. Several coordinate systems
    can be layered on top of one another (with a reference to the underlying
    coordinate system given by the 'base_stage' pointer). When motion of a given
    CoordinateSystem is requested, the motion is passed (with coordinate
    conversion) to the underlying stage.
    """
    
    hint_replacements = { 'positive': 'negative',
                         'up': 'down',
                         'left': 'right',
                         'towards': 'away from',
                         'downstream': 'upstream',
                         'inboard': 'outboard',
                         'clockwise': 'counterclockwise',
                         'CW': 'CCW',
                         'increases': 'decreases',
                         }


    # Core methods
    ########################################
    
    def __init__(self, name='<unnamed>', base=None, **kwargs):
        '''Create a new CoordinateSystem (e.g. a stage or a sample).
        
        Parameters
        ----------
        name : str
            Name for this stage/sample.
        base : Stage
            The stage on which this stage/sample sits.
        '''        
        
        super().__init__(name=name, **kwargs) # Base
        
        self.name = name
        self.base_stage = base
        
        
        self.enabled = True
        
        self.md = {}
        self._marks = {}

        self._set_axes_definitions()
        self._init_axes(self._axes_definitions)
        
        # Cache of positions/velocities
        self._posv_cache = {}
        self._posv_cache_timestamp = 0
        
        
    def _set_axes_definitions(self):
        '''Internal function which defines the axes for this stage. This is kept
        as a separate function so that it can be over-ridden easily.'''
        
        # The _axes_definitions array holds a list of dicts, each defining an axis
        self._axes_definitions = []
        
        
    def _init_axes(self, axes):
        '''Internal method that generates method names to control the various axes.'''
        
        # Note: Instead of defining CoordinateSystem() having methods '.x', '.xr', 
        # '.y', '.yr', etc., we programmatically generate these methods when the 
        # class (and subclasses) are instantiated.
        # Thus, the Axis() class has generic versions of these methods, which are
        # appropriated renamed (bound, actually) when a class is instantiated.
        
        self._axes = {}
        
        for axis in axes:
            
            axis_object = Axis(axis['name'], axis['motor'], axis['enabled'], axis['scaling'], axis['units'], axis['hint'], self.base_stage, stage=self, common=self._common)
            self._axes[axis['name']] = axis_object
            
            if 'limits' in axis:
                axis_object.limits = axis['limits']
            
               
            # Bind the methods of axis_object to appropriately-named methods of 
            # the CoordinateSystem() class.
            setattr(self, axis['name'], axis_object.get_position )
            setattr(self, axis['name']+'abs', axis_object.move_absolute )
            setattr(self, axis['name']+'r', axis_object.move_relative )
            setattr(self, axis['name']+'pos', axis_object.get_position )
            setattr(self, axis['name']+'posMotor', axis_object.get_motor_position )
            
            
            setattr(self, axis['name']+'vel', axis_object.set_velocity )
            
            
            setattr(self, axis['name']+'units', axis_object.get_units )
            setattr(self, axis['name']+'hint', axis_object.get_hint )
            setattr(self, axis['name']+'info', axis_object.get_info )
            
            setattr(self, axis['name']+'set', axis_object.set_current_position )
            setattr(self, axis['name']+'o', axis_object.goto_origin )
            setattr(self, axis['name']+'setOrigin', axis_object.set_origin )
            setattr(self, axis['name']+'mark', axis_object.mark )
            
            setattr(self, axis['name']+'search', axis_object.search )
            setattr(self, axis['name']+'scan', axis_object.scan )
            setattr(self, axis['name']+'c', axis_object.center )
            
            
    def comment(self, text, logbooks=None, tags=None, append_md=True, **md):
        '''Add a comment related to this CoordinateSystem.'''
        
        text += '\n\n[comment for CoordinateSystem: {} ({})].'.format(self.name, self.__class__.__name__)
        
        if append_md:
        
            md_current = { k : v for k, v in RE.md.items() } # Global md
            md_current.update(get_beamline().get_md()) # Beamline md

            # Self md
            #md_current.update(self.get_md())
            
            # Specified md
            md_current.update(md)
            
            text += '\n\n\nMetadata\n----------------------------------------'
            for key, value in sorted(md_current.items()):
                text += '\n{}: {}'.format(key, value)
            
        
        logbook.log(text, logbooks=logbooks, tags=tags)
    
    
    def set_base_stage(self, base):
        
        self.base_stage = base
        self._init_axes(self._axes_definitions)
        

    # Convenience/helper methods
    ########################################
    
    
    def multiple_string_replacements(self, text, replacements, word_boundaries=False):
        '''Peform multiple string replacements simultaneously. Matching is case-insensitive.
        
        Parameters
        ----------
        text : str
            Text to return modified
        replacements : dictionary
            Replacement pairs
        word_boundaries : bool, optional
            Decides whether replacements only occur for words.
        '''
        
        # Code inspired from:
        # http://stackoverflow.com/questions/6116978/python-replace-multiple-strings
        # Note inclusion of r'\b' sequences forces the regex-match to occur at word-boundaries.

        if word_boundaries:
            replacements = dict((r'\b'+re.escape(k.lower())+r'\b', v) for k, v in replacements.items())
            pattern = re.compile("|".join(replacements.keys()), re.IGNORECASE)
            text = pattern.sub(lambda m: replacements[r'\b'+re.escape(m.group(0).lower())+r'\b'], text)
            
        else:
            replacements = dict((re.escape(k.lower()), v) for k, v in replacements.items())
            pattern = re.compile("|".join(replacements.keys()), re.IGNORECASE)
            text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)
        
        return text
    

    def _hint_replacements(self, text):
        '''Convert a motor-hint into its logical inverse.'''
        
        # Generates all the inverse replacements
        replacements = dict((v, k) for k, v in self.hint_replacements.items())
        replacements.update(self.hint_replacements)
        
        return self.multiple_string_replacements(text, replacements, word_boundaries=True)



    # Control methods
    ########################################
    def setTemperature(self, temperature, verbosity=3):
        #if verbosity>=1:
            #print('Temperature functions not implemented in {}'.format(self.__class__.__name__))
        self.msg('Temperature functions not implemented in {}'.format(self.__class__.__name__), 1)
        
        
    def temperature(self, verbosity=3):
        #if verbosity>=1:
            #print('Temperature functions not implemented in {}'.format(self.__class__.__name__))
        self.msg('Temperature functions not implemented in {}'.format(self.__class__.__name__), 1)
            
        return 0.0

        
    # Motion methods
    ########################################
    
    
    def enable(self):
        self.enabled = True
    
    
    def disable(self):
        self.enabled = False
    
    
    def is_enabled(self):
        return self.enabled
    
                          
    def pos(self, verbosity=3):
        '''Return (and print) the positions of all axes associated with this
        stage/sample.'''
        
        out = {}
        for axis_name, axis_object in sorted(self._axes.items()):
            out[axis_name] = axis_object.get_position(verbosity=verbosity)
            #if verbosity>=2: print('') # \n
            
        return out


    def posv(self, verbosity=0):
        '''Return the positions and motor-velocities of all axes associated with this
        stage/sample.'''
        
        for axis_name, axis_object in sorted(self._axes.items()):
            if axis_object.last_change_timestamp>self._posv_cache_timestamp:
                self._posv_cache[axis_name+'__timestamp'] = axis_object.last_change_timestamp
                self._posv_cache[axis_name] = axis_object.get_position(verbosity=verbosity)
                self._posv_cache[axis_name+'vel'] = axis_object.set_velocity(verbosity=verbosity)

        self._posv_cache_timestamp = time.time()
        
        return self._posv_cache

                  
    def origin(self, verbosity=3):
        '''Returns the origin for axes.'''
        
        out = {}
        for axis_name, axis_object in sorted(self._axes.items()):
            origin = axis_object.get_origin()
            #if verbosity>=2: print('{:s} origin = {:.3f} {:s}'.format(axis_name, origin, axis_object.get_units()))
            txt = '{:s} origin = {:.3f} {:s}'.format(axis_name, origin, axis_object.get_units())
            self.msg(txt, 2, verbosity=verbosity)
            out[axis_name] = origin
            
        return out
            
        
    def gotoOrigin(self, axes=None):
        '''Go to the origin (zero-point) for this stage. All axes are zeroed,
        unless one specifies the axes to move.'''
        
        # TODO: Guard against possibly buggy behavior if 'axes' is a string instead of a list.
        # (Python will happily iterate over the characters in a string.)
        
        if axes is None:
            axes_to_move = self._axes.values()
            
        else:
            axes_to_move = [self._axes[axis_name] for axis_name in axes]
                
        for axis in axes_to_move:
            axis.goto_origin()
        
        
    def setOrigin(self, axes=None, positions=None):
        '''Define the current position as the zero-point (origin) for this stage/
        sample. The axes to be considered in this redefinition should be supplied
        as a list.
        
        If the optional positions parameter is passed, then those positions are
        used to define the origins for the axes.'''
        
        if axes is None:
            axes = self._axes.keys()

        if positions is None:
        
            for axis in axes:
                getattr(self, axis+'setOrigin')()
                self._axes[axis].last_change_timestamp = time.time()
                
        else:
            for axis, pos in zip(axes, positions):
                getattr(self, axis+'setOrigin')(pos)
                self._axes[axis].last_change_timestamp = time.time()
    
    
    def gotoAlignedPosition(self):
        '''Goes to the currently-defined 'aligned' position for this stage. If
        no specific aligned position is defined, then the zero-point for the stage
        is used instead.'''
        
        # TODO: Optional offsets? (Like goto mark?)
        
        if 'aligned_position' in self.md and self.md['aligned_position'] is not None:
            for axis_name, position in self.md['aligned_position'].items():
                self._axes[axis_name].move_absolute(position)
        
        else:
            self.gotoOrigin()
        

            
            

    # Motion logging
    ########################################
            
    def setAlignedPosition(self, axes):
        '''Saves the current position as the 'aligned' position for this stage/
        sample. This allows one to return to this position later. One must
        specify the axes to be considered.

        WARNING: Currently this position data is not saved persistently. E.g. it will 
        be lost if you close and reopen the console.
        '''
        
        positions = {}
        for axis_name in axes:
            positions[axis_name] = self._axes[axis_name].get_position(verbosity=0)
        
        self.attributes['aligned_position'] = positions

            
    def mark(self, label, *axes, **axes_positions):
        '''Set a mark for the stage/sample/etc.
        
        'Marks' are locations that have been labelled, which is useful for 
        later going to a labelled position (using goto), or just to keep track
        of sample information (metadata).
        
        By default, the mark is set at the current position. If no 'axes' are 
        specified, all motors are logged. Alternately, axes (as strings) can 
        be specified. If axes_positions are given as keyword arguments, then 
        positions other than the current position can be specified.        
        '''
        
        positions = {}
        
        if len(axes)==0 and len(axes_positions)==0:
            
            for axis_name in self._axes:
                positions[axis_name] = self._axes[axis_name].get_position(verbosity=0)
                
        else:
            for axis_name in axes:
                positions[axis_name] = self._axes[axis_name].get_position(verbosity=0)
                
            for axis_name, position in axes_positions.items():
                positions[axis_name] = position
        
        self._marks[label] = positions
        
        
    def marks(self, verbosity=3):
        '''Get a list of the current marks on the stage/sample/etc. 'Marks' 
        are locations that have been labelled, which is useful for later
        going to a labelled position (using goto), or just to keep track
        of sample information (metadata).'''
        
        #if verbosity>=3:
            #print('Marks for {:s} (class {:s}):'.format(self.name, self.__class__.__name__))
        txt = 'Marks for {:s} (class {:s}):'.format(self.name, self.__class__.__name__)
        self.msg(txt, 3, verbosity=verbosity)
        
        if verbosity>=2:
            for label, positions in self._marks.items():
                self.print(label)
                for axis_name, position in sorted(positions.items()):
                    self.print('  {:s} = {:.4f} {:s}'.format(axis_name, position, self._axes[axis_name].get_units()))
            
        return self._marks
    
    
    def goto(self, label, verbosity=3, **additional):
        '''Move the stage/sample to the location given by the label. For this
        to work, the specified label must have been 'marked' at some point.
        
        Additional keyword arguments can be provided. For instance, to move 
        3 mm from the left edge:
          sam.goto('left edge', xr=+3.0)
        '''
        
        if label not in self._marks:
            #if verbosity>=1:
                #print("Label '{:s}' not recognized. Use '.marks()' for the list of marked positions.".format(label))
            txt = "Label '{:s}' not recognized. Use '.marks()' for the list of marked positions.".format(label)
            self.msg_warning(txt, 1, verbosity=verbosity)
            return
            
        for axis_name, position in sorted(self._marks[label].items()):
            
            if axis_name+'abs' in additional:
                # Override the marked value for this position
                position = additional[axis_name+'abs']
                del(additional[axis_name+'abs'])
            
            
            #relative = 0.0 if axis_name+'r' not in additional else additional[axis_name+'r']
            if axis_name+'r' in additional:
                relative = additional[axis_name+'r']
                del(additional[axis_name+'r'])
            else:
                relative = 0.0
            
            self._axes[axis_name].move_absolute(position+relative, verbosity=verbosity)


        # Handle any optional motions not already covered
        for command, amount in additional.items():
            if command[-1]=='r':
                getattr(self, command)(amount, verbosity=verbosity)
            elif command[-3:]=='abs':
                getattr(self, command)(amount, verbosity=verbosity)
            else:
                #print("Keyword argument '{}' not understood (should be 'r' or 'abs').".format(command))
                self.msg_warning("Keyword argument '{}' not understood (should be 'r' or 'abs').".format(command), 0, verbosity=verbosity)


    # State methods
    ########################################
    def save_state(self):
        '''Outputs a string you can use to re-initialize this object back 
        to its current state.'''
        #TODO: Save to databroker?
        
        state = { 'origin': {} }
        for axis_name, axis in self._axes.items():
            state['origin'][axis_name] = axis.origin
        
        return state
    

    def restore_state(self, state):
        '''Outputs a string you can use to re-initialize this object back 
        to its current state.'''
        
        for axis_name, axis in self._axes.items():
            axis.origin = state['origin'][axis_name]


    # End class CoordinateSystem(object)
    ########################################


class Motor(object):
    '''Generic motor. Should be subclassed to control a specific piece of hardware.
    '''
    def __init__(self, name='<unnamed>', **kwargs):
        self.name = name
        
    # End class Motor(object)
    ########################################

class MotorDummy(Motor):
    '''A 'pretend' motor that doesn't actually connect to hardware.'''
    def __init__(self, name='<unnamed>', **kwargs):
        self.name = name
        self.position = 0
        self.velocity = 0.5
        
    def get_position(self, **kwargs):
        return self.position
    
    def set_position(self, position, **kwargs):
        
        if 'velocity' in kwargs:
            self.velocity = kwargs['velocity']
        difference = position - self.get_position()
        time_to_complete = abs(difference/self.velocity)
        time.sleep(time_to_complete)
        
        self.position = position
        
    def get_velocity(self, **kwargs):
        return self.velocity
    
    def set_velocity(self, velocity=None, **kwargs):
        self.velocity = velocity
        return self.velocity
        
        
    # End class MotorDummy(Motor)
    ########################################
    

class Axis(Base):
    '''Generic motor axis.
    
    Meant to be used within a CoordinateSystem() or Stage() object.
    '''
    
    def __init__(self, name, motor, enabled, scaling, units, hint, base, stage=None, origin=0.0, limits=None, common=None):
        
        super().__init__(name=name, common=common) # Base
        
        self.name = name
        self.motor = motor
        self.enabled = enabled
        self.scaling = scaling
        self.units = units
        self.hint = hint
        
        self.base_stage = base
        self.stage = stage
        
        self.origin = 0.0
        
        
        self.limits = limits # [min, max] in the underlying motor coordinates
        
        self.last_change_timestamp = time.time()
        
        self._move_settle_max_time = 10.0
        self._move_settle_period = 0.05
        self._move_settle_tolerance = 0.01



    # Coordinate transformations
    ########################################
        
        
    def cur_to_base(self, position):
        '''Convert from this coordinate system to the coordinate in the (immediate) base.'''
        
        base_position = self.get_origin() + self.scaling*position
        
        return base_position
    
    
    def base_to_cur(self, base_position):
        '''Convert from this base position to the coordinate in the current system.'''
        
        position = (base_position - self.get_origin())/self.scaling
        
        return position
    
    
    def cur_to_motor(self, position):
        '''Convert from this coordinate system to the underlying motor.'''
        
        if self.motor is not None:
            return self.cur_to_base(position)
        
        else:
            base_position = self.cur_to_base(position)
            return self.base_stage._axes[self.name].cur_to_motor(base_position)
        
    def motor_to_cur(self, motor_position):
        '''Convert a motor position into the current coordinate system.'''
        
        if self.motor is not None:
            return self.base_to_cur(motor_position)
        
        else:
            base_position = self.base_stage._axes[self.name].motor_to_cur(motor_position)
            return self.base_to_cur(base_position)
        
            
            
    # Programmatically-defined methods
    ########################################
    # Note: Instead of defining CoordinateSystem() having methods '.x', '.xr', 
    # '.xp', etc., we programmatically generate these methods when the class 
    # (and subclasses) are instantiated.
    # Thus, the Axis() class has generic versions of these methods, which are
    # appropriated renamed (bound, actually) when a class is instantiated.
    def get_position(self, verbosity=3):
        '''Return the current position of this axis (in its coordinate system).
        By default, this also prints out the current position.'''
        
        
        if self.motor is not None:
            #base_position = self.motor.position # Bluesky
            base_position = self.motor.get_position()
            
        else:
            verbosity_c = verbosity if verbosity>=4 else 0
            base_position = getattr(self.base_stage, self.name+'pos')(verbosity=verbosity_c)
            
        position = self.base_to_cur(base_position)
        
        
        if verbosity>=2:
            if self.stage:
                stg = self.stage.name
            else:
                stg = '?'

            #if verbosity>=5 and self.motor is not None:
                #print( '{:s} = {:.3f} {:s}'.format(self.motor.name, base_position, self.get_units()) )
            if self.motor is not None:
                txt = '{:s} = {:.3f} {:s}'.format(self.motor.name, base_position, self.get_units())
                self.msg(txt, 5, verbosity=verbosity)
            
            self.print( '{:s}.{:s} = {:.3f} {:s} (origin = {:.3f})'.format(stg, self.name, position, self.get_units(), self.get_origin()) )
            
            
        return position
    
    
    def get_motor_position(self, verbosity=3):
        '''Returns the position of this axis, traced back to the underlying
        motor.'''
        
        if self.motor is not None:
            #return self.motor.position # Bluesky
            return self.motor.get_position()
        
        else:
            return getattr(self.base_stage, self.name+'posMotor')(verbosity=verbosity)
            #return self.base_stage._axes[self.name].get_motor_position(verbosity=verbosity)
    
    
    def move_absolute(self, position=None, wait=True, verbosity=3):
        '''Move axis to the specified absolute position. The position is given
        in terms of this axis' current coordinate system. The "defer" argument
        can be used to defer motions until "move" is called.'''
        
        
        if position is None:
            # If called without any argument, just print the current position
            return self.get_position(verbosity=verbosity)
        
        # Account for coordinate transformation
        base_position = self.cur_to_base(position)
        
        if self.is_enabled():
            
            if self.motor:
                #self.motor.user_setpoint.value = base_position # Bluesky
                
                # Enforce motor limits (if any)
                if self.limits is None or (base_position>=self.limits[0] and base_position<=self.limits[1]):
                    # Move the motor
                    self.last_change_timestamp = time.time()
                    self.motor.set_position(base_position)
                else:
                    if verbosity>=1:
                        self.print('motor position {:.3f} is outside range [{:.3f}, {:.3f}] for Axis {} (stage {})'.format(base_position, self.limits[0], self.limits[1], self.name, self.stage.name))
                    return
                
            else:
                # Call self.base_stage.xabs(base_position)
                getattr(self.base_stage, self.name+'abs')(base_position, verbosity=0)


            stg = self.stage.name if self.stage else '?'

            if verbosity>=2:
                
                # Show a realtime output of position
                start_time = time.time()
                current_position = self.get_position(verbosity=0)
                while abs(current_position-position)>self._move_settle_tolerance and (time.time()-start_time)<self._move_settle_max_time:
                    current_position = self.get_position(verbosity=0)
                    self.print( '{:s}.{:s} = {:5.3f} {:s}      \r'.format(stg, self.name, current_position, self.get_units()), end='')
                    time.sleep(self._move_settle_period)
                    
                    
            #if verbosity>=1:
                #current_position = self.get_position(verbosity=0)
                #print( '{:s}.{:s} = {:5.3f} {:s}        '.format(stg, self.name, current_position, self.get_units()))

                
        elif verbosity>=1:
            self.print( 'Axis %s disabled (stage %s).' % (self.name, self.stage.name) )
        
        
        
    def move_relative(self, move_amount=None, verbosity=3):
        '''Move axis relative to the current position.'''
        
        if move_amount is None:
            # If called without any argument, just print the current position
            return self.get_position(verbosity=verbosity)
        
        target_position = self.get_position(verbosity=0) + move_amount
        
        return self.move_absolute(target_position, verbosity=verbosity)
    
    
    
    def set_velocity(self, velocity=None, verbosity=3):
        
        if velocity is None:
            # Treat this as a query of the current velocity
            velocity = self.motor.get_velocity()
            stg = self.stage.name if self.stage else '?'
            if verbosity>=3:
                self.print( '{:s}.{:s}vel = {:.3f} {:s}/s'.format(stg, self.name, velocity, self.get_units()) )
            return velocity
        
        if self.motor:
            self.last_change_timestamp = time.time()
            self.motor.set_velocity(velocity)
            return self.motor.get_velocity()
            
        else:
            # Call self.base_stage.xvel(velocity)
            return getattr(self.base_stage, self.name+'vel')(velocity, verbosity=0)
    
    
    
    def goto_origin(self):
        '''Move axis to the currently-defined origin (zero-point).'''
        
        self.move_absolute(0)
    
    
    def set_origin(self, origin=None):
        '''Sets the origin (zero-point) for this axis. If no origin is supplied,
        the current position is redefined as zero. Alternatively, you can supply
        a position (in the current coordinate system of the axis) that should
        henceforth be considered zero.'''
        
        if origin is None:
            # Use current position
            if self.motor is not None:
                #self.origin = self.motor.position # Bluesky
                self.origin = self.motor.get_position()
                
            else:
                if self.base_stage is None:
                    self.msg_error("%s %s has 'base_stage' and 'motor' set to 'None'." % (self.__class__.__name__, self.name))
                else:
                    self.origin = getattr(self.base_stage, self.name+'pos')(verbosity=0)
                    
        else:
            # Use supplied value (in the current coordinate system)
            base_position = self.cur_to_base(origin)
            self.origin = base_position
            
            
    def set_current_position(self, new_position):
        '''Redefines the position value of the current position.'''
        current_position = self.get_position(verbosity=0)
        self.origin = self.get_origin() + (current_position - new_position)*self.scaling


    def search(self, step_size=1.0, min_step=0.05, intensity=None, target=0.5, detector=None, detector_suffix=None, polarity=+1, verbosity=3):
        '''Moves this axis, searching for a target value.
        
        Parameters
        ----------
        step_size : float
            The initial step size when moving the axis
        min_step : float
            The final (minimum) step size to try
        intensity : float
            The expected full-beam intensity readout
        target : 0.0 to 1.0
            The target ratio of full-beam intensity; 0.5 searches for half-max.
            The target can also be 'max' to find a local maximum.
        detector, detector_suffix
            The beamline detector (and suffix, such as '_stats4_total') to trigger to measure intensity
        polarity : +1 or -1
            Positive motion assumes, e.g. a step-height 'up' (as the axis goes more positive)
        '''
        
        if not get_beamline().beam.is_on():
            self.print('WARNING: Experimental shutter is not open.')
        
        
        if intensity is None:
            intensity = RE.md['beam_intensity_expected']

        
        if detector is None:
            #detector = gs.DETS[0]
            detector = get_beamline().detector[0]
        if detector_suffix is None:
            #value_name = gs.TABLE_COLS[0]
            value_name = get_beamline().TABLE_COLS[0]
        else:
            value_name = detector.name + detector_suffix

        bec.disable_table()
        
        
        # Check current value
        RE(count([detector]))
        value = detector.read()[value_name]['value']


        if target=='max':
            
            if verbosity>=5:
                self.print("Performing search on axis '{}' target is 'max'".format(self.name))
            
            max_value = value
            max_position = self.get_position(verbosity=0)
            
            
            direction = +1*polarity
            
            while step_size>=min_step:
                if verbosity>=4:
                    self.print("        move {} by {} × {}".format(self.name, direction, step_size))
                self.move_relative(move_amount=direction*step_size, verbosity=verbosity-2)

                prev_value = value
                RE(count([detector]))
                
                value = detector.read()[value_name]['value']
                if verbosity>=3:
                    self.print("      {} = {:.3f} {}; value : {}".format(self.name, self.get_position(verbosity=0), self.units, value))
                    
                if value>max_value:
                    max_value = value
                    max_position = self.get_position(verbosity=0)
                    
                if value>prev_value:
                    # Keep going in this direction...
                    pass
                else:
                    # Switch directions!
                    direction *= -1
                    step_size *= 0.5
                
                
        elif target=='min':
            
            if verbosity>=5:
                self.print("Performing search on axis '{}' target is 'min'".format(self.name))
            
            direction = +1*polarity
            
            while step_size>=min_step:
                if verbosity>=4:
                    self.print("        move {} by {} × {}".format(self.name, direction, step_size))
                self.move_relative(move_amount=direction*step_size, verbosity=verbosity-2)

                prev_value = value
                RE(count([detector]))
                value = detector.read()[value_name]['value']
                if verbosity>=3:
                    self.print("      {} = {:.3f} {}; value : {}".format(self.name, self.get_position(verbosity=0), self.units, value))
                    
                if value<prev_value:
                    # Keep going in this direction...
                    pass
                else:
                    # Switch directions!
                    direction *= -1
                    step_size *= 0.5
                                
                
        
        else:

            target_rel = target
            target = target_rel*intensity

            if verbosity>=5:
                self.print("Performing search on axis '{}' target {} × {} = {}".format(self.name, target_rel, intensity, target))
            if verbosity>=4:
                self.print("      value : {} ({:.1f}%)".format(value, 100.0*value/intensity))
            
            
            # Determine initial motion direction
            if value>target:
                direction = -1*polarity
            else:
                direction = +1*polarity
                
            while step_size>=min_step:
                
                if verbosity>=4:
                    self.print("        move {} by {} × {}".format(self.name, direction, step_size))
                self.move_relative(move_amount=direction*step_size, verbosity=verbosity-2)
                
                RE(count([detector]))
                value = detector.read()[value_name]['value']
                if verbosity>=3:
                    self.print("      {} = {:.3f} {}; value : {} ({:.1f}%)".format(self.name, self.get_position(verbosity=0), self.units, value, 100.0*value/intensity))
                    
                # Determine direction
                if value>target:
                    new_direction = -1.0*polarity
                else:
                    new_direction = +1.0*polarity
                    
                if abs(direction-new_direction)<1e-4:
                    # Same direction as we've been going...
                    # ...keep moving this way
                    pass
                else:
                    # Switch directions!
                    direction *= -1
                    step_size *= 0.5
    
        bec.enable_table()
            
        
    def scan(self):
        self.print('todo')
        
    def center(self):
        self.print('todo')
        
    def mark(self, label, position=None, verbosity=3):
        '''Set a mark for this axis. (By default, the current position is
        used.)'''
        
        if position is None:
            position = self.get_position(verbosity=0)
            
        axes_positions = { self.name : position }
        self.stage.mark(label, **axes_positions)
            
        
    


    # Book-keeping
    ########################################
    
    def enable(self):
        self.enabled = True
        
        
    def disable(self):
        self.enabled = False
        
        
    def is_enabled(self):
        
        return self.enabled and self.stage.is_enabled()
    
        
    def get_origin(self):
        
        return self.origin
        
        
    def get_units(self):
        
        if self.units is not None:
            return self.units
        
        else:
            return getattr(self.base_stage, self.name+'units')()


    def get_hint(self, verbosity=3):
        '''Return (and print) the "motion hint" associated with this axis. This
        hint gives information about the expected directionality of the motion.'''
        
        if self.hint is not None:
            s = '{}\n{}'.format(self.hint, self.stage._hint_replacements(self.hint))
            if verbosity>=2:
                self.print(s)
            return s
        
        else:
            return getattr(self.base_stage, self.name+'hint')(verbosity=verbosity)
        
        
    def get_info(self, verbosity=3):
        '''Returns information about this axis.'''
        
        self.get_position(verbosity=verbosity)
        self.get_hint(verbosity=verbosity)

        
    def check_base(self):
        if self.base_stage is None:
            self.print("Error: %s %s has 'base_stage' set to 'None'." % (self.__class__.__name__, self.name))
        
        
        



class Sample_Generic(CoordinateSystem):
    """
    The Sample() classes are used to define a single, individual sample. Each
    sample is created with a particular name, which is recorded during measurements.
    Logging of comments also includes the sample name. Different Sample() classes
    can define different defaults for alignment, measurement, etc.
    """


    # Core methods
    ########################################
    def __init__(self, name, base=None, **md):
        '''Create a new Sample object.
        
        Parameters
        ----------
        name : str
            Name for this sample.
        base : Stage
            The stage/holder on which this sample sits.
        '''               
        
        if base is None:
            base = get_default_stage()
            #print("Note: No base/stage/holder specified for sample '{:s}'. Assuming '{:s}' (class {:s})".format(name, base.name, base.__class__.__name__))
            
        
        super().__init__(name=name, base=base)
        # TODO: Pass common= to CoordinateSystem
        
        self.name = name
        
        
        self.md = {
            'exposure_time' : 1.0 ,
            'measurement_ID' : 1 ,
            }
        self.md.update(md)
        
        self.naming_scheme = ['name', 'extra', 'exposure_time','id']
        self.naming_delimeter = '_'
        

        # TODO
        #if base is not None:
            #base.addSample(self)
        
        
        self.reset_clock()
        
        
    def _set_axes_definitions(self):
        '''Internal function which defines the axes for this stage. This is kept
        as a separate function so that it can be over-ridden easily.'''
        
        # The _axes_definitions array holds a list of dicts, each defining an axis
        self._axes_definitions = [ {'name': 'x',
                            'motor': None,
                            'enabled': True,
                            'scaling': +1.0,
                            'units': None,
                            'hint': None,
                            },
                            {'name': 'y',
                            'motor': None,
                            'enabled': True,
                            'scaling': +1.0,
                            'units': 'mm',
                            'hint': None,
                            },
                            #{'name': 'z',
                            #'motor': None,
                            #'enabled': False,
                            #'scaling': +1.0,
                            #'units': 'mm',
                            #'hint': None,
                            #},
                            {'name': 'th',
                            'motor': None,
                            'enabled': True,
                            'scaling': +1.0,
                            'units': 'deg',
                            'hint': None,
                            },
                            #{'name': 'chi',
                            #'motor': None,
                            #'enabled': True,
                            #'scaling': +1.0,
                            #'units': 'deg',
                            #'hint': None,
                            #},
                            #{'name': 'phi',
                            #'motor': srot,
                            #'enabled': True,
                            #'scaling': +1.0,
                            #'units': 'deg',
                            #'hint': None,
                            #},
                            #{'name': 'yy',
                            #'motor': None,
                            #'enabled': True,
                            #'scaling': +1.0,
                            #'units': 'mm',
                            #'hint': None,
                            #},
                            ]          
        

        
    # Metadata methods
    ########################################
    # These involve setting or getting values associated with this sample.
        
    def clock(self):
        '''Return the current value of the "clock" variable. This provides a
        way to set a clock/timer for a sample. For instance, you can call
        "reset_clock" when you initiate some change to the sample. Thereafter,
        the "clock" method lets you check how long it has been since that
        event.'''
        
        clock_delta = time.time() - self.clock_zero
        return clock_delta
        

    def reset_clock(self):
        '''Resets the sample's internal clock/timer to zero.'''
        
        self.clock_zero = time.time()
        
        return self.clock()        
        
        
        
    def get_attribute(self, attribute):
        '''Return the value of the requested md.'''
        
        if attribute in self._axes:
            return self._axes[attribute].get_position(verbosity=0)
        
        if attribute=='name':
            return self.name

        if attribute=='clock':
            return self.clock()

        if attribute=='temperature':
            return self.temperature(verbosity=0)
        if attribute=='temperature_A':
            return self.temperature(temperature_probe='A', verbosity=0)
        if attribute=='temperature_B':
            return self.temperature(temperature_probe='B',verbosity=0)
        if attribute=='temperature_C':
            return self.temperature(temperature_probe='C',verbosity=0)
        if attribute=='temperature_D':
            return self.temperature(temperature_probe='D',verbosity=0)


        if attribute in self.md:
            return self.md[attribute]


        replacements = { 
            'id' : 'measurement_ID' ,
            'ID' : 'measurement_ID' ,
            'extra' : 'savename_extra' ,
            }
        
        if attribute in replacements:
            return self.md[replacements[attribute]]
        
        return None
            

    def set_attribute(self, attribute, value):
        '''Arbitrary attributes can be set and retrieved. You can use this to 
        store additional meta-data about the sample.
        
        WARNING: Currently this meta-data is not saved anywhere. You can opt
        to store the information in the sample filename (using "naming").
        '''
        
        self.md[attribute] = value
        
        
    def set_md(self, **md):
        
        self.md.update(md)
        
        
        
    def get_md(self, prefix='sample_', include_marks=True, **md):
        '''Returns a dictionary of the current metadata.
        The 'prefix' argument is prepended to all the md keys, which allows the
        metadata to be grouped with other metadata in a clear way. (Especially,
        to make it explicit that this metadata came from the sample.)'''
        
        # Update internal md
        #self.md['key'] = value

        
        md_return = self.md.copy()
        md_return['name'] = self.name
    
    
        if include_marks:
            for label, positions in self._marks.items():
                md_return['mark_'+label] = positions
    
    
        # Add md that varies over time
        md_return['clock'] = self.clock()
        md_return['temperature'] = self.temperature(temperature_probe='A', verbosity=0)
        md_return['temperature_A'] = self.temperature(temperature_probe='A', verbosity=0)
        md_return['temperature_B'] = self.temperature(temperature_probe='B', verbosity=0)
        md_return['temperature_C'] = self.temperature(temperature_probe='C', verbosity=0)
        md_return['temperature_D'] = self.temperature(temperature_probe='D', verbosity=0)
    
        for axis_name, axis in self._axes.items():
            md_return[axis_name] = axis.get_position(verbosity=0)
            md_return['motor_'+axis_name] = axis.get_motor_position(verbosity=0)
        
        
        md_return['savename'] = self.get_savename() # This should be over-ridden by 'measure'
    

        # Include the user-specified metadata
        md_return.update(md)

    
        # Add an optional prefix
        if prefix is not None:
            md_return = { '{:s}{:s}'.format(prefix, key) : value for key, value in md_return.items() }
    
        return md_return
    
    
    
    
        
        
    # Naming scheme methods
    ########################################
    # These allow the user to control how data is named.
        
    def naming(self, scheme=['name', 'extra', 'exposure_time','id'], delimeter='_'):
        '''This method allows one to define the naming convention that will be
        used when storing data for this sample. The "scheme" variable is an array
        that lists the various elements one wants to store in the filename.
        
        Each entry in "scheme" is a string referring to a particular element/
        value. For instance, motor names can be stored ("x", "y", etc.), the
        measurement time can be stored, etc.'''
        
        self.naming_scheme = scheme
        self.naming_delimeter = delimeter


    def get_naming_string(self, attribute):
        
        # Handle special cases of formatting the text
        
        if attribute in self._axes:
            return '{:s}{:.3f}'.format(attribute, self._axes[attribute].get_position(verbosity=0))
        
        if attribute=='clock':
            return '{:.1f}s'.format(self.get_attribute(attribute))

        if attribute=='exposure_time':
            return '{:.2f}s'.format(self.get_attribute(attribute))

        if attribute=='temperature':
            return 'T{:.3f}C'.format(self.get_attribute(attribute))
        if attribute=='temperature_A':
            return 'T{:.3f}C'.format(self.get_attribute(attribute))
        if attribute=='temperature_B':
            return 'T{:.3f}C'.format(self.get_attribute(attribute))
        if attribute=='temperature_C':
            return 'T{:.3f}C'.format(self.get_attribute(attribute))
        if attribute=='temperature_D':
            return 'T{:.3f}C'.format(self.get_attribute(attribute))
        if attribute=='trigger_time':
            return '{:.1f}s'.format(self.get_attribute(attribute))


        if attribute=='extra':
            # Note: Don't eliminate this check; it will not be properly handled
            # by the generic call below. When 'extra' is None, we should
            # return None, so that it gets skipped entirely.
            return self.get_attribute('savename_extra')

        if attribute=='spot_number':
            return 'spot{:d}'.format(self.get_attribute(attribute))
        
        
        # Generically: lookup the attribute and convert to string
        
        att = self.get_attribute(attribute)
        if att is None:
            # If the attribute is not found, simply return the text.
            # This allows the user to insert arbitrary text info into the
            # naming scheme.
            return attribute
        
        else:
            return str(att)
        

    def get_savename(self, savename_extra=None):
        '''Return the filename that will be used to store data for the upcoming
        measurement. The method "naming" lets one control what gets stored in
        the filename.'''
        
        if savename_extra is not None:
            self.set_attribute('savename_extra', savename_extra)
        
        attribute_strings = []
        for attribute in self.naming_scheme:
            s = self.get_naming_string(attribute)
            if s is not None:
                attribute_strings.append(s)

        self.set_attribute('savename_extra', None)
        
        savename = self.naming_delimeter.join(attribute_strings)
        
        # Avoid 'dangerous' characters
        savename = savename.replace(' ', '_')
        #savename = savename.replace('.', 'p')
        savename = savename.replace('/', '-slash-')
        
        return savename
    
        
        



class Stage(CoordinateSystem):
    
    pass


