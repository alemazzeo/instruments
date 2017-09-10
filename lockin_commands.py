# -*- coding: utf-8 -*-

import time
from instruments import CommandGroup


class _lockin_reference(CommandGroup):

    def __init__(self, inst):
        CommandGroup.__init__(inst)

        self._crefMode = ('External', 'Internal')
        self._crefRslp = ('Sine', 'TTL Rising', 'TTL Falling')

    def _get_refPhase(self):
        return float(self._inst.query('PHAS?'))

    def _set_refPhase(self, value):
        f = self._option_limited(value, vmin=-360.00, vmax=729.99, prec=2)
        self._inst.write('PHAS{0:f}'.format(f))

    def _get_refMode(self):
        return self._crefMode[int(self._inst.query('FMOD?'))]

    def _set_refMode(self, value):
        i = self._option_list(value, self._crefMode)
        self._inst.write('FMOD{0}'.format(i))

    def _get_refFreq(self):
        return float(self._inst.query('FREQ?'))

    def _set_refFreq(self, value):
        f = self._option_limited(value, vmin=0.001, vmax=102000, prec=3)
        self._inst.write('FREQ{0:f}'.format(f))

    def _get_refAmpl(self):
        return float(self._inst.query('SLVL?'))

    def _set_refAmpl(self, value):
        f = self._option_limited(value, vmin=0.004, vmax=5.000, prec=3)
        self._inst.write('SLVL{0:f}'.format(f))

    def _get_refHarm(self):
        return int(self._inst.query('HARM?'))

    def _set_refHarm(self, value):
        freq = float(self._inst.query('FREQ?'))
        i = int(self._option_limited(value, vmin=1, vmax=19999, prec=0))
        try:
            self._option_limited(i * freq, vmin=0, vmax=102000.0, prec=4)
        except ValueError:
            raise ValueError('value * freq <= 102000Hz')
        self._inst.write('HARM{0}'.format(i))

    def _get_refRslp(self):
        return self._crefRslp[int(self._inst.query('RSLP?'))]

    def _set_refRslp(self, value):
        i = self._option_list(value, self._crefRslp)
        self._inst.write('RSLP{0}'.format(i))

    Phase = property(_get_refPhase, _set_refPhase)
    Mode = property(_get_refMode, _set_refMode)
    Frequency = property(_get_refFreq, _set_refFreq)
    Amplitude = property(_get_refAmpl, _set_refAmpl)
    Harmonic = property(_get_refHarm, _set_refHarm)
    ExternalTrigger = property(_get_refRslp, _set_refRslp)


