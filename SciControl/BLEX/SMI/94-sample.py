#!/usr/bin/python
# -*- coding: utf-8 -*-
# vi: ts=4 sw=4




################################################################################
#  Code for defining a 'Sample' object, which keeps track of its state, and 
# simplifies the task of aligning, measuring, etc.
################################################################################
# Known Bugs:
#  N/A
################################################################################
# TODO:
#  - Search for "TODO" below.
#  - Ability to have a collection of simultaneous motions? (E.g. build up a set
#  of deferred motions?)
#  - Use internal naming scheme to control whether 'saxs'/'waxs' is put in the
# filename
################################################################################


import time
import re
import os
import shutil

class CoordinateSystem(object):
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
        
        self.name = name
        self.base_stage = base
        
        
        self.enabled = True
        
        self.md = {}
        self._marks = {}

        self._set_axes_definitions()
        self._init_axes(self._axes_definitions)
        
        
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
            
            axis_object = Axis(axis['name'], axis['motor'], axis['enabled'], axis['scaling'], axis['units'], axis['hint'], self.base_stage, stage=self)
            self._axes[axis['name']] = axis_object
               
            # Bind the methods of axis_object to appropriately-named methods of 
            # the CoordinateSystem() class.
            setattr(self, axis['name'], axis_object.get_position )
            setattr(self, axis['name']+'abs', axis_object.move_absolute )
            setattr(self, axis['name']+'r', axis_object.move_relative )
            setattr(self, axis['name']+'pos', axis_object.get_position )
            setattr(self, axis['name']+'posMotor', axis_object.get_motor_position )
            
            
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
        if verbosity>=1:
            print('Temperature functions not implemented in {}'.format(self.__class__.__name__))
        
        
    def temperature(self, verbosity=3):
        if verbosity>=1:
            print('Temperature functions not implemented in {}'.format(self.__class__.__name__))
            
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
                  
    def origin(self, verbosity=3):
        '''Returns the origin for axes.'''
        
        out = {}
        for axis_name, axis_object in sorted(self._axes.items()):
            origin = axis_object.get_origin()
            if verbosity>=2: print('{:s} origin = {:.3f} {:s}'.format(axis_name, origin, axis_object.get_units()))
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
        
        
    def setOrigin(self, axes, positions=None):
        '''Define the current position as the zero-point (origin) for this stage/
        sample. The axes to be considered in this redefinition must be supplied
        as a list.
        
        If the optional positions parameter is passed, then those positions are
        used to define the origins for the axes.'''

        if positions is None:
        
            for axis in axes:
                getattr(self, axis+'setOrigin')()
                
        else:
            for axis, pos in zip(axes, positions):
                getattr(self, axis+'setOrigin')(pos)
    
    
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
        
        if verbosity>=3:
            print('Marks for {:s} (class {:s}):'.format(self.name, self.__class__.__name__))
        
        if verbosity>=2:
            for label, positions in self._marks.items():
                print(label)
                for axis_name, position in sorted(positions.items()):
                    print('  {:s} = {:.4f} {:s}'.format(axis_name, position, self._axes[axis_name].get_units()))
            
        return self._marks
    
    
    def goto(self, label, verbosity=3, **additional):
        '''Move the stage/sample to the location given by the label. For this
        to work, the specified label must have been 'marked' at some point.
        
        Additional keyword arguments can be provided. For instance, to move 
        3 mm from the left edge:
          sam.goto('left edge', xr=+3.0)
        '''
        
        if label not in self._marks:
            if verbosity>=1:
                print("Label '{:s}' not recognized. Use '.marks()' for the list of marked positions.".format(label))
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
                print("Keyword argument '{}' not understood (should be 'r' or 'abs').".format(command))


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




