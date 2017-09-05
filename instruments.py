# -*- coding: utf-8 -*-

import numpy as np
import visa
import time
import tools.FileTools as FT
import tools.PromptTools as PT


class SimVISA(object):
    '''
    Emulator for test with VISA.

    Replaces write and query functions with prompts in console.
    Only for algorithm testing.
    '''

    def __init__(self):
        print('VISA simulation enabled')

    def write(self, command):
        # Print command in console
        print(">> " + command)

    def query(self, command, separator=''):
        # Print command and request simulated answer
        print(">> " + command)
        return input("Answer: ")

    def query_ascii_values(self, command, **args):
        # Print command and generate random curve
        print(">> " + command)
        return np.random.rand(100), np.random.rand(100), 0, 0


class Instrument(object):
    def __init__(self, resource=None, sim_mode=False, backend="@py",
                 query='?*::INSTR', name=None, path='../'):

        if sim_mode:
            # Create a simulated instrument
            self._resource = 'SimVISA'
            self._inst = SimVISA()

        else:
            # Help to find resource
            if resource is None:
                rm = visa.ResourceManager(backend)
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
            self._name = self._inst.query('*IDN?', log=False)

        self._fullname = '%s/%.16s' % (self._path, self._name)
        self._log = '%s.log' % self._fullname

        with open(self._log, 'a') as f:
            f.write('#' * 40 + '\n')
            f.write('# %-36s #\n' % time.strftime('%x - %X'))
            f.write('#' * 40 + '\n')

    def __del__(self):
        self._inst.close()

    def write(self, command, termination=None, encoding=None, log=True):
        self._inst.write(command, termination, encoding)
        if log:
            with open(self._log, 'a') as f:
                f.write(time.strftime('%X') + ">> " + command + '\n')

    def query(self, command, delay=None, log=True):
        answer = self._inst.query(command, delay)
        if log:
            with open(self._log, 'a') as f:
                f.write(time.strftime('%X') + ">> " + command + '\n')
                f.write(" " * 8 + answer + '\n')
        return answer

    def query_ascii_values(self, command, converter='f', separator=',',
                           container=list, delay=None, log=True):
        answer = self._inst.query_ascii_values(command, converter,
                                               separator, container,
                                               delay)
        if log:
            with open(self._log, 'a') as f:
                f.write(time.strftime('%X') + ">> " + command + '\n')
                f.write(" " * 8 + answer + '\n')
        return answer

    def save(self, data, fullname='../data/temp/temp.npy', verbose=False):


class CommandGroup(object):
    def __init__(self, instrument):
        self._inst = instrument


class Oscilloscope(Instrument):
    def __init__(self, resource=None, sim_mode=False, backend="@py",
                 query='?*::INSTR', name=None, path='../'):

        Instrument.__init__(resource, sim_mode, backend, query, name, path)

    def config_curve(self, mode='RPB', width=1, start=1, stop=2500):
        self._inst.write('DAT:ENC %s' % mode)
        self._inst.write('DAT:WID %d' % width)
        self._inst.write('DAT:STAR %d' % start)
        self._inst.write('DAT:STOP %d' % stop)

    def config(self):
        self._inst.write('ACQ:MOD SAMP')


class ITC4001(Instrument):
    def __init__(self, resource=None, sim_mode=False, backend="@py",
                 query='?*::INSTR', name=None, path='../'):

        Instrument.__init__(resource, sim_mode, backend, query, name, path)