class _lockin_input(CommandGroup):

    def __init__(self, inst):
        CommandGroup.__init__(inst)

        self._cinpMode = ('A', 'A-B', 'I1', 'I100')
        self._cinpGnd = ('Float', 'Ground')
        self._cinpCoup = ('AC', 'DC')
        self._cinpLine = ('Out', 'Line In', '2xLine In', 'Both In')

        self._cinpRmod = ('High Reserve', 'Normal', 'Low Noise')
        self._cinpOfsl = ('6dB/oct', '12dB/oct', '18dB/oct', '24dB/oct')
        self._cinpSync = ('Off', 'On')

        self._strinpSens = ('2 nV/fA', '5 nV/fA', '10 nV/fA',
                            '20 nV/fA', '50 nV/fA', '100 nV/fA',
                            '200 nV/fA', '500 nV/fA', '1 ¼V/pA',
                            '2 ¼V/pA', '5 ¼V/pA', '10 ¼V/pA',
                            '20 ¼V/pA', '50 ¼V/pA', '100 ¼V/pA',
                            '200 ¼V/pA', '500 ¼V/pA',  '1 mV/nA',
                            '2 mV/nA', '5 mV/nA', '10 mV/nA',
                            '20 mV/nA', '50 mV/nA', '100 mV/nA',
                            '200 mV/nA', '500 mV/nA', '1 V/¼A')

        self._floatinpSens = (2e-9, 5e-9, 10e-9, 20e-9, 50e-9,
                              100e-9, 200e-9, 500e-9, 1e-6, 2e-6,
                              5e-6, 10e-6, 20e-6, 50e-6, 100e-6,
                              200e-6, 500e-6, 1e-3, 2e-3, 5e-3,
                              10e-3, 20e-3, 50e-3, 100e-3, 200e-3,
                              500e-3, 1)

        self._strinpOflt = ('10 us',  '30 us', '100 us',
                            '300 us', '1 ms', '3 ms',
                            '10 ms', '30 ms', '100 ms',
                            '300 ms', '1 s', '3 s',
                            '10 s', '30 s', '100 s',
                            '300 s', '1 ks', '3 ks',
                            '10 ks', '30 ks')

        self._floatinpOflt = (10e-6, 30e-6, 100e-6, 300e-6,
                              1e-3, 3e-3, 10e-3, 30e-3,
                              100e-3, 300e-3, 1.0, 3.0,
                              10.0, 30.0, 100.0,  300.0,
                              1e3, 3e3, 10e3, 30e3)

    def _get_inpMode(self):
        return self._cinpMode[int(self._inst.query('ISRC?'))]

    def _set_inpMode(self, value):
        i = self._option_list(value, self._cinpMode)
        self._inst.write('ISRC{0}'.format(i))

    def _get_inpGnd(self):
        return self._cinpGnd[int(self._inst.query('IGND?'))]

    def _set_inpGnd(self, value):
        i = self._option_list(value, self._cinpGnd)
        self._inst.write('IGND{0}'.format(i))

    def _get_inpCoup(self):
        return self._cinpCoup[int(self._inst.query('ICPL?'))]

    def _set_inpCoup(self, value):
        i = self._option_list(value, self._cinpCoup)
        self._inst.write('ICPL{0}'.format(i))

    def _get_inpLine(self):
        return self._cinpLine[int(self._inst.query('ILIN?'))]

    def _set_inpLine(self, value):
        i = self._option_list(value, self._cinpLine)
        self._inst.write('ILIN{0}'.format(i))

    def _get_inpSens(self):
        return int(self._inst.query('SENS?'))

    def _set_inpSens(self, value):
        i = self._option_list(value, self._strinpSens, self._floatinpSens)
        self._inst.write('SENS{0}'.format(i))

    def _get_inpRmod(self):
        return self._cinpRmod[int(self._inst.query('RMOD?'))]

    def _set_inpRmod(self, value):
        i = self._option_list(value, self._cinpRmod)
        self._inst.write('RMOD{0}'.format(i))

    def _get_inpOflt(self):
        return int(self._inst.query('OFLT?'))

    def _set_inpOflt(self, value):
        i = self._option_list(value, self._strinpOflt, self._floatinpOflt)
        self._inst.write('OFLT{0}'.format(i))

    def _get_inpOfsl(self):
        return self._cinpOfsl[int(self._inst.query('OFSL?'))]

    def _set_inpOfsl(self, value):
        i = self._option_list(value, self._cinpOfsl)
        self._inst.write('OFSL{0}'.format(i))

    def _get_inpSync(self):
        return self._cinpSync[int(self._inst.query('SYNC?'))]

    def _set_inpSync(self, value):
        i = self._option_list(value, self._cinpSync)
        self._inst.write('SYNC{0}'.format(i))

    Input = property(_get_inpMode, _set_inpMode)
    Ground = property(_get_inpGnd, _set_inpGnd)
    Couple = property(_get_inpCoup, _set_inpCoup)
    Notch = property(_get_inpLine, _set_inpLine)

    Sensitivity = property(_get_inpSens, _set_inpSens)
    Reserve = property(_get_inpRmod, _set_inpRmod)
    TimeConstant = property(_get_inpOflt, _set_inpOflt)
    LowPassFilter = property(_get_inpOfsl, _set_inpOfsl)
    SyncFilter = property(_get_inpSync, _set_inpSync)


class _lockin_auxout(CommandGroup):

    def __init__(self, inst):
        CommandGroup.__init__(inst)

    def _get_auxout1(self):
        return float(self._inst.query('AUXV?1'))

    def _set_auxout1(self, value):
        f = self._option_limited(value, vmin=-10.500, vmax=10.500, prec=3)
        self._inst.write('AUXV1,{0:f}'.format(f))

    def _get_auxout2(self):
        return float(self._inst.query('AUXV?2'))

    def _set_auxout2(self, value):
        f = self._option_limited(value, vmin=-10.500, vmax=10.500, prec=3)
        self._inst.write('AUXV2,{0:f}'.format(f))

    def _get_auxout3(self):
        return float(self._inst.query('AUXV?3'))

    def _set_auxout3(self, value):
        f = self._option_limited(value, vmin=-10.500, vmax=10.500, prec=3)
        self._inst.write('AUXV3,{0:f}'.format(f))

    def _get_auxout4(self):
        return float(self._inst.query('AUXV?4'))

    def _set_auxout4(self, value):
        f = self._option_limited(value, vmin=-10.500, vmax=10.500, prec=3)
        self._inst.write('AUXV4,{0:f}'.format(f))

    AuxOut1 = property(_get_auxout1, _set_auxout1)
    AuxOut2 = property(_get_auxout2, _set_auxout2)
    AuxOut3 = property(_get_auxout3, _set_auxout3)
    AuxOut4 = property(_get_auxout4, _set_auxout4)