class Axis(object):
    '''Generic motor axis.
    
    Meant to be used within a CoordinateSystem() or Stage() object.
    '''
    
    def __init__(self, name, motor, enabled, scaling, units, hint, base, stage=None, origin=0.0):
        
        self.name = name
        self.motor = motor
        self.enabled = enabled
        self.scaling = scaling
        self.units = units
        self.hint = hint
        
        self.base_stage = base
        self.stage = stage
        
        self.origin = 0.0
        
        
        
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
            base_position = self.motor.position
            
        else:
            verbosity_c = verbosity if verbosity>=4 else 0
            base_position = getattr(self.base_stage, self.name+'pos')(verbosity=verbosity_c)
            
        position = self.base_to_cur(base_position)
        
        
        if verbosity>=2:
            if self.stage:
                stg = self.stage.name
            else:
                stg = '?'

            if verbosity>=5 and self.motor is not None:
                print( '{:s} = {:.3f} {:s}'.format(self.motor.name, base_position, self.get_units()) )
            
            print( '{:s}.{:s} = {:.3f} {:s} (origin = {:.3f})'.format(stg, self.name, position, self.get_units(), self.get_origin()) )
            
            
        return position
    
    
    def get_motor_position(self, verbosity=3):
        '''Returns the position of this axis, traced back to the underlying
        motor.'''
        
        if self.motor is not None:
            return self.motor.position
        
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
                #mov( self.motor, base_position )
                self.motor.user_setpoint.value = base_position
                
            else:
                # Call self.base_stage.xabs(base_position)
                getattr(self.base_stage, self.name+'abs')(base_position, verbosity=0)


            if self.stage:
                stg = self.stage.name
            else:
                stg = '?'

            if verbosity>=2:
                
                # Show a realtime output of position
                start_time = time.time()
                current_position = self.get_position(verbosity=0)
                while abs(current_position-position)>self._move_settle_tolerance and (time.time()-start_time)<self._move_settle_max_time:
                    current_position = self.get_position(verbosity=0)
                    print( '{:s}.{:s} = {:5.3f} {:s}      \r'.format(stg, self.name, current_position, self.get_units()), end='')
                    time.sleep(self._move_settle_period)
                    
                    
            #if verbosity>=1:
                #current_position = self.get_position(verbosity=0)
                #print( '{:s}.{:s} = {:5.3f} {:s}        '.format(stg, self.name, current_position, self.get_units()))

                
        elif verbosity>=1:
            print( 'Axis %s disabled (stage %s).' % (self.name, self.stage.name) )
        
        
        
    def move_relative(self, move_amount=None, verbosity=3):
        '''Move axis relative to the current position.'''
        
        if move_amount is None:
            # If called without any argument, just print the current position
            return self.get_position(verbosity=verbosity)
        
        target_position = self.get_position(verbosity=0) + move_amount
        
        return self.move_absolute(target_position, verbosity=verbosity)
        
    
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
                self.origin = self.motor.position
                
            else:
                if self.base_stage is None:
                    print("Error: %s %s has 'base_stage' and 'motor' set to 'None'." % (self.__class__.__name__, self.name))
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
        
        #if not get_beamline().beam.is_on():
            #print('WARNING: Experimental shutter is not open.')
        
        
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
        
        # WARNING: Kludge hard-coding the detector for now
        value = pil1mroi4.read()['pil1mroi4']['value']


        if target is 'max':
            
            if verbosity>=5:
                print("Performing search on axis '{}' target is 'max'".format(self.name))
            
            max_value = value
            max_position = self.get_position(verbosity=0)
            
            
            direction = +1*polarity
            
            while step_size>=min_step:
                if verbosity>=4:
                    print("        move {} by {} × {}".format(self.name, direction, step_size))
                self.move_relative(move_amount=direction*step_size, verbosity=verbosity-2)

                prev_value = value
                
                # Check current value
                RE(count([detector]))
                # WARNING: Kludge hard-coding the detector for now
                value = pil1mroi4.read()['pil1mroi4']['value']
                
                if verbosity>=3:
                    print("      {} = {:.3f} {}; value : {}".format(self.name, self.get_position(verbosity=0), self.units, value))
                    
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
                
                
        elif target is 'min':
            
            if verbosity>=5:
                print("Performing search on axis '{}' target is 'min'".format(self.name))
            
            direction = +1*polarity
            
            while step_size>=min_step:
                if verbosity>=4:
                    print("        move {} by {} × {}".format(self.name, direction, step_size))
                self.move_relative(move_amount=direction*step_size, verbosity=verbosity-2)

                prev_value = value
                RE(count([detector]))
                value = detector.read()[value_name]['value']
                if verbosity>=3:
                    print("      {} = {:.3f} {}; value : {}".format(self.name, self.get_position(verbosity=0), self.units, value))
                    
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
                print("Performing search on axis '{}' target {} × {} = {}".format(self.name, target_rel, intensity, target))
            if verbosity>=4:
                print("      value : {} ({:.1f}%)".format(value, 100.0*value/intensity))
            
            
            # Determine initial motion direction
            if value>target:
                direction = -1*polarity
            else:
                direction = +1*polarity
                
            while step_size>=min_step:
                
                if verbosity>=4:
                    print("        move {} by {} × {}".format(self.name, direction, step_size))
                self.move_relative(move_amount=direction*step_size, verbosity=verbosity-2)
                
                # Check current value
                RE(count([detector]))
                # WARNING: Kludge hard-coding the detector for now
                value = pil1mroi4.read()['pil1mroi4']['value']
                
                
                if verbosity>=3:
                    print("      {} = {:.3f} {}; value : {} ({:.1f}%)".format(self.name, self.get_position(verbosity=0), self.units, value, 100.0*value/intensity))
                    
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
        print('todo')
        
    def center(self):
        print('todo')
        
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
            s = '%s\n%s' % (self.hint, self.stage._hint_replacements(self.hint))
            if verbosity>=2:
                print(s)
            return s
        
        else:
            return getattr(self.base_stage, self.name+'hint')(verbosity=verbosity)
        
        
    def get_info(self, verbosity=3):
        '''Returns information about this axis.'''
        
        self.get_position(verbosity=verbosity)
        self.get_hint(verbosity=verbosity)

        
    def check_base(self):
        if self.base_stage is None:
            print("Error: %s %s has 'base_stage' set to 'None'." % (self.__class__.__name__, self.name))
        
        
        



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
        #md_return['temperature'] = self.temperature(temperature_probe='A', verbosity=0)
        #md_return['temperature_A'] = self.temperature(temperature_probe='A', verbosity=0)
        #md_return['temperature_B'] = self.temperature(temperature_probe='B', verbosity=0)
        #md_return['temperature_C'] = self.temperature(temperature_probe='C', verbosity=0)
        #md_return['temperature_D'] = self.temperature(temperature_probe='D', verbosity=0)
    
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
    
        
        
    # Logging methods
    ########################################
    
    def comment(self, text, logbooks=None, tags=None, append_md=True, **md):
        '''Add a comment related to this sample.'''
        
        text += '\n\n[comment for sample: {} ({})].'.format(self.name, self.__class__.__name__)
        
        if append_md:
        
            md_current = { k : v for k, v in RE.md.items() } # Global md
            md_current.update(get_beamline().get_md()) # Beamline md

            # Sample md
            md_current.update(self.get_md())
            
            # Specified md
            md_current.update(md)
            
            text += '\n\n\nMetadata\n----------------------------------------'
            for key, value in sorted(md_current.items()):
                text += '\n{}: {}'.format(key, value)
            
        
        logbook.log(text, logbooks=logbooks, tags=tags)
        
        
    def log(self, text, logbooks=None, tags=None, append_md=True, **md):
        
        if append_md:
        
            text += '\n\n\nMetadata\n----------------------------------------'
            for key, value in sorted(md.items()):
                text += '\n{}: {}'.format(key, value)
        
        logbook.log(text, logbooks=logbooks, tags=tags)        


    # Control methods
    ########################################
    def setTemperature(self, temperature, verbosity=3):
        return self.base_stage.setTemperature(temperature, verbosity=verbosity)
        
        
    def temperature(self, verbosity=3):
        return self.base_stage.temperature(verbosity=verbosity)
    

    
    # Measurement methods
    ########################################
    
    def get_measurement_md(self, prefix=None, **md):
        
        #md_current = {}
        md_current = { k : v for k, v in RE.md.items() } # Global md

        #md_current['detector_sequence_ID'] = caget('XF:11BMB-ES{Det:SAXS}:cam1:FileNumber_RBV')
        #md_current['detector_sequence_ID'] = caget('XF:11BMB-ES{}:cam1:FileNumber_RBV'.format(pilatus_Epicsname))
        if get_beamline().detector[0].name is 'pilatus300':
            md_current['detector_sequence_ID'] = caget('XF:11BMB-ES{Det:SAXS}:cam1:FileNumber_RBV')
        elif get_beamline().detector[0].name is 'pilatus2M':
            md_current['detector_sequence_ID'] = caget('XF:11BMB-ES{Det:PIL2M}:cam1:FileNumber_RBV')
          
        md_current.update(get_beamline().get_md())
        
        md_current.update(md)

        # Add an optional prefix
        if prefix is not None:
            md_return = { '{:s}{:s}'.format(prefix, key) : value for key, value in md_return.items() }
        
        return md_current

    

    def expose(self, exposure_time=None, extra=None, verbosity=3, poling_period=0.1, **md):
        '''Internal function that is called to actually trigger a measurement.'''
        '''TODO: **md doesnot work in RE(count). '''
        
        
        if 'measure_type' not in md:
            md['measure_type'] = 'expose'
        #self.log('{} for {}.'.format(md['measure_type'], self.name), **md)


        # Set exposure time
        if exposure_time is not None:
            exposure_time = abs(exposure_time)
            for detector in get_beamline().detector:
                if exposure_time != detector.cam.acquire_time.get():
                    detector.cam.acquire_time.set(exposure_time)
                    detector.cam.acquire_period.set(exposure_time)
       


        # Do acquisition
        
        md['plan_header_override'] = md['measure_type']
        start_time = time.time()
        
        md_current = self.get_md()
        md.update(md_current)
        
        
        # Set up file saving paths
        savename = self.get_savename(savename_extra=extra)
        for detector in get_beamline().detector:
            if detector.name is 'pil1M':
                subdir='saxs'
            elif detector.name is 'rayonix':
                subdir='maxs'
            elif detector.name is 'pil300KW':
                subdir='waxs'
            
            detector.cam.file_path.set( '{}{}/'.format(RE.md['experiment_alias_directory'], subdir) )
            time.sleep(.1)
            detector.cam.file_number.set( RE.md['scan_id'] )
            time.sleep(.1)
            detector.cam.file_name.set( savename )
            time.sleep(.1)


        uids = RE(count(get_beamline().detector), **md)
        #yield from (count(get_beamline().detector), **md)
        


        # Wait for detectors to be ready
        max_exposure_time = 0.1
        for detector in get_beamline().detector: 
            max_exposure_time = max(max_exposure_time, detector.cam.acquire_time.get())
            
        if verbosity>=2:
            status = 0
            while (status==0) and (time.time()-start_time)<(max_exposure_time+5):
                percentage = 100*(time.time()-start_time)/max_exposure_time
                print( 'Exposing {:6.2f} s  ({:3.0f}%)      \r'.format((time.time()-start_time), percentage), end='')
                time.sleep(poling_period)
                
                status = 1
                for detector in get_beamline().detector:
                    if detector.name is 'pil1M':
                        if caget('XF:12IDC-ES:2{Det:1M}cam1:DetectorState_RBV')==1:
                            status *= 0
                    elif detector.name is 'rayonix':
                        if caget('XF:12IDC-ES:2{Det:MAXS}cam1:DetectorState_RBV')==1:
                            status *= 0
                    elif detector.name is 'pil300KW':
                        if caget('XF:12IDC-ES:2{Det:300KW}cam1:DetectorState_RBV')==1:
                            status *= 0
            print('')
                    
                
        else:
            time.sleep(max_exposure_time)
        
        #get_beamline().beam.off()
        
        #for detector in get_beamline().detector:
            #self.handle_file(detector, extra=extra, verbosity=verbosity, **md)
            #self.handle_file(detector, extra=extra, verbosity=verbosity)



    def handle_file(self, detector, extra=None, verbosity=3, subdirs=True, **md):
    
        subdir = ''
        
        if detector.name is 'pilatus300':
            chars = caget('XF:11BMB-ES{Det:SAXS}:TIFF1:FullFileName_RBV')
            filename = ''.join(chr(char) for char in chars)[:-1]
            
            # Alternate method to get the last filename
            #filename = '{:s}/{:s}.tiff'.format( detector.tiff.file_path.get(), detector.tiff.file_name.get()  )

            if verbosity>=3:
                print('  Data saved to: {}'.format(filename))

            if subdirs:
                subdir = '/maxs/'

            #if md['measure_type'] is not 'snap':
            if True:
                
                self.set_attribute('exposure_time', caget('XF:11BMB-ES{Det:SAXS}:cam1:AcquireTime'))
                
                # Create symlink
                #link_name = '{}/{}{}'.format(RE.md['experiment_alias_directory'], subdir, md['filename'])
                #savename = md['filename'][:-5]
                
                savename = self.get_savename(savename_extra=extra)
                link_name = '{}/{}{}_{:04d}_maxs.tiff'.format(RE.md['experiment_alias_directory'], subdir, savename, RE.md['scan_id']-1)
                
                if os.path.isfile(link_name):
                    i = 1
                    while os.path.isfile('{}.{:d}'.format(link_name,i)):
                        i += 1
                    os.rename(link_name, '{}.{:d}'.format(link_name,i))
                os.symlink(filename, link_name)
                
                if verbosity>=3:
                    print('  Data linked as: {}'.format(link_name))

        elif detector.name is 'pilatus2M':
            chars = caget('XF:11BMB-ES{Det:PIL2M}:TIFF1:FullFileName_RBV')
            filename = ''.join(chr(char) for char in chars)[:-1]
            
            # Alternate method to get the last filename
            #filename = '{:s}/{:s}.tiff'.format( detector.tiff.file_path.get(), detector.tiff.file_name.get()  )

            if verbosity>=3:
                print('  Data saved to: {}'.format(filename))

            if subdirs:
                subdir = '/saxs/'

            #if md['measure_type'] is not 'snap':
            if True:
                
                self.set_attribute('exposure_time', caget('XF:11BMB-ES{Det:PIL2M}:cam1:AcquireTime'))
                
                # Create symlink
                #link_name = '{}/{}{}'.format(RE.md['experiment_alias_directory'], subdir, md['filename'])
                #savename = md['filename'][:-5]
                
                savename = self.get_savename(savename_extra=extra)
                #link_name = '{}/{}{}_{:04d}_saxs.tiff'.format(RE.md['experiment_alias_directory'], subdir, savename, RE.md['scan_id'])
                link_name = '{}/{}{}_{:04d}_saxs.tiff'.format(RE.md['experiment_alias_directory'], subdir, savename, RE.md['scan_id']-1)
                
                if os.path.isfile(link_name):
                    i = 1
                    while os.path.isfile('{}.{:d}'.format(link_name,i)):
                        i += 1
                    os.rename(link_name, '{}.{:d}'.format(link_name,i))
                os.symlink(filename, link_name)
                
                if verbosity>=3:
                    print('  Data linked as: {}'.format(link_name))
                        
        elif detector.name is 'PhotonicSciences_CMS':
            
            self.set_attribute('exposure_time', detector.exposure_time)
            
            filename = '{:s}/{:s}.tif'.format( detector.file_path, detector.file_name )

            if subdirs:
                subdir = '/waxs/'

            #savename = md['filename'][:-5]
            savename = self.get_savename(savename_extra=extra)
            savename = '{}/{}{}_{:04d}_waxs.tiff'.format(RE.md['experiment_alias_directory'], subdir, savename, RE.md['scan_id']-1)
            
            shutil.copy(filename, savename)
            if verbosity>=3:
                print('  Data saved to: {}'.format(savename))

        
        else:
            if verbosity>=1:
                print("WARNING: Can't do file handling for detector '{}'.".format(detector.name))
                return
                    
    def snap(self, exposure_time=None, extra=None, measure_type='snap', verbosity=3, **md):
        '''Take a quick exposure (without saving data).'''
        
        self.measure(exposure_time=exposure_time, extra=extra, measure_type=measure_type, verbosity=verbosity, **md)
        
        
    def measure(self, exposure_time=None, extra=None, measure_type='measure', verbosity=3, tiling=False, stitchback=False, **md):
        '''Measure data by triggering the area detectors.
        
        Parameters
        ----------
        exposure_time : float
            How long to collect data
        extra : string, optional
            Extra information about this particular measurement (which is typically
            included in the savename/filename).
        tiling : string
            Controls the detector tiling mode.
              None : regular measurement (single detector position)
              'ygaps' : try to cover the vertical gaps in the Pilatus detector
        '''           
        
        self.measure_single(exposure_time=exposure_time, extra=extra, measure_type=measure_type, verbosity=verbosity, **md)
        

    def measure_single(self, exposure_time=None, extra=None, measure_type='measure', verbosity=3, **md):
        '''Measure data by triggering the area detectors.
        
        Parameters
        ----------
        exposure_time : float
            How long to collect data
        extra : string, optional
            Extra information about this particular measurement (which is typically
            included in the savename/filename).
        '''           
        
        if exposure_time is not None:
            self.set_attribute('exposure_time', exposure_time)
        #else:
            #exposure_time = self.get_attribute('exposure_time')
            
        savename = self.get_savename(savename_extra=extra)
        
        #caput('XF:11BMB-ES{Det:SAXS}:cam1:FileName', savename)
        
        if verbosity>=2 and (get_beamline().current_mode != 'measurement'):
            print("WARNING: Beamline is not in measurement mode (mode is '{}')".format(get_beamline().current_mode))

        if verbosity>=1 and len(get_beamline().detector)<1:
            print("ERROR: No detectors defined in cms.detector")
            return
        
        md_current = self.get_md()
        md_current.update(self.get_measurement_md())
        md_current['sample_savename'] = savename
        md_current['measure_type'] = measure_type
        #md_current['filename'] = '{:s}_{:04d}.tiff'.format(savename, md_current['detector_sequence_ID'])
        md_current['filename'] = '{:s}_{:04d}.tiff'.format(savename, RE.md['scan_id'])
        md_current.update(md)

       
        self.expose(exposure_time, extra=extra, verbosity=verbosity, **md_current)
        #self.expose(exposure_time, extra=extra, verbosity=verbosity, **md)
        
        self.md['measurement_ID'] += 1
        

        
    def measureSpots(self, num_spots=4, translation_amount=0.2, axis='y', exposure_time=None, extra=None, measure_type='measureSpots', tiling=False, **md):
        '''Measure multiple spots on the sample.'''
        
        if 'spot_number' not in self.md:
            self.md['spot_number'] = 1
        
        
        for spot_num in range(num_spots):
        
            self.measure(exposure_time=exposure_time, extra=extra, measure_type=measure_type, tiling=tiling, **md)
            
            getattr(self, axis+'r')(translation_amount)
            self.md['spot_number'] += 1
            print('{:d} of {:d} is done'.format(spot_num+1,num_spots))
        
        
    def measureTimeSeries(self, exposure_time=None, num_frames=10, wait_time=None, extra=None, measure_type='measureTimeSeries', verbosity=3, tiling=False, fix_name=True, **md):

        if fix_name and ('clock' not in self.naming_scheme):
            self.naming_scheme_hold = self.naming_scheme
            self.naming_scheme = self.naming_scheme_hold.copy()
            self.naming_scheme.insert(-1, 'clock')

        
        md['measure_series_num_frames'] = num_frames
        
        for i in range(num_frames):
            
            if verbosity>=3:
                print('Measuring frame {:d}/{:d} ({:.1f}% complete).'.format(i+1, num_frames, 100.0*i/num_frames))
                
            md['measure_series_current_frame'] = i+1
            self.measure(exposure_time=exposure_time, extra=extra, measure_type=measure_type, verbosity=verbosity, tiling=tiling, **md)
            if wait_time is not None:
                time.sleep(wait_time)
    
    def measureTimeSeriesAngles(self, exposure_time=None, num_frames=10, wait_time=None, extra=None, measure_type='measureTimeSeries', verbosity=3, tiling=False, fix_name=True, **md):

        if fix_name and ('clock' not in self.naming_scheme):
            self.naming_scheme_hold = self.naming_scheme
            self.naming_scheme = self.naming_scheme_hold.copy()
            self.naming_scheme.insert(-1, 'clock')

        
        md['measure_series_num_frames'] = num_frames
        
        for i in range(num_frames):
            
            if verbosity>=3:
                print('Measuring frame {:d}/{:d} ({:.1f}% complete).'.format(i+1, num_frames, 100.0*i/num_frames))
                
            md['measure_series_current_frame'] = i+1
            print('Angles in measure include: {}'.format(sam.incident_angles_default))
            self.measureIncidentAngles(exposure_time=exposure_time, extra=extra, **md)
            if wait_time is not None:
                time.sleep(wait_time)
            #if (i % 2 ==0):
            #    self.xr(-1)
            #else:
            #    self.xr(1)
            #self.pos()
        
        
    def measureTemperature(self, temperature, exposure_time=None, wait_time=None, temperature_probe='A', temperature_tolerance=0.4, extra=None, measure_type='measureTemperature', verbosity=3, tiling=False, poling_period=1.0, fix_name=True, **md):

        # Set new temperature
        self.setTemperature(temperature, temperature_probe=temperature_probe, verbosity=verbosity)
        
        # Wait until we reach the temperature
        while abs(self.temperature(temperature_probe=temperature_probe, verbosity=0) - temperature)>temperature_tolerance:
            if verbosity>=3:
                print('  setpoint = {:.3f}°C, Temperature = {:.3f}°C          \r'.format(self.temperature_setpoint(temperature_probe=temperature_probe)-273.15, self.temperature(verbosity=0)), end='')
            time.sleep(poling_period)
            
        # Allow for additional equilibration at this temperature
        if wait_time is not None:
            time.sleep(wait_time)
            
        # Measure
        #if fix_name and ('temperature' not in self.naming_scheme):
        #    self.naming_scheme_hold = self.naming_scheme
        #    self.naming_scheme = self.naming_scheme_hold.copy()
        #    self.naming_scheme.insert(-1, 'temperature')
            
            
        self.measure(exposure_time=exposure_time, extra=extra, measure_type=measure_type, verbosity=verbosity, tiling=tiling, **md)
        
        #self.naming_scheme = self.naming_scheme_hold


    def measureTemperatures(self, temperatures, exposure_time=None, wait_time=None, temperature_probe='A', temperature_tolerance=0.4, extra=None, measure_type='measureTemperature', verbosity=3, tiling=False, poling_period=1.0, fix_name=True, **md):
        
        for temperature in temperatures:
            self.measureTemperature(temperature, exposure_time=exposure_time, wait_time=wait_time, temperature_probe=temperature_probe, temperature_tolerance=temperature_tolerance, measure_type=measure_type, verbosity=verbosity, tiling=tiling, poling_period=poling_period, fix_name=fix_name, **md)
        

    def do(self, step=0, verbosity=3, **md):
        '''Performs the "default action" for this sample. This usually means 
        aligning the sample, and taking data.
        
        The 'step' argument can optionally be given to jump to a particular
        step in the sequence.'''
        
        if verbosity>=4:
            print('  doing sample {}'.format(self.name))
        
        if step<=1:
            if verbosity>=5:
                print('    step 1: goto origin')
            self.xo() # goto origin
            self.yo()
            #self.gotoAlignedPosition()
            
        #if step<=5:
            #self.align()
            
        if step<=10:
            if verbosity>=5:
                print('    step 10: measuring')
            self.measure(**md)
                

    def scan_measure(self, motor, start, stop, num_frames, exposure_time=None, detectors=None, extra=None, per_step=None, wait_time=None, measure_type='Scan_measure', verbosity=3, fill_gaps=False, **md):
        
        """
        Scans the specified motor and record the detectors with shutter open during the scan.
        
        Parameters
        ----------
        motor : motor
            The axis/stage/motor that you want to move.
        start, stop : float
            The relative positions of the scan range.
        num_frames : int
            The number of scan points. 
        exposure_time: float
            The exposure time for single point
        md : dict, optional
            metadata        
        """
        #span = abs(stop-start)
        #positions, dp = np.linspace(start, stop, num, endpoint=True, retstep=True)

        if detectors is None:
            detectors = cms.detector
   
        if exposure_time is not None:
            self.set_attribute('exposure_time', exposure_time)

        bec.disable_plots()
        bec.disable_table()
        
        savename = self.get_savename(savename_extra=extra)
        
        #caput('XF:11BMB-ES{Det:SAXS}:cam1:FileName', savename)
        
        if verbosity>=2 and (get_beamline().current_mode != 'measurement'):
            print("WARNING: Beamline is not in measurement mode (mode is '{}')".format(get_beamline().current_mode))

        if verbosity>=1 and len(cms.detector)<1:
            print("ERROR: No detectors defined in cms.detector")
            return
        
        #set exposure time
        for detector in get_beamline().detector:
            detector.setExposureTime(exposure_time, verbosity=verbosity)
        
        md_current = self.get_md()
        md_current['sample_savename'] = savename
        md_current['measure_type'] = measure_type
        md_current['scan'] = 'scan_measure'
        md_current.update(self.get_measurement_md())
        #md_current['filename'] = '{:s}_{:04d}.tiff'.format(savename, md_current['detector_sequence_ID'])
        md_current['measure_series_num_frames'] = num_frames
        md_current['filename'] = '{:s}_{:04d}.tiff'.format(savename, RE.md['scan_id'])
        md_current['measure_series_motor'] = motor.name
        md_current['measure_series_positions'] = [start, stop]
        md_current['exposure_time'] = exposure_time

        #md_current['fileno'] = '{:s}_{:04d}.tiff'.format(savename, RE.md['scan_id'])
        md_current.update(md)
        
        print(RE.md['scan_id'])
        
        # Perform the scan
        get_beamline().beam._test_on(wait_time=0.1)
        #RE(relative_scan(gs.DETS, motor, start, stop, num_frames+1, per_step=per_step, md=md_current))
        RE(relative_scan(cms.detector, motor, start, stop, num_frames+1, per_step=per_step,md=md_current), LiveTable([motor, 'motor_setpoint']))
        #RE(relative_scan(gs.DETS, motor, start, stop, num_frames+1, per_step=per_step,**md), self.cb)
     
        if verbosity>=3 and caget('XF:11BMB-ES{Det:SAXS}:cam1:Acquire')==1:
            print('Warning: Detector Pilatus300k still not done acquiring.')
        elif verbosity>=3 and caget('XF:11BMB-ES{Det:PIL2M}:cam1:Acquire')==1:
            print('Warning: Detector Pilatus2M still not done acquiring.')
  
        #print(RE.md['scan_id'])

        get_beamline().beam._test_off(wait_time=0.1)

        self.md['measurement_ID'] += 1
   
        #data collected, link uid to file name
        for detector in cms.detector:
            #print(detector.name)
            self.handle_fileseries(detector, num_frames=num_frames, extra=extra, verbosity=verbosity, **md)


    def handle_fileseries(self, detector, num_frames=None, extra=None, verbosity=3, subdirs=True, **md):
    
        subdir = ''
        
        if detector.name is 'pilatus300' :
            chars = caget('XF:11BMB-ES{Det:SAXS}:TIFF1:FullFileName_RBV')
            filename = ''.join(chr(char) for char in chars)[:-1]
            filename_part1 = ''.join(chr(char) for char in chars)[:-13]

            print('pilatus300k data handling')
            # Alternate method to get the last filename
            #filename = '{:s}/{:s}.tiff'.format( detector.tiff.file_path.get(), detector.tiff.file_name.get()  )

            #if verbosity>=3:
            #    print('  Data saved to: {}'.format(filename))

            if subdirs:
                subdir = '/maxs/'

            #if md['measure_type'] is not 'snap':
            if True:
                
                self.set_attribute('exposure_time', caget('XF:11BMB-ES{Det:SAXS}:cam1:AcquireTime'))
                
                # Create symlink
                #link_name = '{}/{}{}'.format(RE.md['experiment_alias_directory'], subdir, md['filename'])
                #savename = md['filename'][:-5]
                
                savename = self.get_savename(savename_extra=extra)
                link_name = '{}/{}{}_{:04d}_maxs.tiff'.format(RE.md['experiment_alias_directory'], subdir, savename, RE.md['scan_id']-1)
                link_name_part1 = '{}/{}{}_{:04d}'.format(RE.md['experiment_alias_directory'], subdir, savename, RE.md['scan_id']-1)
                
                if os.path.isfile(link_name):
                    i = 1
                    while os.path.isfile('{}.{:d}'.format(link_name,i)):
                        i += 1
                    os.rename(link_name, '{}.{:d}'.format(link_name,i))
                
                for num_frame in range(num_frames+1):
                    filename_new = '{}_{:06d}.tiff'.format(filename_part1, num_frame)
                    link_name_new= '{}_{:06d}_maxs.tiff'.format(link_name_part1, num_frame)
                    os.symlink(filename_new, link_name_new)                
                    if verbosity>=3:
                        print('  Data {} linked as: {}'.format(filename_new, link_name_new))

        elif detector.name is  'pilatus2M':
            chars = caget('XF:11BMB-ES{Det:PIL2M}:TIFF1:FullFileName_RBV')
            filename = ''.join(chr(char) for char in chars)[:-1]
            filename_part1 = ''.join(chr(char) for char in chars)[:-13]

            print('pilatus2M data handling')
            
            # Alternate method to get the last filename
            #filename = '{:s}/{:s}.tiff'.format( detector.tiff.file_path.get(), detector.tiff.file_name.get()  )

            #if verbosity>=3:
            #    print('  Data saved to: {}'.format(filename))

            if subdirs:
                subdir = '/saxs/'

            #if md['measure_type'] is not 'snap':
            if True:
                
                self.set_attribute('exposure_time', caget('XF:11BMB-ES{Det:PIL2M}:cam1:AcquireTime'))
                
                # Create symlink
                #link_name = '{}/{}{}'.format(RE.md['experiment_alias_directory'], subdir, md['filename'])
                #savename = md['filename'][:-5]
                
                savename = self.get_savename(savename_extra=extra)
                link_name = '{}/{}{}_{:04d}_saxs.tiff'.format(RE.md['experiment_alias_directory'], subdir, savename, RE.md['scan_id']-1)
                link_name_part1 = '{}/{}{}_{:04d}'.format(RE.md['experiment_alias_directory'], subdir, savename, RE.md['scan_id']-1)
                
                if os.path.isfile(link_name):
                    i = 1
                    while os.path.isfile('{}.{:d}'.format(link_name,i)):
                        i += 1
                    os.rename(link_name, '{}.{:d}'.format(link_name,i))
                
                for num_frame in range(num_frames+1):
                    filename_new = '{}_{:06d}.tiff'.format(filename_part1, num_frame)
                    link_name_new= '{}_{:06d}_saxs.tiff'.format(link_name_part1, num_frame)
                    os.symlink(filename_new, link_name_new)                
                    if verbosity>=3:
                        print('  Data {} linked as: {}'.format(filename_new, link_name_new))
           
        else:
            if verbosity>=1:
                print("WARNING: Can't do file handling for detector '{}'.".format(detector.name))
                return



    # Control methods
    ########################################
    def setTemperature(self, temperature, output_channel='1', verbosity=3):
        #if verbosity>=1:
            #print('Temperature functions not implemented in {}'.format(self.__class__.__name__))
        if output_channel == '1':
            if verbosity>=2:
                print('  Changing temperature setpoint from {:.3f}°C  to {:.3f}°C'.format(caget('XF:11BM-ES{Env:01-Out:1}T-SP')-273.15, temperature))
            caput('XF:11BM-ES{Env:01-Out:1}T-SP', temperature+273.15)
        
        if output_channel == '2':
            if verbosity>=2:
                print('  Changing temperature setpoint from {:.3f}°C  to {:.3f}°C'.format(caget('XF:11BM-ES{Env:01-Out:2}T-SP')-273.15, temperature))
            caput('XF:11BM-ES{Env:01-Out:2}T-SP', temperature+273.15)
        
        if output_channel == '3':
            if verbosity>=2:
                print('  Changing temperature setpoint from {:.3f}°C  to {:.3f}°C'.format(caget('XF:11BM-ES{Env:01-Out:3}T-SP')-273.15, temperature))
            caput('XF:11BM-ES{Env:01-Out:3}T-SP', temperature+273.15)

        if output_channel == '4':
            if verbosity>=2:
                print('  Changing temperature setpoint from {:.3f}°C  to {:.3f}°C'.format(caget('XF:11BM-ES{Env:01-Out:4}T-SP')-273.15, temperature))
            caput('XF:11BM-ES{Env:01-Out:4}T-SP', temperature+273.15)
            
            
    def temperature(self, temperature_probe='A', output_channel='1', verbosity=3):
        #if verbosity>=1:
            #print('Temperature functions not implemented in {}'.format(self.__class__.__name__))
 
        if temperature_probe == 'A':
            current_temperature = caget('XF:11BM-ES{Env:01-Chan:A}T:C-I')
            if verbosity>=3:
                print('  Temperature = {:.3f}°C (setpoint = {:.3f}°C)'.format( current_temperature, self.temperature_setpoint(output_channel=output_channel)-273.15 ) )
            
        if temperature_probe == 'B':
            current_temperature = caget('XF:11BM-ES{Env:01-Chan:B}T:C-I')
            if verbosity>=3:
                print('  Temperature = {:.3f}°C (setpoint = {:.3f}°C)'.format( current_temperature, self.temperature_setpoint(output_channel=output_channel)-273.15 ) )

        if temperature_probe == 'C':
            current_temperature = caget('XF:11BM-ES{Env:01-Chan:C}T:C-I')
            if verbosity>=3:
                print('  Temperature = {:.3f}°C (setpoint = {:.3f}°C)'.format( current_temperature, self.temperature_setpoint(output_channel=output_channel)-273.15 ) )

        if temperature_probe == 'D':
            current_temperature = caget('XF:11BM-ES{Env:01-Chan:D}T:C-I')
            if verbosity>=3:
                print('  Temperature = {:.3f}°C (setpoint = {:.3f}°C)'.format( current_temperature, self.temperature_setpoint(output_channel=output_channel)-273.15 ) )            
            
        return current_temperature


    def temperature_setpoint(self, output_channel='1', verbosity=3):
        #if verbosity>=1:
            #print('Temperature functions not implemented in {}'.format(self.__class__.__name__))
 
        if output_channel == '1':
            setpoint_temperature = caget('XF:11BM-ES{Env:01-Out:1}T-SP')
            
        if output_channel == '2':
            setpoint_temperature = caget('XF:11BM-ES{Env:01-Out:2}T-SP')

        if output_channel == '3':
            setpoint_temperature = caget('XF:11BM-ES{Env:01-Out:3}T-SP')

        if output_channel == '4':
            setpoint_temperature = caget('XF:11BM-ES{Env:01-Out:4}T-SP')
            
        return setpoint_temperature
        


