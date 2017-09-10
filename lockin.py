# -*- coding: utf-8 -*-

import time
import numpy as np

from instruments import Instrument

from lockin_commands import _lockin_autofuncs
from lockin_commands import _lockin_auxout
from lockin_commands import _lockin_ch1
from lockin_commands import _lockin_ch2
from lockin_commands import _lockin_input
from lockin_commands import _lockin_interface
from lockin_commands import _lockin_reference
from lockin_commands import _lockin_setup


class Lockin(Instrument):
    '''
    Clase para el manejo amplificador Lockin SR830 usando PyVISA de interfaz.
    '''

    def __init__(self, resource=None, sim_mode=False, backend="@py",
                 query='?*::INSTR', name=None, path='./'):

        Instrument.__init__(self, resource, sim_mode,
                            backend, query, name, path)

        self.input_panel = _lockin_input(self._inst)
        self.ch1_panel = _lockin_ch1(self._inst)
        self.ch2_panel = _lockin_ch2(self._inst)
        self.auto_panel = _lockin_autofuncs(self._inst)
        self.setup_panel = _lockin_setup(self._inst)
        self.interface_panel = _lockin_interface(self._inst)
        self.reference_panel = _lockin_reference(self._inst)
        self.auxiliar_outs = _lockin_auxout(self._inst)

        # Bloquea el uso de las teclas del Lockin
        self._inst.write('LOCL2')
        self._inst.write('OVRM0')

        self._buffer_size = 16383

    #----------------------------------------------------------------------
    # Listado y almacenamiento de propiedades en la pc
    #----------------------------------------------------------------------

    def listarPropiedades(self, impr=print, nL=''):
        """ 
        Lista las propiedes del Lockin 

        Parámetros:
        ----------
        impr : function
            Función utilizada para imprimir. Por defecto utiliza el comando
            print pero en principio es posible utilizar la función write
            correspondiente a un archivo u otra similar.
        nL : str
            Cadena correspondiente al salto de línea. La función print tiene
            por defecto el fin de línea adecuado. Sin embargo la función
            write para la escritura de archivos requiere este parámetro.
        """

        sens = str(self._strinpSens[self.inpSens])
        oflt = str(self._strinpOflt[self.inpOflt])

        impr('\nPROPIEDADES:\n-----------\n')
        impr('REFERENCIA / FASE:' + nL)
        impr('Origen:_______________ ' + self.refMode + nL)
        impr('Amplitud:_____________ ' + str(self.refAmpl) + 'Vrms' + nL)
        impr('Frequencia:___________ ' + str(self.refFreq) + 'Hz' + nL)
        impr('Phase:_________________ ' + str(self.refPhase) + '°' + nL)
        impr('Armónico #:___________ ' + str(self.refHarm) + nL)
        impr('Ref externa:__________ ' + self.refRslp + nL)
        impr('\n')
        impr('ENTRADA / FILTROS:' + nL)
        impr('Origen:_______________ ' + self.inpMode + nL)
        impr('Tierra:_______________ ' + self.inpGnd + nL)
        impr('Acoplamiento:_________ ' + self.inpCoup + nL)
        impr('Filtros:______________ ' + self.inpLine + nL)
        impr('\n')
        impr('GANANCIA / TC:' + nL)
        impr('Sensibilidad:_________ ' + sens + nL)
        impr('Reserva:______________ ' + self.inpRmod + nL)
        impr('Const. tiempo:________ ' + oflt + nL)
        impr('Filtro dB/oct:________ ' + self.inpOfsl + nL)
        impr('Sincronización:_______ ' + self.inpSync + nL)
        impr('\n')
        impr('DISPLAY:' + nL)
        impr('Canal 1:______________ ' + self.ch1Mode + nL)
#        impr('Razón_________________ ' + self.ch1RatS + nL)
        impr('Canal 2:______________ ' + self.ch2Mode + nL)
#        impr('Razón:________________ ' + self.ch1RatS + nL)
        impr('\n')
        impr('SALIDAS / OFFSET:' + nL)
