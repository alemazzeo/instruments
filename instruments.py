# -*- coding: utf-8 -*-

import numpy as np
import visa
import time
from tools import FileTools as FT
from tools import PromptTools as PT
from tools import LogTools as LT

MAX_LOG_ANSWERS = 10


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
            return "Simulated VISA Device, SimVISA"
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
                 query='?*::INSTR', name=None, path='./'):

        if sim_mode:
            # Create a simulated instrument
            self._resource = 'SimVISA'
            self._inst = SimVISA()

        else:
            rm = visa.ResourceManager(backend)
            # Help to find resource
            if resource is None:

                available = rm.list_resources(query=query)

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
                        option = '%s' % item
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

        self._idn = self._inst.query('*IDN?')
        self._name = self._idn.split(',')[0] + '-' + self._idn.split(',')[1]

        self._fullname = '%s/%s' % (path, self._name)
        self._path = path
        self._path_data = path + '/data/temp.npy'

        self._log = LT('%{}.log'.format(self._fullname))
        self._temp_list = list()

        self._log.block(time.strftime('%x - %X'),
                        'Session started',
                        self._resource,
                        self._name)

    def __del__(self):
        self._log.block(time.strftime('%x - %X'),
                        'Session closed')
        self._inst.close()

    def write(self, command, termination=None, encoding=None, log=True):
        self._inst.write(command, termination, encoding)
        if log:
            self._log.time_stamp(command)

    def query(self, command, delay=None, log=True):
        answer = self._inst.query(command, delay)
        if log:
            self._log.time_stamp(command, answer)
        return answer

    def query_ascii_values(self, command, converter='f', separator=',',
                           container=list, delay=None, log=True):
        answer = self._inst.query_ascii_values(command, converter,
                                               separator, container,
                                               delay)
        if log:
            if len(answer) < MAX_LOG_ANSWERS:
                for value in answer:
                    self._log.time_selftamp(answer=value)
            else:
                save = self.save(answer)
                self._log.time_stamp(command, answer=save)
        return answer

    def query_binary_values(self, command, datatype='f', is_big_endian=False,
                            container=list, delay=None, header_fmt='ieee',
                            log=True):

        answer = self._inst.query_binary_values(command, datatype,
                                                is_big_endian, container,
                                                delay, header_fmt)
        if log:
            save = self.save(answer)
            self._log.time_stamp(command, answer=save)
        return answer

    def save(self, data, fullname='temp.npy'):
        fullname = FT.newname(fullname, default=self._path_data)
        np.save(fullname, data)
        self._temp_list.append(fullname)
        return fullname

    def load(self, fullname='temp.npy'):
        fullname = FT.file_exist(fullname, default_path=self._path_data)
        return np.load(fullname)


class CommandGroup():
    def __init__(self, instrument):
        self._inst = instrument


class Oscilloscope(Instrument):
    def __init__(self, resource=None, sim_mode=False, backend="@py",
                 query='?*::INSTR', name=None, path='./'):

        Instrument.__init__(self, resource, sim_mode,
                            backend, query, name, path)

        self._xze = None
        self._xin = None
        self._yze = None
        self._ymu = None
        self._yoff = None

        self.setup_curve()
        self.get_waveform_preamble()

    def setup_curve(self, source='CH1', mode='RPB',
                    width=1, start=1, stop=2500):

        self._inst.write('DATa:SOUrce {}'.format(source))
        self._inst.write('DATa:ENC {}'.format(mode))
        self._inst.write('DATa:WIDth {}'.format(width))
        self._inst.write('DATa:STARt {}'.format(start))
        self._inst.write('DATa:STOP {}'.format(stop))

    def get_waveform_preamble(self, log=False):
        query = 'WFMPRE:XZE?;XIN?;YZE?;YMU?;YOFF?;'
        answer = self.query_ascii_values(query, separator=';', log=log)
        self._xze = answer[0]
        self._xin = answer[1]
        self._yze = answer[2]
        self._ymu = answer[3]
        self._yoff = answer[4]

    def get_curve(self, auto_wfmpre=True, log=True):
        if auto_wfmpre:
            self.get_waveform_preamble(log=log)

        y = self._inst.query_binary_values('CURV?', datatype='B',
                                           container=np.array)
        y = (y - self._yoff) * self._ymu + self._yze
        x = self._xze + np.arange(len(y)) * self._xin

        if log:
            save = self.save([x, y])
            self._log.time_stamp('CURV?', answer=save)

        return x, y


class ITC4001(Instrument):
    def __init__(self, resource=None, sim_mode=False, backend="@py",
                 query='?*::INSTR', name=None, path='./'):

        Instrument.__init__(self, resource, sim_mode,
                            backend, query, name, path)

    def measurement(self, scalar='TEMP', log=True):
        self.query('MEAS:{}'.format(scalar), log=log)

    def current_setpoint(self, current, log=True):
        self.write('SOUR:CURR {}'.format(current))

    def temperature_setpoint(self, temp, log=True):
        self.write('SOUR2:TEMP {}c'.format(temp))

    def sweep_temp(self, Ti=22.5, Tf=23.5, dT=0.01, dtime=4,
                   func=None, func_args=None):

        n = int((Tf - Ti) / dT)
        dT = dT * np.sign(Tf - Ti)
        T = np.zeros(n, dtype=float)
        t = np.zeros(n, dtype=float)

        self._inst.write('SOUR2:TEMP {}'.format(Ti))

        for i in range(n):
            t[i] = time.time()
            T[i] = self._inst('MEAS:TEMP?')

            if func is not None:
                func(i, *func_args)

            time.delay(dtime)
            self._inst.write('SOUR2:TEMP {}'.format(Ti + i * dT))

        t = t - t[0]

        return t, T