class SampleTSAXS_Generic(Sample_Generic):
    
    ################# Direct beam transmission measurement ####################
    def intMeasure(self, output_file, exposure_time):
        '''Measure the transmission intensity of the sample by ROI4.
        The intensity will be saved in output_file
        '''        
        if abs(beam.energy(verbosity=0) - 13.5) < 0.1:
            beam.setAbsorber(4)
        elif abs(beam.energy(verbosity=0) - 17) < 0.1:
            beam.setAbsorber(6)

        print('Absorber is moved to position {}'.format(beam.absorber()[0]))

        detselect([pilatus2M])
        if beam.absorber()[0]>=4:
            bsx.move(bsx.position+6)
            beam.setTransmission(1)
            
        self.measure(exposure_time)
        
        temp_data = self.transmission_data_output(beam.absorber()[0])

        cms.modeMeasurement()
        beam.setAbsorber(0)
       
        #output_data = output_data.iloc[0:0]

        #create a data file to save the INT data
        INT_FILENAME='{}/data/{}.csv'.format(os.path.dirname(__file__) , output_file)            
        
        if os.path.isfile(INT_FILENAME):
            output_data = pds.read_csv(INT_FILENAME, index_col=0)
            output_data = output_data.append(temp_data, ignore_index=True)    
            output_data.to_csv(INT_FILENAME)
        else:
            temp_data.to_csv(INT_FILENAME)
            
    def transmission_data_output(self, slot_pos):
        
        h = db[-1]
        dtable = h.table()
        
        #beam.absorber_transmission_list = [1, 0.041, 0.0017425, 0.00007301075, 0.00000287662355, 0.000000122831826, 0.00000000513437]

            
        scan_id = h.start['scan_id']     
        I_bim5 = h.start['beam_int_bim5']  #beam intensity from bim5
        I0 = dtable.pilatus2M_stats4_total
        filename = h.start['sample_name']
        exposure_time = h.start['sample_exposure_time']
        #I2 = dtable.pilatus2M_stats2_total
        #I3 = 2*dtable.pilatus2M_stats1_total - dtable.pilatus2M_stats2_total
        #In = I3 / beam.absorber_transmission_list[slot_pos] / exposure_time

        current_data = {'a_filename': filename,
                        'b_scanID': scan_id,
                        'c_I0': I0,
                        'd_I_bim5': I_bim5,
                        'e_absorber_slot': slot_pos,
                        #'f_absorber_ratio': beam.absorber_transmission_list[slot_pos],
                        'f_absorber_ratio': beam.absorber()[1],
                        'g_exposure_seconds': exposure_time}
        

        return pds.DataFrame(data=current_data)

