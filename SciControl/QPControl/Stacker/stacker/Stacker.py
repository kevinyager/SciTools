from BLEX.Base import *
from BLEX.sample import *

import zmq
# ZeroMQ is used to pass commands from a client instance to the
# server instance (which is actually driving the hardware).

STACKER_VERSION = '1.22 2021-08-09'
import inspect    


class MotorClient(Motor):
    '''A virtual motor that passes commands over the network.'''
    def __init__(self, name='<unnamed>', command_client=None, **kwargs):
        self.name = name
        self.command_client = command_client
        
    def get_position(self, **kwargs):
        command = { 
            'system': 'sam',
            'command': 'xpos',
            'args': [],
            'kwargs': {},
            }        
        response = self.command_client.client_send(command)
        return_value = response['return_value']
        return return_value
    
    def set_position(self, position, **kwargs):
        
        if 'velocity' in kwargs:
            self.velocity = kwargs['velocity']
        difference = position - self.get_position()
        time_to_complete = abs(difference/self.velocity)
        
        self.position = position
        
        
    # End class MotorClient(Motor)
    ########################################


class SampleStage(Stage):
    
    def __init__(self, name='sam', base=None, motors={}, connect_Xeryon=True, connect_Instec=True, **kwargs):
        self._motors = motors
        super().__init__(name=name, base=base, **kwargs)
        
        if connect_Xeryon:
            from Devices.XeryonActuator import MotorXeryon
            self.actuator = MotorXeryon(name='actuator')
            
        if connect_Instec:
            from Devices.Instec import InstecThermalChuck
            self.Tcontrol = InstecThermalChuck(name='sam_Tcontrol', serial_device="COM5", common=self._common, verbosity=self.verbosity, log_verbosity=self.log_verbosity)
            
        
    def _set_axes_definitions(self):
        '''Internal function which defines the axes for this stage. This is kept
        as a separate function so that it can be over-ridden easily.'''
        
        # The _axes_definitions array holds a list of dicts, each defining an axis
        self._axes_definitions = [ {'name': 'x',
                            'motor': self._motors['x'],
                            'enabled': True,
                            'scaling': -1.0,
                            'units': 'mm',
                            'hint': 'positive moves sample right (view moves left on screen)',
                            'limits': [-25, +25],
                            },
                            {'name': 'y',
                            'motor': self._motors['y'],
                            'enabled': True,
                            'scaling': -1.0,
                            'units': 'mm',
                            'hint': 'positive moves sample away (view moves down on screen)',
                            'limits': [-25, +25],
                            },
                            {'name': 'phi',
                            'motor': self._motors['phi'],
                            'enabled': True,
                            'scaling': +1.0,
                            'units': 'deg',
                            'hint': 'positive rotates clockwise (LHR about +z)',
                            'limits': [-145, +110],
                            },
                            #{'name': 'T',
                            #'motor': self._motors['T'],
                            #'enabled': True,
                            #'scaling': +1.0,
                            #'units': 'C',
                            #'hint': 'positive increases temperature',
                            #},
                            
                        ]     
                            
    def up(self):
        self.actuator.up()
    def down(self):
        self.actuator.down()

    def hold(self):
        self.Tcontrol.vacuum_on()
    def release(self):
        self.Tcontrol.vacuum_off()

    # Basic temperature control
    def T(self):
        return self.Tcontrol.get_position()
    def Tabs(self, temperature):
        self.Tcontrol.set_position(temperature)
    def Tr(self, T_change):
        T_current = self.T()
        self.Tcontrol.set_position(T_current+T_change)
    def Tunits(self):
        return 'C'
        

class CameraStage(Stage):
    
    def __init__(self, name='cam', base=None, motors={}, **kwargs):
        self._motors = motors
        super().__init__(name=name, base=base, **kwargs)
        
    def _set_axes_definitions(self):
        '''Internal function which defines the axes for this stage. This is kept
        as a separate function so that it can be over-ridden easily.'''
        
        # The _axes_definitions array holds a list of dicts, each defining an axis
        self._axes_definitions = [ {'name': 'z',
                            #'motor': MotorDummy(name='zmotor'),
                            'motor': self._motors['z'],
                            'enabled': True,
                            'scaling': -1.0,
                            'units': 'mm',
                            'hint': 'positive moves camera up (away from sample)',
                            },
                        ]     