#        impr('Canal 1:______________ ' + self.ch1OutS + nL)
#        impr('Canal 2:______________ ' + self.ch2OutS + nL)
#        impr('Offset X:_____________ ' + str(self.offsetX) + '%' + nL)
#        impr('Offset Y:_____________ ' + str(self.offsetY) + '%' + nL)
#        impr('Offset R:_____________ ' + str(self.offsetR) + '%' + nL)
#        impr('Expand X:_____________ ' + self.expandX + nL)
#        impr('Expand Y:_____________ ' + self.expandY + nL)
#        impr('Expand R:_____________ ' + self.expandR + nL)
        impr('\n')
        impr('SALIDAS AUXILIARES:' + nL)
        impr('Auxiliar 1:___________ ' + str(self.auxout1) + 'V' + nL)
        impr('Auxiliar 2:___________ ' + str(self.auxout2) + 'V' + nL)
        impr('Auxiliar 3:___________ ' + str(self.auxout3) + 'V' + nL)
        impr('Auxiliar 4:___________ ' + str(self.auxout4) + 'V' + nL)
        impr('\n')
        impr('CONFIGURACIÓN:' + nL)
        impr('Bloc. teclas:_________ ' + self.stpLock + nL)

    def crearRegistro(self, archivoLog='LockinSR830.log'):
        """ Crea un registro con el nombre de archivo indicado """
        with open(archivoLog, 'w') as f:
            self.listarPropiedades(impr=f.write, nL='\n')

    def consultarValor(self, valor='R'):
        """ Consulta el valor indicado: 'X', 'Y', 'R' o 'T' """
        valores = {'X': 1, 'Y': 2, 'R': 3, 'T': 4}
        try:
            i = valores[valor]
        except KeyError:
            raise ValueError(valores)

        return float(self._inst.query('OUTP?{0}'.format(i)))

    def consultarDisplay(self, display=1):
        """ Consulta el valor actual del display indicado: 1 o 2 """
        if not (display == 1 or display == 2):
            raise ValueError('CH1 = 1, CH2 = 2')
        return float(self._inst.query('OUTR?{0}'.format(display)))

    def consultarSimultaneo(self, *parametros):
        """
        Consulta simultaneamente los valores indicados (mínimo 2, máximo 6)

        Valores permitidos:
        ------------------
        'X', 'Y', 'R', 'T',
        'AuxIn1', 'AuxIn2', 'AuxIn3', 'AuxIn4',
        'Freq', 'Ch1', 'Ch2'
        """

        valores = {'X': 1, 'Y': 2, 'R': 3, 'T': 4,
                   'AuxIn1': 5, 'AuxIn2': 6, 'AuxIn3': 7, 'AuxIn4': 8,
                   'Freq': 9, 'Ch1': 10, 'Ch2': 11}
        lista = list()
        try:
            for param in parametros:
                lista.append(valores[param])
        except KeyError:
            raise ValueError(valores.keys())
        if 2 <= len(lista) <= 6:
            consulta = 'SNAP?'
            for elemento in lista[:-1]:
                consulta += str(elemento) + ','
            consulta += str(lista[-1])
        else:
            raise ValueError('Mín 2 / Máx 6 parámetros')

        return self._inst.query_ascii_values(consulta, separator=",")

    def consultarAuxiliar(self, aux=1):
        """ Consulta el valor de las entradas auxiliares (1 a 4) """
        if not (aux == 1 or aux == 2 or aux == 3 or aux == 4):
            raise ValueError('Auxiliares: 1 a 4')
        return float(self._inst.query('OAUX?{0}'.format(aux)))

    def leerBuffer(self, display=1, frecMuestreo='64 Hz', puntos=16383,
                   graficar=True):
        """
        Vacia el buffer, adquiere la cantidad de muestras indicadas a la
        frecuencia seleccionada y finalmente transmite el contenido.

        Parámetros:
        ----------
        display : int
            Display de origen de datos: 1 o 2.
        frecMuestreo : int, float, str
            Selecciona la frecuencia de muestreo. Dado que los valores son
            una lista fija, puede ingresarse el índice que figura en el
            manual, el valor como numero flotante o la cadena de texto que
            se corresponde.
        puntos : int
            Número de muestras. Máximo en self._tamBuffer (16383 por manual).
        graficar : bool
            Indica si al finalizar se obtiene un gráfico de vista previa.
        archivoDatos : str
            Nombre del archivo para el volcado de datos.
        """

        strFreqs = ('62.5 mHz', '125 mHz', '250 mHz', '500 mHz', '1 Hz',
                    '2 Hz', '4 Hz', '8 Hz', '16 Hz', '32 Hz',
                    '64 Hz', '128 Hz', '256 Hz', '512 Hz')
        floatFreqs = (0.0625, 0.125, 0.25, 0.5, 1.0,
                      2.0, 4.0, 8.0, 16.0, 32.0,
                      64.0, 128.0, 256.0, 512.0)

        if not (display in [1, 2]):
            raise ValueError('display = 1 ó display = 2')

        if isinstance(frecMuestreo, str):
            try:
                i = strFreqs.index(frecMuestreo)
            except ValueError:
                raise ValueError(strFreqs)
        elif isinstance(frecMuestreo, int):
            if 0 <= frecMuestreo <= 14:
                i = frecMuestreo
            else:
                raise ValueError('0 <= frecMuestreo <= 14, valor entero')
        elif isinstance(frecMuestreo, float):
            try:
                i = floatFreqs.index(frecMuestreo)
            except ValueError:
                raise ValueError(floatFreqs)

        self._inst.write('SRAT{0}'.format(i))

        if not (1 <= puntos <= 16383 and isinstance(puntos, int)):
            raise ValueError('1 <= puntos <= 16383, valor entero')

        orden = 'TRCB?' + str(display) + ',0,' + str(puntos)

        modeBuffer = int(self._inst.query('SEND?'))

        self._inst.write('SEND0')
        self._inst.write('REST')
        print('Eliminando datos en buffer...', end='')
        time.sleep(0.5)
        print('Hecho.')
        print('Iniciando volcado de datos en buffer')
        self._inst.write('STRT')
        duracion = puntos / floatFreqs[i]
        if duracion > 3:
            print('Duración estimada: ' + str(duracion) + 's')
            for paso in self._barraProgreso(50):
                time.sleep(duracion / 50)
        print('\nVerificando estado del buffer...', end='')
        while int(self._inst.query('SPTS?')) < puntos:
            time.sleep(0.1)
        print('Completo. \nTransmitiendo datos a la PC...', end='')

        self._ejeDatos = self._inst.query_binary_values(orden, datatype='f',
                                                        container=np.array)
        self._ejeTiempo = np.linspace(0, duracion, puntos)
        print('Lectura finalizada.')

        self._inst.write('PAUS')
        self._inst.write('SEND{0}'.format(modeBuffer))

        texto_ejeX = 'Tiempo (s)'
        if display == 1:
            texto_ejeY = self.ch1Mode + ' (Vrms)'
        else:
            if self.ch2Mode == 'T':
                texto_ejeY = 'Phase (º)'
            else:
                texto_ejeY = self.ch1Mode + ' (Vrms)'

        if graficar:
            titulo = 'Display - Canal ' + str(display)
            figura = plt.figure()
            figura.canvas.set_window_title(titulo)
            self._figuras.append(figura)
            ejes = figura.add_subplot(111)
            ejes.set_title(titulo)
            ejes.set_xlabel(texto_ejeX)
            ejes.set_ylabel(texto_ejeY)
            ejes.plot(self._ejeTiempo, self._ejeDatos)
            ejes.legend(self.ch1Mode, loc='best', frameon=True,
                        shadow=True, fancybox=True)

        self._datos.append([self._ejeTiempo, self._ejeDatos])

        if graficar:
            return self._ejeTiempo, self._ejeDatos, figura
        else:
            return self._ejeTiempo, self._ejeDatos

    def leerDirectoXY(self):
        """ Lectura directa utilizando el comando Fast Data Transfer """
        pass

    def barrerFrequencia(self, inicio, fin, pasos,
                         graficar, *parametros):
        """
        Barrido de frecuencia con obtención de multiples parámetros.
        Se utiliza la función consultar simultáneo al mismo tiempo que se
        barre entre la frecuencia inicial y final a un número dado de pasos.

        Parámetros:
        ----------
        inicio : float
            Frequencia inicial.
        fin : float
            Frequencia final.
        puntos : int
            Número de pasos.
        graficar : bool
            Indica si al finalizar se obtiene un gráfico de vista previa.
        parametros : tuple
            Parámetros a medir. Los valores permitidos son los mismos que
            para la función consultarSimultaneo.
        """

        self._frecBarrido = np.linspace(inicio, fin, pasos)
        self.consultarSimultaneo(*parametros)

        self._datosBarrido = np.zeros([pasos, len(parametros)])

        for i in self._barraProgreso(pasos):
            self.refFreq = self._frecBarrido[i]
            self._datosBarrido[i] = self.consultarSimultaneo(*parametros)

        self._datosBarrido = self._datosBarrido.transpose()

        if 0 < graficar <= len(parametros):
            figura = plt.figure()
            titulo = ('Barrido de frecuencia: ' + str(inicio) +
                      ' a ' + str(fin) + ' Hz')
            figura.canvas.set_window_title(titulo)
            ejes = figura.add_subplot(111)
            ejes.set_title(titulo)
            ejes.set_xlabel('Freq. (Hz)')

            for i in range(graficar):
                ejes.plot(self._frecBarrido, self._datosBarrido[i])

            if graficar == 1:
                if parametros[0] == 'T':
                    ejes.set_ylabel('Phase (º)')
                else:
                    ejes.set_ylabel(parametros[0] + '(Vrms)')
                ejes.legend([parametros[0]], loc='best', frameon=True,
                            shadow=True, fancybox=True)
            else:
                ejes.set_ylabel('Tensión (Vrms)')
                ejes.legend(parametros, loc='best', frameon=True,
                            shadow=True, fancybox=True)

            self._figuras.append(figura)

        self._datos.append([self._frecBarrido, self._datosBarrido])

        if graficar:
            return self._frecBarrido, self._datosBarrido, figura
        else:
            return self._frecBarrido, self._datosBarrido