class SampleGISAXS_Generic(Sample_Generic):
    
    def __init__(self, name, base=None, **md):
        
        super().__init__(name=name, base=base, **md)
        self.naming_scheme = ['name', 'extra', 'th', 'exposure_time']
        self.incident_angles_default = [0.08, 0.10, 0.12, 0.15, 0.20]
        
        
    def measureSpots(self, num_spots=2, translation_amount=0.1, axis='x', exposure_time=None, extra=None, measure_type='measureSpots', **md):
        super().measureSpots(num_spots=num_spots, translation_amount=translation_amount, axis=axis, exposure_time=exposure_time, extra=extra, measure_type=measure_type, **md)
    
    
    def measureIncidentAngle(self, angle, exposure_time=None, extra=None, tiling=None, **md):
        
        self.thabs(angle)
        
        self.measure(exposure_time=exposure_time, extra=extra, tiling=tiling, **md)


    def measureIncidentAngles(self, angles=None, exposure_time=None, extra=None, tiling=None, **md):
        
        if angles is None:
            angles = self.incident_angles_default
        
        for angle in angles:
            self.measureIncidentAngle(angle, exposure_time=exposure_time, extra=extra, tiling=tiling, **md)
    
    
    def _alignOld(self, step=0):
        '''Align the sample with respect to the beam. GISAXS alignment involves
        vertical translation to the beam center, and rocking theta to get the
        sample plane parralel to the beam.
        
        The 'step' argument can optionally be given to jump to a particular
        step in the sequence.'''
        
        # TODO: Deprecate and delete
        
        if step<=0:
            # TODO: Check what mode we are in, change if necessary...
            # get_beamline().modeAlignment()
            beam.on()
        
        # TODO: Improve implementation
        if step<=2:
            #fit_scan(smy, 2.6, 35, fit='HM')
            fit_scan(smy, 2.6, 35, fit='sigmoid_r')
        
        
        if step<=4:
            #fit_scan(smy, 0.6, 17, fit='HM')
            fit_scan(smy, 0.6, 17, fit='sigmoid_r')
            fit_scan(sth, 1.2, 21, fit='max')

        #if step<=6:
        #    fit_scan(smy, 0.3, 17, fit='sigmoid_r')
        #    fit_scan(sth, 1.2, 21, fit='COM')

        if step<=8:
            fit_scan(smy, 0.2, 17, fit='sigmoid_r')
            fit_scan(sth, 0.8, 21, fit='gauss')
        
        if step<=9:
            #self._testing_refl_pos()
            #movr(sth,.1)
            #fit_scan(sth, 0.2, 41, fit='gauss')
            #fit_scan(smy, 0.2, 21, fit='gauss')
            #movr(sth,-.1)
            
            
            beam.off()
    
    
    
    def align(self, step=0, reflection_angle=0.08, verbosity=3):
        '''Align the sample with respect to the beam. GISAXS alignment involves
        vertical translation to the beam center, and rocking theta to get the
        sample plane parralel to the beam. Finally, the angle is re-optimized
        in reflection mode.
        
        The 'step' argument can optionally be given to jump to a particular
        step in the sequence.'''

        if verbosity>=4:
            print('  Aligning {}'.format(self.name))
        
        if step<=0:
            # Prepare for alignment
            
            if RE.state!='idle':
                RE.abort()
                
            if get_beamline().current_mode!='alignment':
                if verbosity>=2:
                    print("WARNING: Beamline is not in alignment mode (mode is '{}')".format(get_beamline().current_mode))
                #get_beamline().modeAlignment()
                
                
            get_beamline().setDirectBeamROI()
            
            beam.on()

        
        if step<=2:
            if verbosity>=4:
                print('    align: searching')
                
            # Estimate full-beam intensity
            value = None
            if True:
                # You can eliminate this, in which case RE.md['beam_intensity_expected'] is used by default
                self.yr(-2)
                #detector = gs.DETS[0]
                detector = get_beamline().detector[0]
                value_name = get_beamline().TABLE_COLS[0]
                
                # Check current value
                RE(count([detector]))
                # WARNING: Kludge hard-coding the detector for now
                value = pil1mroi4.read()['pil1mroi4']['value']
                
                self.yr(+2)
            
            if 'beam_intensity_expected' in RE.md and value<RE.md['beam_intensity_expected']*0.75:
                print('WARNING: Direct beam intensity ({}) lower than it should be ({})'.format(value, RE.md['beam_intensity_expected']))
                
            # Find the step-edge
            self.ysearch(step_size=0.2, min_step=0.001, intensity=value, target=0.5, verbosity=verbosity, polarity=-1)
            
            # Find the peak
            self.thsearch(step_size=0.4, min_step=0.01, target='max', verbosity=verbosity)
        
        
        if step<=4:
            if verbosity>=4:
                print('    align: fitting')
            
            fit_scan(piezo.y, 1.2*1000, 21, fit='HMi')
            fit_scan(piezo.th, 2.0*1000, 21, fit='max')
            
        if step<=5:
            
            fit_scan(piezo.y, 0.6*1000, 21, fit='HMi')
            fit_scan(piezo.th, 1.5*1000, 21, fit='max')
            


        if step<=8:
            #fit_scan(smy, 0.3, 21, fit='sigmoid_r')
            
            fit_edge(piezo.y, 0.3*1000, 21)
            fit_scan(piezo.th, 1.0*1000, 21, fit='max')
            self.setOrigin(['y', 'th'])
        
        
        if step<=9 and reflection_angle is not None:
            # Final alignment using reflected beam
            if verbosity>=4:
                print('    align: reflected beam')
            get_beamline().setReflectedBeamROI(total_angle=reflection_angle*2.0)
            #get_beamline().setReflectedBeamROI(total_angle=reflection_angle*2.0, size=[12,2])
            
            get_beamline().detselect(get_beamline().SAXS.detector, roi=3)
            
            self.thabs(reflection_angle)
            
            result = fit_scan(piezo.th, 0.2*1000, 21, fit='max') 
            sth_target = result.values['x_max']-reflection_angle
            
            if result.values['y_max']>50:
                th_target = self._axes['th'].motor_to_cur(sth_target)
                self.thsetOrigin(th_target)

            #fit_scan(smy, 0.2, 21, fit='max')
            self.setOrigin(['y'])            

        if step<=10:
            self.thabs(0.0)
            beam.off()
            
            
    def alignQuick(self, align_step=8, reflection_angle=0.08, verbosity=3):
        
        get_beamline().modeAlignment()
        #self.yo()
        self.tho()
        beam.on()
        self.align(step=align_step, reflection_angle=reflection_angle, verbosity=verbosity)
        
        

    
    def _testing_level(self, step=0,pos_x_left=-5, pos_x_right=5):
        
        #TODO: Move this code. (This should be a property of the GIBar object.)
        
        #level sample by checking bar height at pos_left and pos_right
        print('checking the level of Sample')
        if step<=1:
           cms.modeAlignment()
        self.xabs(pos_x_left)
        beam.on()
        fit_edge(smy, .6, 17)  #it's better not to move smy after scan but only the center position
        pos_y_left=smy.user_readback.value
        
        self.xabs(pos_x_right)
        fit_edge(smy, .6, 17)  #it's better not to move smy after scan but only the center position
        pos_y_right=smy.user_readback.value

        offset_schi=(pos_y_right-pos_y_left)/(pos_x_right-pos_x_left)
        print('The schi offset is {} degrees'.format(np.rad2deg(offset_schi)))
        schi.move(schi.position + offset_schi)
        
        
        #double-check the chi offset
        self.xabs(pos_x_left)
        fit_edge(smy, .6, 17)  #it's better not to move smy after scan but only the center position
        pos_y_left=smy.user_readback.value
        
        self.xabs(pos_x_right)
        fit_edge(smy, .6, 17)  #it's better not to move smy after scan but only the center position
        pos_y_right=smy.user_readback.value
        beam.off()
        
        self.xo()
        offset_schi=(pos_y_right-pos_y_left)/(pos_x_right-pos_x_left)

        if offset_schi<=0.1:
            print('schi offset is aligned successfully!')
        else:
            print('schi offset is WRONG. Please redo the level command')
        
        
    
    def do(self, step=0, align_step=0, **md):
        
        if step<=1:
            get_beamline().modeAlignment()
            
        if step<=2:
            self.xo() # goto origin


        if step<=4:
            self.yo()
            self.tho()
        
        if step<=5:
            self.align(step=align_step)
            #self.setOrigin(['y','th']) # This is done within align

        #if step<=7:
            #self.xr(0.2)

        if step<=8:
            get_beamline().modeMeasurement()
        
        if step<=10:
            #detselect([pilatus300, psccd])
            #detselect(psccd)
            #detselect(pilatus300)
            detselect(pilatus2M)
            for detector in get_beamline().detector:
                if detector.name == 'pilatus2M': 
                    RE(detector.setExposureTime(self.md['exposure_time']))
                else: 
                    detector.setExposureTime(self.md['exposure_time'])
            self.measureIncidentAngles(self.incident_angles_default, **md)
            self.thabs(0.0)