class StampStage(Stage):
    
    def __init__(self, name='stmp', base=None, motors={}, connect_Thorlabs=True, **kwargs):
        self._motors = motors
        super().__init__(name=name, base=base, **kwargs)
        
        if connect_Thorlabs:
            from Devices.Thorlabs import MotorThorlabs_Linear
            self.gripper = MotorThorlabs_Linear(SN="27258631", name='gripper', common=self._common, verbosity=self.verbosity, log_verbosity=self.log_verbosity)
            
            self._gripper_open_position = 6
            self._gripper_closed_position = 11
        
        
    def _set_axes_definitions(self):
        '''Internal function which defines the axes for this stage. This is kept
        as a separate function so that it can be over-ridden easily.'''
        
        # The _axes_definitions array holds a list of dicts, each defining an axis
        self._axes_definitions = [ {'name': 'x',
                            'motor': self._motors['x'],
                            'enabled': True,
                            'scaling': -1.0,
                            'units': 'mm',
                            'hint': 'positive moves stamp right',
                            },
                            {'name': 'y',
                            'motor': self._motors['y'],
                            'enabled': True,
                            'scaling': -1.0,
                            'units': 'mm',
                            'hint': 'positive moves stamp away (up in image)',
                            },
                            {'name': 'z',
                            'motor': self._motors['z'],
                            'enabled': True,
                            'scaling': +1.0,
                            'units': 'mm',
                            'hint': 'positive moves stamp up (away from sample)',
                            },
                            {'name': 'hz',
                            'motor': self._motors['hz'],
                            'enabled': True,
                            'scaling': -1.0,
                            'units': 'mm',
                            'hint': 'positive moves stamp up (away from sample)',
                            },
                            
                            {'name': 'yaw',
                            'motor': self._motors['yaw'],
                            'enabled': True,
                            'scaling': +1.0,
                            'units': 'deg',
                            'hint': 'positive rotates clockwise (in-plane (phi) rotation; LHR about +z-axis)',
                            },
                            {'name': 'pitch',
                            'motor': self._motors['pitch'],
                            'enabled': True,
                            'scaling': +1.0,
                            'units': 'deg',
                            'hint': 'positive rotates stamp-holder up (RHR about -y-axis)',
                            },
                            {'name': 'roll',
                            'motor': self._motors['roll'],
                            'enabled': True,
                            'scaling': +1.0,
                            'units': 'deg',
                            'hint': 'positive rotates near-side up (RHR about -x-axis)',
                            },
                            
                        ]     



    def posv(self, verbosity=0):
        #super().posv(verbosity=verbosity)
        
        # The stage axis is special with respect to velocity.
        # In particular, the hexapod has a single velocity, so all of its
        # axes (x, y, hz, yaw, pitch, roll) all have the same velocity.
        # We avoid repeat lookups of velocity by using 'x' as the store
        # for this common value.
        # (We treat 'z' separately since this is the Newport motor.)
        for axis_name, axis_object in sorted(self._axes.items()):
            if axis_object.last_change_timestamp>self._posv_cache_timestamp:
                self._posv_cache[axis_name+'__timestamp'] = axis_object.last_change_timestamp
                self._posv_cache[axis_name] = axis_object.get_position(verbosity=verbosity)
                if axis_name=='x' or axis_name=='z':
                    self._posv_cache[axis_name+'vel'] = axis_object.set_velocity(verbosity=verbosity)

        # We use xvel as the velocity for the entire hexapod (since they are all the same)
        self._posv_cache['vel'] = self._posv_cache['xvel']
        for axis_name, axis_object in sorted(self._axes.items()):
            if axis_name!='x' and axis_name!='z':
                self._posv_cache[axis_name+'vel'] = self._posv_cache['vel']

        self._posv_cache_timestamp = time.time()
        
        return self._posv_cache
            
    def rock(self, amount=1, velocity=None):
        if velocity is not None:
            self.rollvel(velocity)
        self.rollr(+amount)
        self.rollr(-2*amount)
        self.rollr(+amount)
        
    def hold(self):
        position = self._gripper_closed_position
        self.gripper.set_position(position)
        time.sleep(3)

    def release(self):
        position = self._gripper_open_position
        self.gripper.set_position(position)
        time.sleep(3)
            
            
    def _dev_goto(self, label, verbosity=3, **additional):
        '''Move the stage/sample to the location given by the label. For this
        to work, the specified label must have been 'marked' at some point.
        
        Additional keyword arguments can be provided. For instance, to move 
        3 mm from the left edge:
          sam.goto('left edge', xr=+3.0)
        '''
        
        # This over-rides the default version, accounting for the movement sequence
        # specific to StampStage
        
        if label not in self._marks:
            #if verbosity>=1:
                #print("Label '{:s}' not recognized. Use '.marks()' for the list of marked positions.".format(label))
            txt = "Label '{:s}' not recognized. Use '.marks()' for the list of marked positions.".format(label)
            self.msg_warning(txt, 1, verbosity=verbosity)
            return


        zcur = self._axes['z'].get_position(position+relative, verbosity=verbosity)
        hzcur = self._axes['hz'].get_position(position+relative, verbosity=verbosity)
        #axis_order = ['z', 'hz']
            
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
            
            
            
            
class StageClient(Base):
    '''This object is meant to stand-in for a Stage object.
    This version instead dispatches commands (method calls) to a 
    remote connection.'''
    
    def __init__(self, name='StageClient', command_client=None, use_cache=False, verbosity=3, log_verbosity=5, **kwargs):
        super().__init__(name=name, verbosity=verbosity, log_verbosity=log_verbosity, **kwargs)
        
        self.command_client = command_client
        
        self.use_cache = use_cache
        self.cache = {}
        self.cache_timing = 8 # s
        
        
    def __getattr__(self, name):
        '''Handle any undefined method calls.
        These calls will be sent as remote commands.'''
        
        if self.use_cache:
            suffix = '__cache'
            if name.endswith(suffix):
                name = name[:-len(suffix)]
                
                if name in self.cache:
                    elapsed = time.time()-self.cache[name]['time']
                    stale = (elapsed>self.cache_timing)
                    if self.cache[name]['valid'] and not stale:
                        # Only in this exceptional instance do we use the cache
                        # (The entry exists, is valid, and is not too old/stale)
                                        
                        def lookup_cache_method(*args, **kwargs):
                            '''We create on-the-fly a new method, so that this method
                            has access within its local scope to the name of the command.'''
                            return self.lookup_cache(name, *args, **kwargs)
                        
                        self.remote_command_name = name # No longer used
                        #return self.lookup_cache
                        return lookup_cache_method
            
            elif name.endswith('abs'):
                # These motor movements invalidate the cache
                cname = name[:-len('abs')]
                if cname in self.cache:
                    self.cache[cname]['valid'] = False
                if 'pos' in self.cache:
                    self.cache['pos']['valid'] = False
            elif name.endswith('r'):
                cname = name[:-len('r')]
                if cname in self.cache:
                    self.cache[cname]['valid'] = False
                if 'pos' in self.cache:
                    self.cache['pos']['valid'] = False
        
        
        def dispatch_connection_method(*args, **kwargs):
            '''We create on-the-fly a new method, so that this method
            has access within its local scope to the name of the command.'''
            return self.dispatch(name, *args, **kwargs)
        
        # By default, functions are packaged as a command and dispatched to the remote server
        self.remote_command_name = name # No longer used
        #return self.dispatch
        return dispatch_connection_method
    

        
    def dispatch(self, requested_command_name, *args, **kwargs):
        #cmd = self.remote_command_name # It is unreliable to use an internal variable in an async(callback) context
        cmd = requested_command_name
        
        # Package command
        command = {
            'system': self.name,
            'command': cmd,
            'args': args,
            'kwargs': kwargs
            }
        
        # Send command to server
        response = self.command_client.client_send(command)
        
        if self.use_cache:
            self.msg('Updating cache {}.{}() = {}'.format(self.name, cmd, response['return_value']), 6, 3)
            
            # Update cache
            self.cache[cmd] = {
                'value': response['return_value'],
                'time': time.time(),
                'valid': True,
                }

        
        #if cmd!=self.remote_command_name:
            #self.msg('FYI: dispatch command inconsistency: cmd={}, self.rcn={}'.format(cmd, self.remote_command_name), 4, 0)
        
        return response['return_value']
    
    def lookup_cache(self, requested_command_name, *args, **kwargs):
        #cmd = self.remote_command_name # It is unreliable to use an internal variable in an async(callback) context
        cmd = requested_command_name
        return_value = self.cache[cmd]['value']
        self.msg('Using cached {}.{}() = {}'.format(self.name, cmd, return_value), 6, 3)
        return return_value
    
    
    



