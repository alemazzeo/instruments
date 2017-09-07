# -*- coding: utf-8 -*-

import numpy as np
import visa
import time
from tools import FileTools as FT
from tools import PromptTools as PT

import matplotlib.pyplot as plt


class SimVISA(object):
    '''
    Emulator for test with VISA.

    Replaces write and query functions with prompts in console.
    Only for algorithm testing.
    '''

    def __init__(self):
        print('VISA simulation enabled')

    def write(self, command, termination=None, encoding=None):
        # Print command in console
        print(">> " + command)

    def query(self, command, separator=''):
        # Print command and request simulated answer
        print(">> " + command)
        if command == '*IDN?':
            return "Simulated VISA Device"
        else:
            return input("Answer: ")

    def query_ascii_values(self, command, **args):
        # Print command and generate random curve
        print(">> " + command)
        return np.random.rand(100), np.random.rand(100), 0, 0

    def close(*args, **kwargs):
        pass


class Instrument():
    def __init__(self, resource=None, sim_mode=False, backend="@py",
                 query='?*::INSTR', name=None, 
                 path='D:/ALUMNOS/Grupo 1/Espectro Rb'):

        if sim_mode:
            # Create a simulated instrument
            self._resource = 'SimVISA'
            self._inst = SimVISA()

        else:
            rm = visa.ResourceManager(backend)
            # Help to find resource
            if resource is None:
                
                available = rm.list_resources_info(query=query)

                # Filter results with the (optional) name provided
                if name is not None:
                    available = {k: v for k, v in available.items()
                                 if v.resource_name == name}

                # Generate a list with results
                if len(available) >= 1:
                    resources = list()
                    options = list()
                    for i, item in enumerate(available):
                        resources.append(item)
                        rsc_name = available[item].resource_name
                        option = '%s\n    (%s)' % (item, rsc_name)
                        options.append(option)

                    # Make a list for multiples values
                    if len(available) > 1:
                        message = "Available devices:\n"
                        number = PT.select_prompt(options, message)
                        self._resource = resources[number]

                    # Or autoselect
                    else:
                        self._resource = resources[0]

                # Raise exception for negative query results
                else:
                    raise(visa.VisaIOError(-1073807343))

            # Use the resource selected
            else:
                self._resource = resource

            # Open resource
            self._inst = rm.open_resource(self._resource)

        self._name = self._inst.query('*IDN?')

        self._fullname = '%s/%.16s' % (path, self._name)
        self._path = path

        self._log = '%s.log' % self._fullname
        self._temp_list = list()

        with open(self._log, 'a') as f:
            f.write('\n' + '#' * 40 + '\n')
            f.write('# %-36s #\n' % time.strftime('%x - %X'))
            f.write('# %-36s #\n' % 'Session started')
            f.write('# %-36s #\n' % self._resource)
            f.write('# %-36s #\n' % self._name)
            f.write('#' * 40 + '\n')

    def __del__(self):
        with open(self._log, 'a') as f:
            f.write('\n' + '#' * 40 + '\n')
            f.write('# %-36s #\n' % time.strftime('%x - %X'))
            f.write('# %-36s #\n' % 'Session closed')
            f.write('#' * 40 + '\n')
        self._inst.close()

    def write(self, command, termination=None, encoding=None, log=True):
        self._inst.write(command, termination, encoding)
        if log:
            with open(self._log, 'a') as f:
                f.write(time.strftime('%X') + " >> " + command + '\n')

    def query(self, command, delay=None, log=True):
        answer = self._inst.query(command, delay)
        if log:
            with open(self._log, 'a') as f:
                f.write(time.strftime('%X') + " >> " + command + '\n')
                f.write(' ' * 8 + ' << ' + answer + '\n')
        return answer

    def query_ascii_values(self, command, converter='f', separator=',',
                           container=list, delay=None, log=True):
        answer = self._inst.query_ascii_values(command, converter,
                                               separator, container,
                                               delay)
        if log:
            with open(self._log, 'a') as f:
                f.write(time.strftime('%X') + " >> " + command + '\n')
                f.write(" " * 8 + answer + '\n')
        return answer

    def save(self, data, fullname='../data/temp/temp.npy', log=True):
        fullname = FT.newname(fullname)
        np.save(fullname, data)
        self._temp_list.append(fullname)
        if log:
            with open(self._log, 'a') as f:
                f.write(time.strftime('%X') + " <> SAVED: " + fullname + '\n')

    def load(self, fullname='../data/temp/temp.npy', log=True):
        return np.load(fullname)


class CommandGroup():
    def __init__(self, instrument):
        self._inst = instrument


class Oscilloscope(Instrument):
    def __init__(self, resource=None, sim_mode=False, backend="@py",
                 query='?*::INSTR', name=None, 
                 path='D:/ALUMNOS/Grupo 1/Espectro Rb'):

        Instrument.__init__(self, resource, sim_mode, 
                            backend, query, name, path)
        
        self._xze = None
        self._xin = None
        self._yze = None
        self._ymu = None
        self._yoff = None
        
        self.config_curve()

    def config_curve(self, canal=1, mode='RPB', width=1, start=1, stop=2500):
        self._inst.write('DAT:SOU CH%d' % canal)
        self._inst.write('DAT:ENC %s' % mode)
        self._inst.write('DAT:WID %d' % width)
        self._inst.write('DAT:STAR %d' % start)
        self._inst.write('DAT:STOP %d' % stop)
        query = 'WFMPRE:XZE?;XIN?;YZE?;YMU?;YOFF?;'
        xze, xin, yze, ymu, yoff = self._inst.query_ascii_values(query, 
                                                                 separator=';')
        self._xze = xze
        self._xin = xin
        self._yze = yze
        self._ymu = ymu
        self._yoff = yoff      

    def config_acq(self):
        self._inst.write('ACQ:MOD SAMP')
        
    def get_curve(self):
        data = self._inst.query_binary_values('CURV?', datatype='B', 
                                               container=np.array) 
        data = (data - self._yoff) * self._ymu + self._yze
        time = self._xze + np.arange(len(data)) * self._xin
        
        return data, time
        


class ITC4001(Instrument):
    def __init__(self, resource=None, sim_mode=False, backend="@py",
                 query='?*::INSTR', name=None,
                 path='D:/ALUMNOS/Grupo 1/Espectro Rb'):

        Instrument.__init__(self, resource, sim_mode, backend, query, name, 
                            path)
    
    # Cambiar idioma
    def medir(self, cantidad='TEMP', n=10000, ax=None, **kwargs):
        Temp = np.zeros(n, dtype=float)
        Tiempo = np.zeros(n, dtype=float)
        for i in range(n):
            Tiempo[i] = time.time()    
            Temp[i] = self.query('MEAS:%4s?' % cantidad, log=False)
            
        Tiempo = Tiempo - Tiempo[0]
        
        if ax is None:
            fig, ax = plt.subplots(1)
            
        ax.plot(Tiempo, Temp, **kwargs)
        return Tiempo, Temp