class SampleCDSAXS_Generic(Sample_Generic):
    
    def __init__(self, name, base=None, **md):
        
        super().__init__(name=name, base=base, **md)
        self.naming_scheme = ['name', 'extra', 'phi', 'exposure_time']
        self.rot_angles_default = np.arange(-45, +45+1, +1)
        #self.rot_angles_default = np.linspace(-45, +45, num=90, endpoint=True)
        
    def _set_axes_definitions(self):
        '''Internal function which defines the axes for this stage. This is kept
        as a separate function so that it can be over-ridden easily.'''
        super()._set_axes_definitions()
        
        self._axes_definitions.append( {'name': 'phi',
                            'motor': srot,
                            'enabled': True,
                            'scaling': +1.0,
                            'units': 'deg',
                            'hint': None,
                            } )
        
    def measureAngle(self, angle, exposure_time=None, extra=None, measure_type='measure', **md):
        
        self.phiabs(angle)
        
        self.measure(exposure_time=exposure_time, extra=extra, measure_type=measure_type, **md)
        
        
    def measureAngles(self, angles=None, exposure_time=None, extra=None, measure_type='measureAngles', **md):
        
        if angles is None:
            angles = self.rot_angles_default
        
        for angle in angles:
            self.measureAngle(angle, exposure_time=exposure_time, extra=extra, measure_type=measure_type, **md)
        
class SampleXR(SampleGISAXS_Generic):

    ################# Specular reflectivity (XR) measurement ####################

    def XR_scan(self, scan_type='theta_scan', theta_range=[0,1.6], theta_delta=0.1, qz_list=None, roi_size=[12,30], exposure_time=1, threshold=20000, max_exposure_time=10, extra='XR_scan', output_file=None):
        ''' Run x-ray reflectivity measurement for thin film samples. 
        Parameters
        ----------
        scan_type : list
            theta_scan: in step of theta
            q_scan: in step of q
        theta_range: list 
            The scanning range. It can be single section or multiple sections with various step_size.
            Examples:  
            [0, 1.6] or 
            [[0, .3],[0.3, 1], [1, 1.6]]                    
        theta_delta: float or list
            The scaning step. Examples:
            0.02    or
            [0.005, 0.1, 0.2]
        roi_size: float
            The szie of ROI1.
        exposure_time: float
            The mininum exposure time
        min_step : float
            The final (minimum) step size to try
        intensity : float
            The expected full-beam intensity readout
        threshold : float
            The threshold of minimum intensity. Exposure time increases automatically if < max_exposure_time 
        max_exposure_time : float
            The maximum of exposure time to limit the total time.
 
        '''
        #TODO:
        #if theta_end < theta_start:
        #    print("The theta_end is larger than theta_start!!!")
        
        #disable the besteffortcallback and plot all ROIs
        #bec.disable_table()
        cms.modeMeasurement()
        
        bec.disable_plots()

        pilatus_name.stats1.total.kind = 'hinted'
        pilatus_name.stats2.total.kind = 'hinted'

        self.naming_scheme_hold = self.naming_scheme
        self.naming_scheme = ['name', 'extra', 'th', 'exposure_time']
        default_SAXSy = SAXSy.position
        #initial exposure period
        #N = 1
        
        #move in absorber and move out the beamstop
        slot_pos = 6
        beam.setAbsorber(slot_pos)
        if beam.absorber()[0]>=4:
            bsx.move(bsx.position+6)
            beam.setTransmission(1)
        
        #create a clean dataframe and a direct beam images
        self.yr(-2)
        self.tho()
        #Energy = 13.5kev
        if abs(beam.energy(verbosity=1)-13.5) < 0.1:
            direct_beam_slot = 4
        #Energy = 17kev
        if abs(beam.energy(verbosity=1)-17) < 0.1:
            direct_beam_slot = 5
            slot_pos = 5
        beam.setAbsorber(direct_beam_slot)
        get_beamline().setSpecularReflectivityROI(total_angle=0,size=roi_size,default_SAXSy=-73)
        self.measure(exposure_time, extra='direct_beam')
        self.yo()
        
        output_data = self.XR_data_output(direct_beam_slot, exposure_time)
        #output_data = output_data.iloc[0:0]

        #create a data file to save the XRR data
        if output_file is None:
            header = db[-1]
            #XR_FILENAME='{}/data/{}.csv'.format(os.path.dirname(__file__) , header.get('start').get('scan_id')+1)
            #XR_FILENAME='{}/data/{}.csv'.format(header.start['experiment_alias_directory'], header.get('start').get('scan_id')+1)
            XR_FILENAME='{}/data/{}_{}.csv'.format(header.start['experiment_alias_directory'],header.start['sample_name'], header.get('start').get('scan_id')+1)
        else:
            XR_FILENAME='{}/data/{}.csv'.format(header.start['experiment_alias_directory'], output_file)            

        #load theta positions in scan
        if scan_type == 'theta_scan':
            #list the sth positions in scan
            theta_list=np.arange(theta_range[0], theta_range[1], theta_delta)
            
            #
            '''
            if np.size(theta_range) == 2:
                theta_list=np.arange(theta_range[0], theta_range[1], theta_delta)
            #multiple sections for measurement
            else: 
                theta_list=[]
                if np.shape(theta_range)[0] != np.size(theta_delta):
                    print("The theta_range does not match theta_delta")
                    return
                if np.shape(theta_range)[-1] != 2:
                    print("The input of theta_range is incorrect.")
                    return                
                for number, item in enumerate(theta_range):
                    theta_list_temp = np.arange(item[0], item[1], theta_delta[number])
                    theta_list.append(theta_list_temp)
                theta_list = np.hstack(theta_list)
            
            '''
        elif scan_type == 'qz_scan':
            if qz_list is not None:
                qz_list = qz_list
            else:
               qz_list = self.qz_list_default
            theta_list = np.rad2deg(np.arcsin(qz_list * header.start['calibration_wavelength_A'] /4*np.pi))

       
        for theta in theta_list:

            self.thabs(theta)
            #get_beamline().setSpecularReflectivityROI(total_angle=theta*2,size=roi_size,default_SAXSy=-73)

            get_beamline().setSpecularReflectivityROI_update(total_angle=theta*2,size=roi_size,default_SAXSy=-73)


            if cms.out_of_beamstop(total_angle=theta*2, size=roi_size):
                cms.modeMeasurement()       
                print('=========The beamstop is inserted to block the direct beam.=============')
            
            self.measure(exposure_time, extra=extra)
            temp_data = self.XR_data_output(slot_pos, exposure_time)
            
            #initial exposure period
            N = 1
            N_last = 1
            if threshold is not None and type(threshold) == int :
                    
                    
                while temp_data['e_I1'][temp_data.index[-1]] < threshold and N < max_exposure_time:   
                    if slot_pos > 0:
                        if temp_data['e_I1'][temp_data.index[-1]] < 10: #The count is too small to evaluate the next slot_pos.
                            slot_pos = slot_pos - 1
                        else:
                           slot_current = beam.absorber_transmission_list[slot_pos]*threshold/temp_data['e_I1'][temp_data.index[-1]]
                           for slot_no in np.arange(5, 0, -1):
                               if slot_current > beam.absorber_transmission_list[slot_no]:
                                   slot_pos = slot_no - 1 
                              
                        beam.setAbsorber(slot_pos)
                        print('The absorber is slot {}\n'.format(slot_pos))
                        print('The theta is {}\n'.format(theta))
                        self.measure(exposure_time, extra=extra)
                        temp_data = self.XR_data_output(slot_pos, exposure_time)
                    else:
                        if threshold/float(temp_data['e_I1'][temp_data.index[-1]]) < max_exposure_time and N_last < max_exposure_time:
                            N = np.ceil(N_last*threshold/float(temp_data['e_I1'][temp_data.index[-1]]))
                            print('e_I1={}'.format(float(temp_data['e_I1'][temp_data.index[-1]])))
                            print('N={}'.format(N))
                            print('exposure time  = {}'.format(N*exposure_time))
                        else:  
                            N = max_exposure_time
                            print('exposure time is MAX')
                        print('The absorber is slot {}\n'.format(slot_pos))
                        print('The theta is {}\n'.format(theta))


                        self.measure(N*exposure_time, extra=extra)                        
                        temp_data = self.XR_data_output(slot_pos, N*exposure_time)
                        N_last = N
                        
            elif len(threshold)>1 and temp_data['e_I1'][temp_data.index[-1]] > threshold[-1]:
                slot_pos = slot_pos+1
                print('The absorber is slot {}\n'.format(slot_pos))
                print('The theta is {}\n'.format(theta))
                beam.setAbsorber(slot_pos)
                self.measure(exposure_time, extra=extra)
                temp_data = self.XR_data_output(slot_pos, exposure_time)


            output_data = output_data.append(temp_data, ignore_index=True)    
            #save to file 
            output_data.to_csv(XR_FILENAME)
        
        #reset the changed items
        bec.enable_plots()
        #bec.enable_table()
        self.naming_scheme = self.naming_scheme_hold
        #remove the absorber completely out of the beam
        beam.absorber_out()

        pilatus_name.stats3.total.kind = 'hinted'
        pilatus_name.stats4.total.kind = 'hinted'
        
        SAXSy.move(default_SAXSy)

    def XR_abort(self):        
        '''Reset the beamline status back to origin before XRR measurement.
        '''        
        beam.off()        
        cms.modeMeasurement()
        beam.setAbsorber(0)
        #remove the absorber completely out of the beam
        beam.absorber_out()
        
        self.xo()
        self.yo()
        self.tho()

        bec.enable_plots()
        bec.enable_table()
        pilatus_name.hints = {'fields': ['pilatus2M_stats3_total', 'pilatus2M_stats4_total']}

        
    def XR_data_output(self, slot_pos, exposure_time):
        '''XRR data output in DataFrame format, including: 
                        'a_qz': qz,                  #qz
                        'b_th':sth_pos,              #incident angle 
                        'c_scanID': scan_id,         #scan ID
                        'd_I0': I0,                  #bim5 flux
                        'e_I1': I1,                  #ROI1
                        'f_I2': I2,                  #ROI2
                        'g_I3': I3,                  #2*ROI1-ROI2
                        'h_In': In,                  #reflectivity
                        'i_absorber_slot': slot_pos, #absorption slot No.
                        'j_exposure_seconds': exposure_time}   #exposure time
        '''
        
        h = db[-1]
        dtable = h.table()
        
        #beam.absorber_transmission_list = [1, 0.041, 0.0017425, 0.00007301075, 0.00000287662355, 0.000000122831826, 0.00000000513437]

        #Energy = 13.5kev
        if abs(beam.energy(verbosity=1)-13.5) < 0.1:        
            beam.absorber_transmission_list = beam.absorber_transmission_list_13p5kev

        #Energy = 17kev
        elif abs(beam.energy(verbosity=1)-17) < 0.1:        
            beam.absorber_transmission_list = beam.absorber_transmission_list_17kev
        
        else: 
            print("The absorber has not been calibrated under current Energy!!!")
            
            
        sth_pos = h.start['sample_th']
        qz = 4*np.pi*np.sin(np.deg2rad(sth_pos))/h.start['calibration_wavelength_A']
        scan_id = h.start['scan_id']     
        I0 = h.start['beam_int_bim5']  #beam intensity from bim5
        I1 = dtable.pilatus2M_stats1_total
        I2 = dtable.pilatus2M_stats2_total
        I3 = 2*dtable.pilatus2M_stats1_total - dtable.pilatus2M_stats2_total
        In = I3 / beam.absorber_transmission_list[slot_pos] / exposure_time

        current_data = {'a_qz': qz,                  #qz
                        'b_th':sth_pos,              #incident angle 
                        'c_scanID': scan_id,         #scan ID
                        'd_I0': I0,                  #bim5 flux
                        'e_I1': I1,                  #ROI1
                        'f_I2': I2,                  #ROI2
                        'g_I3': I3,                  #2*ROI1-ROI2
                        'h_In': In,                  #reflectivity
                        'i_absorber_slot': slot_pos, #absorption slot No.
                        'j_exposure_seconds': exposure_time}   #exposure time

        return pds.DataFrame(data=current_data)
        
    def XR_align(self, step=0, reflection_angle=0.15, verbosity=3):
        '''Specific alignment for XRR
        
        Align the sample with respect to the beam. XR alignment involves
        vertical translation to the beam center, and rocking theta to get the
        sample plane parralel to the beam. Finally, the angle is re-optimized
        in reflection mode.
        
        The 'step' argument can optionally be given to jump to a particular
        step in the sequence.'''

        cms.modeAlignment()

        if verbosity>=4:
            print('  Aligning {}'.format(self.name))
        
        if step<=0:
            # Prepare for alignment
            cms.modeAlignment()
            if RE.state!='idle':
                RE.abort()
            if get_beamline().current_mode!='alignment':
                if verbosity>=2:
                    print("WARNING: Beamline is not in alignment mode (mode is '{}')".format(get_beamline().current_mode))
                #get_beamline().modeAlignment()
            get_beamline().setDirectBeamROI()
            beam.on()
        
        if step<=2:
            if verbosity>=4:
                print('    align: searching')
                
            # Estimate full-beam intensity
            value = None
            if True:
                # You can eliminate this, in which case RE.md['beam_intensity_expected'] is used by default
                self.yr(-2)
                #detector = gs.DETS[0]
                detector = get_beamline().detector[0]
                value_name = get_beamline().TABLE_COLS[0]
                RE(count([detector]))
                value = detector.read()[value_name]['value']
                self.yr(+2)
            
            if 'beam_intensity_expected' in RE.md and value<RE.md['beam_intensity_expected']*0.75:
                print('WARNING: Direct beam intensity ({}) lower than it should be ({})'.format(value, RE.md['beam_intensity_expected']))
                
            # Find the step-edge
            self.ysearch(step_size=0.5, min_step=0.005, intensity=value, target=0.5, verbosity=verbosity, polarity=-1)
            
            # Find the peak
            self.thsearch(step_size=0.4, min_step=0.01, target='max', verbosity=verbosity)
        
        
        if step<=4:
            if verbosity>=4:
                print('    align: fitting')
            
            fit_scan(smy, 1.2, 21, fit='HMi')
            #time.sleep(2)
            fit_scan(sth, 1.5, 21, fit='max')
            #time.sleep(2)            
            
        if step<=8:
            
            fit_scan(smy, 0.6, 21, fit='sigmoid_r')
            
            #fit_edge(smy, 0.6, 21)
            #time.sleep(2)
            #fit_edge(smy, 0.4, 21)
            fit_scan(sth, 0.8, 21, fit='COM')
            #time.sleep(2)            
            self.setOrigin(['y', 'th'])
        
        
        if step<=9 and reflection_angle is not None:
            # Final alignment using reflected beam
            if verbosity>=4:
                print('    align: reflected beam')
                
            if abs(beam.energy(verbosity)-17)<0.1:
                reflection_angle = 0.15

            get_beamline().setReflectedBeamROI(total_angle=reflection_angle*2.0)
            #get_beamline().setReflectedBeamROI(total_angle=reflection_angle*2.0, size=[12,2])
            
            self.thabs(reflection_angle)
            
            result = fit_scan(sth, 0.1, 41, fit='max') 
            #result = fit_scan(sth, 0.2, 81, fit='max') #it's useful for alignment of SmarAct stage
            sth_target = result.values['x_max']-reflection_angle
            
            if result.values['y_max']>50:
                th_target = self._axes['th'].motor_to_cur(sth_target)
                self.thsetOrigin(th_target)

            #fit_scan(smy, 0.2, 21, fit='max')
            #self.setOrigin(['y'])            

        if step<=10:
            self.thabs(0.0)
            beam.off()

    def XR_check_alignment(self, int_angle=1, exposure_time=1, roi_size=[12, 30]):
        ''' Check the alignment of the XR.
        The total_angle is the incident angle. 
        The reflection spot should be located in the center of ROI2'''
        cms.modeMeasurement()
        cms.setSpecularReflectivityROI(total_angle=int_angle*2, size=roi_size,  default_SAXSy=-73)                    
        #sam.xo()
        sam.yo()
        sam.thabs(int_angle)
        sam.measure(exposure_time)
        print('===========sam.th moves to {}deg and ROI1 is set at {}deg. ============'.format(int_angle, int_angle*2))
        print('======Please check the ROI whether at the reflected position. =======')
        print('========If not, modify sam.th or schi to meet the reflected beam. ===========')