class _lockin_ch1(CommandGroup):

    def __init__(self, inst):
        CommandGroup.__init__(inst)

        self._cch1Mode = ('X', 'R', 'Xn', 'Aux1', 'Aux2')
        self._cch1RatS = ('None', 'Aux In 1', 'Aux In 2')
        self._cch1OutS = ('Display', 'X')
        self._cExpand = ('x1', 'x10', 'x100')

    def _get_ch1Mode(self):
        d, r = self._inst.query_ascii_values('DDEF? 1', separator=',')
        return self._cch1Mode[d]

    def _set_ch1Mode(self, value):
        d, r = self._inst.query_ascii_values('DDEF? 1', separator=',')
        d = self._option_list(value, self._cch1Mode)
        self._inst.write('DDEF? 1, {d}, {r}'.format(d=d, r=r))

    def _get_ch1RatS(self):
        d, r = self._inst.query_ascii_values('DDEF? 1', separator=',')
        return self._cch1Rats[r]

    def _set_ch1RatS(self, value):
        d, r = self._inst.query_ascii_values('DDEF? 1', separator=',')
        r = self._option_list(value, self._cch1Rats)
        self._inst.write('DDEF? 1, {d}, {r}'.format(d=d, r=r))

    Display = property(_get_ch1Mode, _set_ch1Mode)
    Ratio = property(_get_ch1RatS, _set_ch1RatS)
    # Output = property(_get_ch1OutS, _set_ch1OutS)
    # OffsetX = property(_get_offsetX, _set_offsetX)
    # OffsetY = property(_get_offsetY, _set_offsetY)
    # ExpandX = property(_get_expandX, _set_expandX)
    # ExpandY = property(_get_expandY, _set_expandY)


class _lockin_ch2(CommandGroup):

    def __init__(self, inst):
        CommandGroup.__init__(inst)

        self._cch2Mode = ('Y', 'T', 'Yn', 'Aux3', 'Aux4')
        self._cch2RatS = ('None', 'Aux In 3', 'Aux In 4')
        self._cch2OutS = ('Display', 'Y')
        self._cExpand = ('x1', 'x10', 'x100')

    def _get_ch2Mode(self):
        d, r = self._inst.query_ascii_values('DDEF? 2', separator=',')
        return self._cch2Mode[d]

    def _set_ch2Mode(self, value):
        d, r = self._inst.query_ascii_values('DDEF? 2', separator=',')
        d = self._option_list(value, self._cch1Mode)
        self._inst.write('DDEF? 1, {d}, {r}'.format(d=d, r=r))

    def _get_ch2RatS(self):
        d, r = self._inst.query_ascii_values('DDEF? 2', separator=',')
        return self._cch2Rats[r]

    def _set_ch2RatS(self, value):
        d, r = self._inst.query_ascii_values('DDEF? 2', separator=',')
        r = self._option_list(value, self._cch1Rats)
        self._inst.write('DDEF? 1, {d}, {r}'.format(d=d, r=r))

    Display = property(_get_ch2Mode, _set_ch2Mode)
    Ratio = property(_get_ch2RatS, _set_ch2RatS)
    # Output = property(_get_ch2OutS, _set_ch2OutS)
    # OffsetR = property(_get_offsetR, _set_offsetR)
    # ExpandR = property(_get_expandR, _set_expandR)


class _lockin_interface(CommandGroup):

    def __init__(self, inst):
        CommandGroup.__init__(inst)

        self._cstpLock = ('Local', 'Remote', 'Local Lockout')

    def _get_stpLock(self):
        return self._cstpLock[int(self._inst.query('LOCL?'))]

    def _set_stpLock(self, value):
        i = self._option_list(value, self._cstpLock)
        self._inst.write('LOCL{0}'.format(i))

    Lock = property(_get_stpLock, _set_stpLock)


class _lockin_autofuncs(CommandGroup):

    def __init__(self, inst):
        CommandGroup.__init__(inst)

    def autoGanacia(self):
        """ Ejecuta la funcion AutoGanancia del Lockin """
        self._inst.write('AGAN')
        print('Ejecutando autoGanancia... ', end='')
        while not bool(self._inst.query('*STB?1')):
            pass
        print('Finalizado')

    def autoReserva(self):
        """ Ejecuta la funcion AutoReserva del Lockin """
        self._inst.write('ARSV')
        print('Ejecutando autoReserva... ', end='')
        while not bool(self._inst.query('*STB?1')):
            pass
        print('Finalizado')

    def autoPhase(self):
        """ Ejecuta la funcion AutoPhase del Lockin """
        self._inst.write('APHS')
        print('Ejecutando autoPhase... ', end='')
        time.sleep(2)
        print('Finalizado')

    def autoOffset(self, num):
        """
        Ejecuta la funcion AutoGanancia del Lockin
        """
        if not (num == 1 or num == 2 or num == 3):
            raise ValueError('X(1), Y(2), R(3)')
        self._inst.write('AOFF{0}'.format(num))
        print('Ejecutando autoOffset... ', end='')
        time.sleep(2)
        print('Finalizado')


class _lockin_setup(CommandGroup):

    def __init__(self, inst):
        CommandGroup.__init__(inst)

    def configGuardar(self, ranura=1):
        """ Guarda la configuración en la ranura indicada (1 a 9) """
        if not (isinstance(ranura, int) and 1 <= ranura <= 9):
            raise ValueError('Ranuras válidas del 1 al 9')
        self._inst.write('SSET{0}'.format(ranura))
        print('Configuración guardada en la ranura ' + str(ranura))

    def configCargar(self, ranura=1):
        """ Carga la configuración desde la ranura indicada (1 a 9) """
        if not (isinstance(ranura, int) and 1 <= ranura <= 9):
            raise ValueError('Ranuras válidas del 1 al 9')
        self._inst.write('RSET{0}'.format(ranura))
        print('Configuración recuperada de la ranura ' + str(ranura))