class CommandClientServer(Base):
    '''Provides a means for a simple client and server object to
    communicate with each other. Zero Message Queue (ZMQ) is used to
    transfer Python dictionaries. The dictionary is interpreted as
    a request to run one of the class methods of the Server.'''
    
    def __init__(self, authentication_token, name='CommandClientServer', log_verbosity=5, **kwargs):
        # authentication_token - a string
        # NOTE: This authentication token is meant to provide only minimal security.
        # The token is exchanged unencrypted, and is stored in readable source
        # code files. The main purpose of the token is to prevent processing of 
        # unintentional and malformed commands.
        #  If real security is needed, a proper authentication mechanism should
        # be used instead.
        
        super().__init__(name=name, log_verbosity=log_verbosity, **kwargs)
    
    
    def server_listen(self, ip='127.0.0.1', port=5551):
        '''Start ZMQ server. Listen for commands and process each one.'''
        
        if self.mode!='server':
            self.msg_error("server_listen was called, but {} has mode='{}' ".format(self.__class__.__name__, self.mode))
        self.mode = 'server'
        
        self.ip, self.port = ip, port
        self.context = zmq.Context()

        # Act as a "server", receiving commands
        self.msg('Starting queue (server)', 3, 1)
        self.msg('IP: {}, port: {}'.format(ip, port), 3, 2)
        success, attempt, start_time = False, 0, time.time()
        while not success:
            attempt += 1
            try:
                self.server_socket = self.context.socket(zmq.REP)
                self.server_socket.bind("tcp://{}:{:d}".format(ip, port))
                success = True
                self.msg('Success (attempt {:d}, {:.1f} s)'.format(attempt, time.time()-start_time), 3, 2)
            except zmq.error.ZMQError:
                self.msg('Retrying (attempt {:d}, {:.1f} s)'.format(attempt, time.time()-start_time), 3, 2)
                time.sleep(1)
                
                
        while True: # Run forever
            #  Wait for next request from client
            self.msg('Waiting for command ({})...'.format(self.now()), 4, 1)
            
            command = self.server_socket.recv_pyobj()
            
            args_str = ', '.join([str(a) for a in command['args']])
            kwargs_str = ''.join(['{}={}, '.format(key, value) for key, value in command['kwargs'].items()])
            command_str = '{}.{}({}, {})'.format(command['system'], command['command'], args_str, kwargs_str)
            self.msg('Received command (from {}): {}'.format(command['sender'], command_str), 4, 2)
            
            
            response = self.server_process_command(command)
            
            self.server_socket.send_pyobj(response)
            
    
    def server_process_command(self, command):
        
        if 'auth' not in command or command['auth']!=self.authentication_token:
            return {'status': 'failed', 'reason': 'Authentication required.'}

        if 'system' not in command:
            return {'status': 'failed', 'reason': 'System not specified.'}

        if 'command' not in command:
            return {'status': 'failed', 'reason': 'Command not specified.'}

        if self._common is not None:
            self._common.accumulate_msgs()
            
        try:
            system = getattr(self, command['system'])
            function = getattr(system, command['command'])
            return_value = function(*command['args'], **command['kwargs'])
            response = {'status': 'success', 'return_value': return_value}
        
        except Exception as e:
            response = {'status': 'failed', 'reason': 'Python exception', 'exception': '{}'.format(e), 'return_value': None}
            
        if self._common is not None:
            response['msgs'] = self._common.get_accumulated_msgs()
        
            
        return response



    def client_connect_to_server(self, ip='127.0.0.1', port=5551):
        '''Connect to server ZMQ. Use this port to send commands.'''
        
        if self.mode!='client':
            self.msg_error("client_connect_to_server was called, but {} has mode='{}' ".format(self.__class__.__name__, self.mode))
        self.mode = 'client'
        
        self.ip, self.port = ip, port
        self.context = zmq.Context()
        
        # Act as a "client", sending commands
        self.msg('Starting queue (client)', 3, 1)
        self.msg('IP: {}, port: {}'.format(ip, port), 3, 2)
        success, attempt, start_time = False, 0, time.time()
        while not success:
            attempt += 1
            try:
                self.client_socket = self.context.socket(zmq.REQ)
                self.client_socket.connect("tcp://{}:{:d}".format(ip, port))
                success = True
                self.msg('Connected to server (attempt {:d}, {:.1f} s)'.format(attempt, time.time()-start_time), 3, 2)
            except zmq.error.ZMQError:
                self.msg('Waiting for server (attempt {:d}, {:.1f} s)'.format(attempt, time.time()-start_time), 3, 2)
                time.sleep(1)        

        
    def client_send(self, command, print_remote_msgs=True, sleep_time=0.25):
        
        args_str = ', '.join([str(a) for a in command['args']])
        kwargs_str = ''.join(['{}={}, '.format(key, value) for key, value in command['kwargs'].items()])
        command_str = '{}.{}({}, {})'.format(command['system'], command['command'], args_str, kwargs_str)
        
        command['auth'] = self.authentication_token
        command['sender'] = self.name
        
        self.msg('Command: {}'.format(command_str), 5, 1)
        
        
        success, attempt, start_time = False, 0, time.time()
        while not success and attempt<600:
            try:
                self.client_socket.send_pyobj(command)
                response = self.client_socket.recv_pyobj()
                success = True
            except zmq.error.ZMQError as e:
                self.msg('Waiting for client_send (attempt {:d}, {:.1f} s)'.format(attempt, time.time()-start_time), 3, 2)
                if attempt>=10:
                    sleep_time = 1
                elif attempt>=4:
                    sleep_time = 0.5
                time.sleep(sleep_time)
            attempt += 1
        
        
        self.msg('command {} complete (status: {})'.format(command_str, response['status']), 5, 2)
        self.msg('response: {}'.format(response), 6, 3)
        if response['status']=='failed':
            self.msg_warning('Command failed with reason: {}'.format(response['reason']), 1)
            if 'exception' in response:
                self.msg_warning('Python exception:: {}'.format(response['exception']), 1)
            
            
        if print_remote_msgs:
            for msg in response['msgs']:
                self.print(msg)
            
        return response

    def close(self):
        self.client_socket.close()

    #def print(self, txt, **kwargs):
        #print('Special!')
        #super().print(txt, **kwargs)
        