class Stage(CoordinateSystem):
    
    pass


class SampleStage(Stage):
    
    def __init__(self, name='SampleStage', base=None, **kwargs):
        
        super().__init__(name=name, base=base, **kwargs)
        
    def _set_axes_definitions(self):
        '''Internal function which defines the axes for this stage. This is kept
        as a separate function so that it can be over-ridden easily.'''
        
        # The _axes_definitions array holds a list of dicts, each defining an axis
        self._axes_definitions = [ {'name': 'x',
                            'motor': piezo.x,
                            'enabled': True,
                            'scaling': +1000.0,
                            'units': 'mm',
                            'hint': 'positive moves stage left/outboard (beam moves right on sample)',
                            },
                            {'name': 'y',
                            'motor': piezo.y,
                            'enabled': True,
                            'scaling': +1000.0,
                            'units': 'mm',
                            'hint': 'positive moves stage up (beam moves down on sample)',
                            },
                            {'name': 'z',
                            'motor': piezo.z,
                            'enabled': True,
                            'scaling': +1000.0,
                            'units': 'mm',
                            'hint': 'along the x-ray beam',
                            },
                            
                            {'name': 'th',
                            'motor': piezo.th,
                            'enabled': True,
                            'scaling': -1000.0,
                            'units': 'deg',
                            'hint': 'positive tilts clockwise (positive incident angle)',
                            },
                            {'name': 'chi',
                            'motor': piezo.ch,
                            'enabled': True,
                            'scaling': 1000.0,
                            'units': 'deg',
                            'hint': 'TBD',
                            },                            
                        ]     
            



class Holder(Stage):
    '''The Holder() classes are used to define bars/stages that hold one or more 
    samples. This class can thus help to keep track of coordinate conversions, 
    to store the positions of multiple samples, and to automate the measurement 
    of multiple samples.'''

    # Core methods
    ########################################

    def __init__(self, name='Holder', base=None, **kwargs):
        
        if base is None:
            base = get_default_stage()
        
        super().__init__(name=name, base=base, **kwargs)
        
        self._samples = {}

    def _set_axes_definitions(self):
        '''Internal function which defines the axes for this stage. This is kept
        as a separate function so that it can be over-ridden easily.'''
        
        # The _axes_definitions array holds a list of dicts, each defining an axis
        self._axes_definitions = [ {'name': 'x',
                            'motor': None,
                            'enabled': True,
                            'scaling': +1.0,
                            'units': 'mm',
                            'hint': 'positive moves stage left/outboard (beam moves right on sample)',
                            },
                            {'name': 'y',
                            'motor': None,
                            'enabled': True,
                            'scaling': +1.0,
                            'units': 'mm',
                            'hint': 'positive moves stage up (beam moves down on sample)',
                            },
                            {'name': 'th',
                            'motor': None,
                            'enabled': True,
                            'scaling': +1.0,
                            'units': 'deg',
                            'hint': 'positive tilts clockwise (positive incident angle)',
                            },
                        ]  

    # Sample management
    ########################################
    
    def addSample(self, sample, sample_number=None):
        '''Add a sample to this holder/bar.'''
        
        if sample_number is None:
            if len(self._samples)==0:
                sample_number = 1
            else:
                ki = [ int(key) for key in self._samples.keys() ]
                sample_number = np.max(ki) + 1
                
                
        if sample_number in self._samples.keys():
            print('Warning: Sample number {} is already defined on holder "{:s}". Use "replaceSample" if you are sure you want to eliminate the existing sample from the holder.'.format(sample_number, self.name) )
            
        else:
            self._samples[sample_number] = sample
            
        self._samples[sample_number] = sample
        
        sample.set_base_stage(self)
        sample.md['holder_sample_number'] = sample_number

       
    def removeSample(self, sample_number):
        '''Remove a particular sample from this holder/bar.'''
        
        del self._samples[sample_number]
        
    
    def removeSamplesAll(self):
        
        self._samples = {}
        

    def replaceSample(self, sample, sample_number):
        '''Replace a given sample on this holder/bar with a different sample.'''
        
        self.removeSample(sample_number)
        self.addSample(sample, sample_number)
                
                
    def getSample(self, sample_number, verbosity=3):
        '''Return the requested sample object from this holder/bar.
        
        One can provide an integer, in which case the corresponding sample
        (from the holder's inventory) is returned. If a string is provided, 
        the closest-matching sample (by name) is returned.'''
        
        if type(sample_number) is int:
            if sample_number not in self._samples:
                if verbosity>=1:
                    print('Error: Sample {} not defined.'.format(sample_number))
                return None
            
            sample_match = self._samples[sample_number]

            if verbosity>=3:
                print('{}: {:s}'.format(sample_number, sample_match.name))
            
            return sample_match
        
            
        elif type(sample_number) is str:
            
            # First search for an exact name match
            matches = 0
            sample_match = None
            sample_i_match = None
            for sample_i, sample in sorted(self._samples.items()):
                if sample.name==sample_number:
                    matches += 1
                    if sample_match is None:
                        sample_match = sample
                        sample_i_match = sample_i
                    
            if matches==1:
                if verbosity>=3:
                    print('{}: {:s}'.format(sample_i_match, sample_match.name))
                return sample_match
                    
            elif matches>1:
                if verbosity>=2:
                    print('{:d} exact matches for "{:s}", returning sample {}: {:s}'.format(matches, sample_number, sample_i_match, sample_match.name))
                return sample_match
            
            
            # Try to find a 'start of name' match
            for sample_i, sample in sorted(self._samples.items()):
                if sample.name.startswith(sample_number):
                    matches += 1
                    if sample_match is None:
                        sample_match = sample
                        sample_i_match = sample_i
                        
            if matches==1:
                if verbosity>=3:
                    print('Beginning-name match: {}: {:s}'.format(sample_i_match, sample_match.name))
                return sample_match
                    
            elif matches>1:
                if verbosity>=2:
                    print('{:d} beginning-name matches for "{:s}", returning sample {}: {:s}'.format(matches, sample_number, sample_i_match, sample_match.name))
                return sample_match
            
            # Try to find a substring match
            for sample_i, sample in sorted(self._samples.items()):
                if sample_number in sample.name:
                    matches += 1
                    if sample_match is None:
                        sample_match = sample
                        sample_i_match = sample_i
                        
            if matches==1:
                if verbosity>=3:
                    print('Substring match: {}: {:s}'.format(sample_i_match, sample_match.name))
                return sample_match
                    
            elif matches>1:
                if verbosity>=2:
                    print('{:d} substring matches for "{:s}", returning sample {}: {:s}'.format(matches, sample_number, sample_i_match, sample_match.name))
                return sample_match
            
            if verbosity>=1:
                print('No sample has a name matching "{:s}"'.format(sample_number))
            return None
            
            
        else:
            
            print('Error: Sample designation "{}" not understood.'.format(sample_number))
            return None
    
    import string
    def getSamples(self, range=None, verbosity=3):
        '''Get the list of samples associated with this holder.
        
        If the optional range argument is provided (2-tuple), then only sample
        numbers within that range (inclusive) are run. If range is instead a 
        string, then all samples with names that match are returned.'''
        
        samples = []
        
        if range is None:
            for sample_number in sorted(self._samples):
                samples.append(self._samples[sample_number])
                
        elif type(range) is list:
            if type(range[0]) is int:
                if len(range) == 2:
                    start, stop = range
                    for sample_number in sorted(self._samples):
                        if sample_number>=start and sample_number<=stop:
                            samples.append(self._samples[sample_number])
                else: 
                    for sample_number in sorted(self._samples):
                        for ii in range: 
                            if sample_number == ii:
                                samples.append(self._samples[sample_number])                
 
            elif type(range[0]) is str: #For 96 well holder, format: A1, D2 ...
                for sample_number in sorted(self._samples):
                    sample_row = string.ascii_lowercase(sample_number[0])
                    sample_column = int(sample_number[1:])
                    sample_number = sample_row*12 + sample_column
                    samples.append(self._samples[sample_number])                 

        elif type(range) is str:
            for sample_number, sample in sorted(self._samples.items()):
                if range in sample.name:
                    samples.append(sample)
                    
        elif type(range) is int:
            samples.append(self._samples[range])
        
        else:
            if verbosity>=1:
                print('Range argument "{}" not understood.'.format(range))
            
            
        return samples
        
        
    def listSamples(self):
        '''Print a list of the current samples associated with this holder/
        bar.'''
        
        for sample_number, sample in sorted(self._samples.items()):
            print( '{}: {:s}'.format(sample_number, sample.name) )
        

    def gotoSample(self, sample_number):
        
        sample = self.getSample(sample_number, verbosity=0)
        sample.gotoAlignedPosition()
        
        return sample
        
        
    # Control methods
    ########################################
    def setTemperature(self, temperature, output_channel='1', verbosity=3):
        #if verbosity>=1:
            #print('Temperature functions not implemented in {}'.format(self.__class__.__name__))
        if output_channel == '1':
            if verbosity>=2:
                print('  Changing temperature setpoint from {:.3f}°C  to {:.3f}°C'.format(caget('XF:11BM-ES{Env:01-Out:1}T-SP')-273.15, temperature))
            caput('XF:11BM-ES{Env:01-Out:1}T-SP', temperature+273.15)
        
        if output_channel == '2':
            if verbosity>=2:
                print('  Changing temperature setpoint from {:.3f}°C  to {:.3f}°C'.format(caget('XF:11BM-ES{Env:01-Out:2}T-SP')-273.15, temperature))
            caput('XF:11BM-ES{Env:01-Out:2}T-SP', temperature+273.15)
        
        if output_channel == '3':
            if verbosity>=2:
                print('  Changing temperature setpoint from {:.3f}°C  to {:.3f}°C'.format(caget('XF:11BM-ES{Env:01-Out:3}T-SP')-273.15, temperature))
            caput('XF:11BM-ES{Env:01-Out:3}T-SP', temperature+273.15)

        if output_channel == '4':
            if verbosity>=2:
                print('  Changing temperature setpoint from {:.3f}°C  to {:.3f}°C'.format(caget('XF:11BM-ES{Env:01-Out:4}T-SP')-273.15, temperature))
            caput('XF:11BM-ES{Env:01-Out:4}T-SP', temperature+273.15)
            
            
    def temperature(self, temperature_probe='A', output_channel='1', verbosity=3):
        #if verbosity>=1:
            #print('Temperature functions not implemented in {}'.format(self.__class__.__name__))
 
        if temperature_probe == 'A':
            current_temperature = caget('XF:11BM-ES{Env:01-Chan:A}T:C-I')
            if verbosity>=3:
                print('  Temperature = {:.3f}°C (setpoint = {:.3f}°C)'.format( current_temperature, self.temperature_setpoint(output_channel=output_channel)-273.15 ) )
            
        if temperature_probe == 'B':
            current_temperature = caget('XF:11BM-ES{Env:01-Chan:B}T:C-I')
            if verbosity>=3:
                print('  Temperature = {:.3f}°C (setpoint = {:.3f}°C)'.format( current_temperature, self.temperature_setpoint(output_channel=output_channel)-273.15 ) )

        if temperature_probe == 'C':
            current_temperature = caget('XF:11BM-ES{Env:01-Chan:C}T:C-I')
            if verbosity>=3:
                print('  Temperature = {:.3f}°C (setpoint = {:.3f}°C)'.format( current_temperature, self.temperature_setpoint(output_channel=output_channel)-273.15 ) )

        if temperature_probe == 'D':
            current_temperature = caget('XF:11BM-ES{Env:01-Chan:D}T:C-I')
            if verbosity>=3:
                print('  Temperature = {:.3f}°C (setpoint = {:.3f}°C)'.format( current_temperature, self.temperature_setpoint(output_channel=output_channel)-273.15 ) )            
            
        return current_temperature

    def temperature_setpoint(self, output_channel='1', verbosity=3):
        #if verbosity>=1:
            #print('Temperature functions not implemented in {}'.format(self.__class__.__name__))
 
        if output_channel == '1':
            setpoint_temperature = caget('XF:11BM-ES{Env:01-Out:1}T-SP')
            
        if output_channel == '2':
            setpoint_temperature = caget('XF:11BM-ES{Env:01-Out:2}T-SP')

        if output_channel == '3':
            setpoint_temperature = caget('XF:11BM-ES{Env:01-Out:3}T-SP')

        if output_channel == '4':
            setpoint_temperature = caget('XF:11BM-ES{Env:01-Out:4}T-SP')
            
        return setpoint_temperature
        
        
        
    # Action (measurement) methods
    ########################################
                           
    def doSamples(self, range=None, verbosity=3, **md):
        '''Activate the default action (typically measurement) for all the samples.
        
        If the optional range argument is provided (2-tuple), then only sample
        numbers within that range (inclusive) are run. If range is instead a 
        string, then all samples with names that match are returned.'''
        
        for sample in self.getSamples(range=range):
            if verbosity>=3:
                print('Doing sample {}...'.format(sample.name))
            sample.do(verbosity=verbosity, **md)
            
            
    def doTemperature(self, temperature, wait_time=None, temperature_probe='A', output_channel='1', temperature_tolerance=0.4, range=None, verbosity=3, poling_period=2.0, **md):
        
        # Set new temperature
        self.setTemperature(temperature, output_channel=output_channel, verbosity=verbosity)
        
        # Wait until we reach the temperature
        #while abs(self.temperature(verbosity=0) - temperature)>temperature_tolerance:
        while abs(self.temperature(temperature_probe=temperature_probe, verbosity=0) - temperature)>temperature_tolerance:
            if verbosity>=3:
                print('  setpoint = {:.3f}°C, Temperature = {:.3f}°C          \r'.format(self.temperature_setpoint()-273.15, self.temperature(verbosity=0)), end='')
            time.sleep(poling_period)
            
            
        # Allow for additional equilibration at this temperature
        if wait_time is not None:
            time.sleep(wait_time)
            
        self.doSamples(range=range, verbosity=verbosity, **md)
            

    def doTemperatures(self, temperatures,  wait_time=None, temperature_probe='A', output_channel='1', temperature_tolerance=0.4, range=None, verbosity=3, **md):
        
        for temperature in temperatures:
            
            self.doTemperature(temperature,  wait_time=wait_time, temperature_probe=temperature_probe, output_channel=output_channel, temperature_tolerance=temperature_tolerance, range=range, verbosity=verbosity, **md)
                



class PositionalHolder(Holder):
    '''This class is a sample holder that is one-dimensional. E.g. a bar with a
    set of samples lined up, or a holder with a set number of slots for holding
    samples. This class thus helps to associate each sample with its position
    on the bar.'''

    # Core methods
    ########################################

    def __init__(self, name='PositionalHolder', base=None, **kwargs):
        
        super().__init__(name=name, base=base, **kwargs)
        
        self._positional_axis = 'x'
        self.GaragePosition=[]
        
    # Sample management
    ########################################

    def slot(self, sample_number):
        '''Moves to the selected slot in the holder.'''
        
        getattr(self, self._positional_axis+'abs')( self.get_slot_position(sample_number) )
        
    
    def get_slot_position(self, slot):
        '''Return the motor position for the requested slot number.'''
        # This method should be over-ridden in sub-classes, so as to properly
        # implement the positioning appropriate for that holder.
        
        position = 0.0 + slot*1.0
        
        return position
        
        
    def addSampleSlot(self, sample, slot, detector_opt='SAXS'):
        '''Adds a sample to the specified "slot" (defined/numbered sample 
        holding spot on this holder).'''
        
        self.addSample(sample, sample_number=slot)
        sample.setOrigin( [self._positional_axis], [self.get_slot_position(slot)] )
        sample.detector = detector_opt
        
    def addSampleSlotPosition(self, sample, slot, position, detector_opt='BOTH', incident_angles=None, transmission=1):
        '''Adds a sample to the specified "slot" (defined/numbered sample 
        holding spot on this holder).'''
        
        self.addSample(sample, sample_number=slot)
        sample.setOrigin( [self._positional_axis], [position] )
        sample.detector = detector_opt
        sample.incident_angles = incident_angles
        sample.transmission = transmission
        #sample.exposure_time_WAXS = None 
        #sample.exposure_time_SAXS = None 
        
        
    def listSamplesPositions(self):
        '''Print a list of the current samples associated with this holder/
        bar.'''
        
        for sample_number, sample in self._samples.items():
            #pos = getattr(sample, self._positional_axis+'pos')(verbosity=0)
            pos = sample.origin(verbosity=0)[self._positional_axis]
            print( '%s: %s (%s = %.3f)' % (str(sample_number), sample.name, self._positional_axis, pos) )

    def listSamplesDetails(self):
        '''Print a list of the current samples associated with this holder/
        bar.'''
        
        for sample_number, sample in self._samples.items():
            #pos = getattr(sample, self._positional_axis+'pos')(verbosity=0)
            pos = sample.origin(verbosity=0)[self._positional_axis]
            print( '%s: %s (%s = %.3f) %s' % (str(sample_number), sample.name, self._positional_axis, pos, sample.detector) )
            
    def addGaragePosition(self, shelf_num, spot_num):
        '''the position in garage'''
        if shelf_num not in range(1, 5) or spot_num not in range(1, 4):
            print('Out of the range in Garage (4 x 3)')
                    
        self.GaragePosition=[shelf_num, spot_num]

    def intMeasure(self, output_file, exposure_time):
        
        for sample in self.getSamples():
            sample.gotoOrigin()
            sample.intMeasure(output_file, exposure_time)

    def saveSampleStates(self, output_file = None):
        '''Print a list of the current samples associated with this holder/bar. 
        
        It can be saved in the output_file under setup'''
        
        states = {}
        for sample_number, sample in sorted(self._samples.items()):
            states[sample_number]  = sample.save_state()
        
        cms.samples_states = states
        if output_file is not None:
            with open(output_file, 'wb') as handle:
                pickle.dump(states, handle, protocol=pickle.HIGHEST_PROTOCOL)
                
        return states
    
    def restoreSampleStates(self, input_file = None):
        
        if input_file is not None:
            with open(input_file,'rb') as handle:
                cms.samples_states = pickle.load(handle)
            
        for sample_number, sample in sorted(self._samples.items()):            
            sample.restore_state(cms.samples_states[sample_number])
            print(sample.save_state())        

    
    def checkPositions(self):
        for sample in self.getSamples():
            sample.gotoOrigin()
            time.sleep(1)
            