class Stacker(CommandClientServer):
    
    def __init__(self, authentication_token, name='Stacker', mode='local', verbosity=3, log_verbosity=5, connect_PI=True, connect_Instec=True, **kwargs):
        super().__init__(authentication_token=authentication_token, name=name, verbosity=verbosity, log_verbosity=log_verbosity, **kwargs)
        
        
        self.mode = mode
        self.authentication_token = authentication_token
        
        if mode=='client':
            self.sam = StageClient(name='sam', command_client=self, common=self._common, verbosity=verbosity, log_verbosity=log_verbosity)
            self.cam = StageClient(name='cam', command_client=self, common=self._common, verbosity=verbosity, log_verbosity=log_verbosity)
            self.stmp = StageClient(name='stmp', command_client=self, common=self._common, verbosity=verbosity, log_verbosity=log_verbosity)
            
            
        elif mode=='testing':
            motors = {
                'x': MotorDummy(name='xmotor'),
                'y': MotorDummy(name='ymotor'),
                'phi': MotorDummy(name='phimotor'),
                'T': MotorDummy(name='Tcontrol'),
                }
            self.sam = SampleStage(name='sam', common=self._common, motors=motors, connect_Xeryon=False, connect_Instec=False, verbosity=verbosity, log_verbosity=log_verbosity)
            motors = {'z': MotorDummy(name='zmotor')}
            self.cam = CameraStage(name='cam', common=self._common, motors=motors, verbosity=verbosity, log_verbosity=log_verbosity)
            motors = {
                'x': MotorDummy(name='hex_x'),
                'y': MotorDummy(name='hex_y'),
                'hz': MotorDummy(name='hex_z'),
                'z': MotorDummy(name='stmp_zmotor'),
                'yaw': MotorDummy(name='hex_yaw'),
                'pitch': MotorDummy(name='hex_pitch'),
                'roll': MotorDummy(name='hex_roll'),
                }            
            self.stmp = StampStage(name='stmp', common=self._common, motors=motors, connect_Thorlabs=False, verbosity=verbosity, log_verbosity=log_verbosity)
            
        else:
            
            # Controllers
            from Devices.Newport import ControllerNewport, MotorNewport
            self.controllerNewport = ControllerNewport('controllerNewport', serial_device="COM4", common=self._common, verbosity=verbosity, log_verbosity=log_verbosity)
            
            
            if connect_PI:
                from Devices.PI import MotorPI_Linear, ControllerPI_Hexapod
                self.controllerPI_Hexapod = ControllerPI_Hexapod(controller_name='C-887', IP='130.199.242.254', port=50000, name='hexapod', verbosity=verbosity, log_verbosity=log_verbosity)
                
                
                sam_x = MotorPI_Linear(SN='120054604', name='sam_xmotor', common=self._common, verbosity=verbosity, log_verbosity=log_verbosity)
                sam_y = MotorPI_Linear(SN='120060377', name='sam_ymotor', common=self._common, verbosity=verbosity, log_verbosity=log_verbosity)
                
                hex_x = self.controllerPI_Hexapod.Z
                hex_y = self.controllerPI_Hexapod.Y
                hex_z = self.controllerPI_Hexapod.X
                hex_yaw = self.controllerPI_Hexapod.U
                hex_pitch = self.controllerPI_Hexapod.V
                hex_roll = self.controllerPI_Hexapod.W
                
                
            else:
                # We can't connect to the actual PI system
                # Use dummy motors instead
                sam_x = MotorDummy(name='sam_x')
                sam_y = MotorDummy(name='sam_y')
                hex_x = MotorDummy(name='hex_x')
                hex_y = MotorDummy(name='hex_y')
                hex_z = MotorDummy(name='hex_z')
                hex_yaw = MotorDummy(name='hex_yaw')
                hex_pitch = MotorDummy(name='hex_pitch')
                hex_roll = MotorDummy(name='hex_roll')
            
            
            # Sample
            motors = {
                'x': sam_x,
                'y': sam_y,
                'phi': MotorNewport(self.controllerNewport, 2, name='sam_phimotor', common=self._common, verbosity=verbosity, log_verbosity=log_verbosity),
                }
            self.sam = SampleStage(name='sam', common=self._common, motors=motors, connect_Instec=connect_Instec, verbosity=verbosity, log_verbosity=log_verbosity)
            
            # Camera
            motors = {
                'z': MotorNewport(self.controllerNewport, 1, name='cam_zmotor', common=self._common, verbosity=verbosity, log_verbosity=log_verbosity),
                }
            self.cam = CameraStage(name='cam', common=self._common, motors=motors, verbosity=verbosity, log_verbosity=log_verbosity)

            # Stamp
            motors = {
                'x': hex_x,
                'y': hex_y,
                'hz': hex_z,
                'z': MotorNewport(self.controllerNewport, 3, name='stmp_zmotor', common=self._common, verbosity=verbosity, log_verbosity=log_verbosity),
                'yaw': hex_yaw,
                'pitch': hex_pitch,
                'roll': hex_roll,
                }
            self.stmp = StampStage(name='stmp', common=self._common, motors=motors, verbosity=verbosity, log_verbosity=log_verbosity)
            


    def pos(self, force_update=False, verbosity=0):
        
        ret = {}
        ret['cam'] = self.cam.posv(verbosity=verbosity)
        ret['stmp'] = self.stmp.posv(verbosity=verbosity)
        ret['sam'] = self.sam.posv(verbosity=verbosity)
        
        return ret

            
    def demo(self, iterations=1, stmp=False, sam=False, cam=False):
        '''Run a simple demonstration of the different motions the system can perform.'''
        
        for i in range(iterations):
            self.msg('Running demo iteration {:d}'.format(i))

            if stmp:
                self.stmp.zr(+4)
                self.stmp.zr(-4)
                self.stmp.xr(+2)
                self.stmp.xr(-4)
                self.stmp.xr(+2)
                self.stmp.yr(+2)
                self.stmp.yr(-4)
                self.stmp.yr(+2)
                
                self.stmp.rollr(+2)
                self.stmp.rollr(-4)
                self.stmp.rollr(+2)

                #self.stmp.yawr(+2)
                #self.stmp.yawr(-4)
                #self.stmp.yawr(+2)

                self.stmp.pitchr(+3)
                self.stmp.pitchr(-3)
                
            
            if sam:
                self.sam.xr(+5)
                self.sam.xr(-5)
                self.sam.yr(+5)
                self.sam.yr(-5)
                
                self.sam.phir(+8)
                self.sam.phir(-16)
                self.sam.phir(+8)
            
            if cam:
                self.cam.zr(+5)
                self.cam.zr(-5)
        
        
        
        