class GIBar(PositionalHolder):
    '''This class is a sample bar for grazing-incidence (GI) experiments.'''
    
    # Core methods
    ########################################

    def __init__(self, name='GIBar', base=None, **kwargs):
        
        super().__init__(name=name, base=base, **kwargs)
        
        self._positional_axis = 'x'
        
        self.xsetOrigin(-54.19)
        self.ysetOrigin(4.0)
        
        self.mark('right edge', x=+108.2)
        self.mark('left edge', x=0)
        self.mark('center', x=54.1, y=0)
             
             
    def addSampleSlotPosition(self, sample, slot, position, detector_opt='SAXS', incident_angles=None, account_substrate=True):
        '''Adds a sample to the specified "slot" (defined/numbered sample 
        holding spot on this holder).'''
        
        super().addSampleSlotPosition(sample, slot, position, incident_angles)

        # Adjust y-origin to account for substrate thickness
        if account_substrate and 'substrate_thickness' in sample.md:
            sample.ysetOrigin( -1.0*sample.md['substrate_thickness'] )
        
        sample.detector=detector_opt
        
        



    def alignSamples(self, range=None, step=0, x_offset=0, verbosity=3, **md):
        '''Iterates through the samples on the holder, aligning each one.'''
        
        if step<=0:
            get_beamline().modeAlignment()
        
        
        if step<=5:
            for sample in self.getSamples(range=range):
                sample.gotoOrigin(['x','y','th'])
                sample.xr(x_offset)
                sample.align()
            
            
        if step<=10:
            if verbosity>=3:
                print('Alignment complete.')
                for i, sample in enumerate(self.getSamples()):
                    print('Sample {} ({})'.format(i+1, sample.name))
                    print(sample.save_state())


    def alignSamplesQuick(self, range=None, step=0, x_offset=0, verbosity=3, **md):
        '''Iterates through the samples on the holder, aligning each one.'''
        
        if step<=0:
            get_beamline().modeAlignment()
        
        
        if step<=5:
            for sample in self.getSamples(range=range):
                sample.gotoOrigin(['x','y','th'])
                sample.xr(x_offset)
                sample.alignQuick(reflection_angle=0.07)
            
            
        if step<=10:
            if verbosity>=3:
                print('Alignment complete.')
                for i, sample in enumerate(self.getSamples()):
                    print('Sample {} ({})'.format(i+1, sample.name))
                    print(sample.save_state())
                

    def alignSamplesVeryQuick(self, range=None, step=0, x_offset=0, verbosity=3, **md):
        '''Iterates through the samples on the holder, aligning each one.'''
        
        if step<=0:
            get_beamline().modeAlignment()
            beam.on()
            caput('XF:11BMB-ES{Det:SAXS}:cam1:AcquireTime', 0.25)
            caput('XF:11BMB-ES{Det:SAXS}:cam1:AcquirePeriod', 0.30)
        
        
        if step<=5:
            for sample in self.getSamples(range=range):
                sample.gotoOrigin(['x','y','th'])
                sample.xr(x_offset)
                sample.alignVeryQuick(intensity=INTENSITY_EXPECTED_025, mode_control=False)
                
             
        if step<=10:
            if verbosity>=3:
                print('Alignment complete.')
                for i, sample in enumerate(self.getSamples()):
                    print('Sample {} ({})'.format(i+1, sample.name))
                    print(sample.save_state())
                

                
    def measureSamples(self, range=None, step=0, angles=None, exposure_time=15, x_offset=0, verbosity=3, **md):
        '''Measures all the samples.
        
        If the optional range argument is provided (2-tuple), then only sample
        numbers within that range (inclusive) are run. If range is instead a 
        string, then all samples with names that match are returned.'''

        if step<=0:
            get_beamline().modeMeasurement()

        if step<=5:
            for sample in self.getSamples(range=range):
                if verbosity>=3:
                    print('Measuring sample {}...'.format(sample.name))
                
                sample.gotoOrigin(['x','y','th'])
                sample.xr(x_offset)
                sample.measureIncidentAngles(angles=angles, verbosity=verbosity, exposure_time=exposure_time, **md)
            
            
            
    def printSaveStates(self, range=None, verbosity=3, **md):
        
        if range is None:
            range_start = 0
        else:
            range_start = range[0]
        
        save_string = 'origins = [\n'
        
        for i, sample in enumerate(self.getSamples(range=range)):
            
            sample_id = range_start + i + 1
            
            save_string += '    {} , # Sample {}\n'.format(sample.save_state(), sample_id)
            #save_string += '    {} , # Sample {} ({})\n'.format(sample.save_state(), sample_id, sample.name)
            
            
        save_string += '    ]\n'
        save_string += 'for origin, sample in zip(origins, hol.getSamples()):\n'
        save_string += '    sample.restore_state(origin)\n'
        
        print(save_string)
        
                
        
   #def _testing_level(self, step=0,pos_x_left=-5, pos_x_right=5):
        
        ##TODO: Move this code. (This should be a property of the GIBar object.)
        
        ##level GIBar by checking bar height at pos_left and pos_right
        #print('checking the level of GIBar')
        #if step<=1:
           #cms.modeAlignment()
           
        #self.xabs(pos_x_left)
        #fit_scan(smy, .6, 17, fit='sigmooid_r')  #it's better not to move smy after scan but only the center position
        #pos_y_left=smy.user_readback.value
        
        
        #self.xabs(pos_x_right)
        #fit_scan(smy, .6, 17, fit='sigmooid_r')
        #pos_y_right=smy.user_readback.value

        #offset_schi=(pos_y_right-pos_y_left)/(pos_x_right-pos_x_left)
        #movr(sch, offset_schi)
        
        
        ##double-check the chi offset
        #self.xabs(pos_x_left)
        #fit_scan(smy, .6, 17, fit='sigmooid_r')  #it's better not to move smy after scan but only the center position
        #pos_y_left=smy.user_readback.value
        
        #self.xabs(pos_x_right)
        #fit_scan(smy, .6, 17, fit='sigmooid_r')
        #pos_y_right=smy.user_readback.value
        
        #offset_schi=(pos_y_right-pos_y_left)/(pos_x_right-pos_x_left)

        #self.xo()
        #self.yo()
        #if offset_schi<=0.1:
            #print('schi offset is aligned successfully!')
        #else:
            #print('schi offset is WRONG. Please redo the level command')


class GIBar_long_thermal(GIBar):
    '''This class is a sample bar with heating/cooling feature and 6" long bar for grazing-incidence (GI) experiments.'''
    
    # Core methods
    ########################################

    def __init__(self, name='GIBar', base=None, **kwargs):
        
        super().__init__(name=name, base=base, **kwargs)
        
        self._positional_axis = 'x'
        
        # Set the x and y origin to be the center of slot 8

        #self.xsetOrigin(-71.89405-22.1) # TODO: Update this value
        #self._axes['y'].origin = 7.06
        self._axes['y'].origin = 2.06
        
        self.mark('right edge', x=+152.4)
        self.mark('left edge', x=0)
        self.mark('center', x=76.2, y=0)
             
class CapillaryHolder(PositionalHolder):
    '''This class is a sample holder that has 15 slots for capillaries.'''

    # Core methods
    ########################################

    def __init__(self, name='CapillaryHolder', base=None, **kwargs):
        
        super().__init__(name=name, base=base, **kwargs)
        
        self._positional_axis = 'x'
        
        self.x_spacing = 6.342 # 3.5 inches / 14 spaces
        
        # slot  1; smx = +26.60
        # slot  8; smx = -17.80
        # slot 15; smx = -61.94
        
        # Set the x and y origin to be the center of slot 8
        #self.xsetOrigin(-16.7)
        #self.ysetOrigin(-2.36985)
        self.ysetOrigin(-2.36985)  
        self.xsetOrigin(-16.7+-0.3)
        
        self.mark('right edge', x=+54.4)
        self.mark('left edge', x=-54.4)
        self.mark('bottom edge', y=-12.71)
        self.mark('center', x=0, y=0)
                
                
    def get_slot_position(self, slot):
        '''Return the motor position for the requested slot number.'''
        
        return +1*self.x_spacing*(slot-8)
        
        
class CapillaryHolderHeated(CapillaryHolder):
    
    def update_sample_names(self):
        
        for sample in self.getSamples():
            if 'temperature' not in sample.naming_scheme:
                sample.naming_scheme.insert(-1, 'temperature')
    
    def doHeatCool(self, heat_temps, cool_temps, exposure_time=None, stabilization_time=120, temp_tolerance=0.5, step=1):
        
        if step<=1:
            
            for temperature in heat_temps:
                try:
                    self.setTemperature(temperature)
                    
                    while self.temperature(verbosity=0) < temperature-temp_tolerance:
                        time.sleep(5)
                    time.sleep(stabilization_time)
                    
                    for sample in self.getSamples():
                        sample.gotoOrigin()
                        sample.xr(-0.05)
                        sample.measure(exposure_time)
                        
                except HTTPError:
                    pass


        if step<=5:
            
            for temperature in heat_temps:
                try:
                    self.setTemperature(temperature)
                
                    self.setTemperature(temperature)
                
                    while self.temperature(verbosity=0) > temperature+temp_tolerance:
                        time.sleep(5)
                    time.sleep(stabilization_time)

                    for sample in self.getSamples():
                        sample.gotoOrigin()
                        sample.xr(0.1)
                        sample.measure(exposure_time)
                        
                except HTTPError:
                    pass
        

class WellPlateHolder(PositionalHolder):
    '''This class is a sample holder for 96 well plate. 
       row: A--E; column: 1--12
       The sample names are like: 'A1', 'D3', 'E12'
       It uses two stages, smx and smy2 to locate the sample.
       
    '''

    # Core methods
    ########################################

    def __init__(self, name='CapillaryHolder', base=None, **kwargs):
        
        super().__init__(name=name, base=base, **kwargs)
        
        self._positional_axis = ['x','yy']

        self._axes['y'].origin = -5  #smy stage should be set with the limit [-5.5, -5]
        self._axes['x'].origin = -49.25
        self._axes['yy'].origin = 3.3
        
        
        self.x_spacing = 9 # 9mm seperation both in x and yy direction
        self.yy_spacing = 9 
        
        
    def _set_axes_definitions(self):
        '''Internal function which defines the axes for this stage. This is kept
        as a separate function so that it can be over-ridden easily.'''
        
        # The _axes_definitions array holds a list of dicts, each defining an axis
        super()._set_axes_definitions()

        self._axes_definitions.append ( {'name': 'yy',
                            'motor': smy2,
                            'enabled': True,
                            'scaling': +1.0,
                            'units': 'mm',
                            'hint': 'positive moves stage up',
                            } )
                        

    def slot(self, sample_number):
        '''Moves to the selected slot in the holder.'''
        
        getattr(self, self._positional_axis[0]+'abs')( self.get_slot_position(sample_number) )
        
    
    def get_slot_position(self, slot):
        '''Return the motor position for the requested slot number.'''
        # This method should be over-ridden in sub-classes, so as to properly
        # implement the positioning appropriate for that holder.
        # slot is like 'A1', 'D12'
        

        sample_row = ord(slot[0])-ord('A')
        sample_column = int(slot[1:])-1
        #sample_number = sample_row*12 + sample_column
               
        return sample_column*self.x_spacing,  sample_row*self.yy_spacing
        
        
    def addSample(self, sample, sample_number=None):
        '''Add a sample to this holder/bar.'''
        
        if sample_number is None:
            if len(self._samples)==0:
                sample_number = 1
            else:
                ki = [ int(key) for key in self._samples.keys() ]
                sample_number = np.max(ki) + 1
                
                
        if sample_number in self._samples.keys():
            print('Warning: Sample number {} is already defined on holder "{:s}". Use "replaceSample" if you are sure you want to eliminate the existing sample from the holder.'.format(sample_number, self.name) )
            
        else:
            self._samples[sample_number] = sample
            
        self._samples[sample_number] = sample
        
        sample.set_base_stage(self)
        sample.md['holder_sample_number'] = sample_number
        
        
    def addSampleSlot(self, sample, slot):
        '''Adds a sample to the specified "slot" (defined/numbered sample 
        holding spot on this holder).'''
 
       
        self.addSample(sample, sample_number=slot)
        sample.setOrigin( ['x'], [self.get_slot_position(slot)[0]] )
        sample.setOrigin( ['yy'], [self.get_slot_position(slot)[1]] )

                
    def listSamplesPositions(self):
        '''Print a list of the current samples associated with this holder/
        bar.'''
        
        for sample_number, sample in self._samples.items():
            pos = getattr(sample, self._positional_axis+'pos')(verbosity=0)
            print( '%s: %s (%s = %.3f)' % (str(sample_number), sample.name, self._positional_axis, pos) )


    def listSamples(self):
        '''Print a list of the current samples associated with this holder/
        bar.'''
         
        for sample_number, sample in sorted(self._samples.items()):
            print( '{}: {:s}'.format(sample_number, sample.name) )
            
            
    def gotoAlignedPosition(self):
        '''Goes to the currently-defined 'aligned' position for this stage. If
        no specific aligned position is defined, then the zero-point for the stage
        is used instead.'''
        
        # TODO: Optional offsets? (Like goto mark?)
        self.gotoOrigin(axes=self._positional_axis)
        #time.sleep(10)

    def getSample(self, sample_number, verbosity=3):
        '''Return the requested sample object from this holder/bar.
        
        One can provide an integer, in which case the corresponding sample
        (from the holder's inventory) is returned. If a string is provided, 
        the closest-matching sample (by name) is returned.'''
        
        if sample_number not in self._samples:
            if verbosity>=1:
                print('Error: Sample {} not defined.'.format(sample_number))
            return None
        
        sample_match = self._samples[sample_number]

        if verbosity>=3:
            print('{}: {:s}'.format(sample_number, sample_match.name))
        
        return sample_match            
        
    def namingWellPlate(name,row_range=['A', 'G'], column_range=[1, 12]):
        '''Name the samples in the well plate.  
        The format is 'NAME_A05_'
        '''
        md = {
            'owner' : 'J. Paloni (MIT) group' ,
            'series' : 'various' ,
            }
            
        for row_number in range(ord(row_range[0]), ord(row_range[1])+1):
            row=chr(row_number)
            #print(row)
            for column in range(column_range[0], column_range[1]+1):
                #print(column)
                sample_name = '{}_{}{}'.format(name, row, column)
                position = '{}'.format(row)+'{0:0=2d}'.format(column)
                self.addSampleSlot( SampleTSAXS( sample_name), position )


stg = SampleStage()
def get_default_stage():
    return stg




if False:
    # For testing:
    # %run -i /opt/ipython_profiles/profile_collection/startup/94-sample.py
    sam = SampleGISAXS_Generic('testing_of_code')
    sam.mark('here')
    #sam.mark('XY_field', 'x', 'y')
    #sam.mark('specified', x=1, th=0.1)
    #sam.naming(['name', 'extra', 'clock', 'th', 'exposure_time', 'id'])
    #sam.thsetOrigin(0.5)
    #sam.marks()
    
    
    hol = CapillaryHolder(base=stg)
    hol.addSampleSlot( SampleGISAXS_Generic('test_sample_01'), 1.0 )
    hol.addSampleSlot( SampleGISAXS_Generic('test_sample_02'), 3.0 )
    hol.addSampleSlot( SampleGISAXS_Generic('test_sample_03'), 5.0 )
    
    sam = hol.getSample(1)


    
