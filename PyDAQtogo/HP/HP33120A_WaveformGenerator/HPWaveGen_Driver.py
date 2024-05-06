# -*- coding: utf-8 -*-
"""
Created on Thu Oct 14 11:46:35 2021

@author:Zhu Zhang <z.zhang@uu.nl>

This is python code to control the HP33120A 15MHz waveform generator
by the SR232 connection.

"""


import sys
import serial
import time
import numpy as np

class HP33120A:
   
    def __init__(self, COMPort):
        
        
        self.HP = serial.Serial()
        self.HP.baudrate = 9600; self.HP.port = COMPort; self.HP.bytesize = 8;
        self.HP.parity='N'; self.HP.stopbits=2; 
        self.HP.timeout=None; self.HP.xonxoff=0 ; self.HP.rtscts=0
        self.HP.open()
        print("The wgen is open, is open ?>>> %s" %self.HP.is_open)
   
        
        
    def CLS(self):
        self.HP.write(b'\n*CLS\r\n')
    def close(self):
        self.HP.close()
        print("The wgen is close, is open ?>>> %s" %self.HP.is_open)
    

    def control(self, control):
        """Sets the control modes to the device.
        remote  -> control by remotly by the code
        local   -> manully control by by pressing the keys in the device with hand
        
        """
        if control.find('local') != -1:
            self.HP.write(bytes("SYSTEM:LOCAL\n",'utf-8'))
        elif control.find('remote') != -1:
            self.HP.write(bytes("SYSTEM:REMOTE\n",'utf-8'))
    
    def loadImpedance(self, impedance):
        """ Sets the load impedance the device expects to be driving.
        This allows the output to be accurately set.
        """
        if type(impedance):
            self.HP.write("OUTP:LOAD %s" % impedance)
        elif impedance.find('inf') != -1:
            self.HP.write("OUTP:LOAD INF")
        elif impedance.find('min') != -1:
            self.HP.write("OUTP:LOAD MIN")
        elif impedance.find('max') != -1:
            self.HP.write("OUTP:LOAD MAX")
        else:
            print("ERROR: Invalid impedance parameter specified\n \
                   Please choose a impedance from the list of: 50|INF|MIN|MAX")
            sys.exit()
    
    def shape(self, shape):
        """ Selects the output shape
        Possible values are:
            sine     -> Sine wave
            square   -> Square wave
            ramp     -> Triangle/saw-tooth wave
            triangle -> Alias of ramp
            pulse    -> Pulse output
            noise    -> White noise
            dc       -> DC voltage
            user     -> Arbitrary waveforms
            
            SIN|SQU|TRI|RAMP|NOIS|DC|USER
        """
        if shape.find('sin') != -1:
            self.HP.write(bytes("FUNCtion:SHAPe SIN\n",'utf-8'))
        elif shape.find('squ') != -1:
            self.HP.write(bytes("FUNCtion:SHAPe SQU\n",'utf-8'))
        elif shape.find('tri') != -1:
            self.HP.write(bytes("FUNCtion:SHAPe TRI\n",'utf-8'))
        elif shape.find('ramp') != -1:
            self.HP.write(bytes("FUNCtion:SHAPe RAM\n",'utf-8'))
        elif shape.find('puls') != -1:
            self.HP.write(bytes("FUNCtion:SHAPe PULS\n",'utf-8'))
        elif shape.find('nois') != -1:
            self.HP.write(bytes("FUNCtion:SHAPe NOIS\n",'utf-8'))
        elif shape.find('dc') != -1:
            self.HP.write(bytes("FUNCtion:SHAPe DC\n",'utf-8'))
        elif shape.find('user') != -1:
            self.HP.write(bytes("FUNCtion:SHAPe USER\n",'utf-8'))
        else:
            print("Invalid waveform shape specified \n \
                  Please choose a waveform from the list of: SIN|SQU|TRI|RAMP|NOIS|DC|USER")
            sys.exit()
            
    
    def frequency(self, freq):
        """ Sets the output frequency to the given value 
        Number of Arb Points             
        8 to 8,192 (8k)          5  MHz   
        8,193 to 12,287 (12k)    2.5MHZ
        12,288 to 16,000         200KHz
        
        Sine                        15MHz
        Square                      15MHz
        Triangle                    100KHz
        Ramp                        100KHz
        Built-In Arbs               5MHz
      """
        self.HP.write(bytes("FREQuency %f\n" %freq, 'utf-8'))
        #self._frequency = freq
    def dutyCycle(self, duty):
        """ Sets the dutycycle of square waveform to the given value
        """
        self.HP.write(bytes("PULSe:DCYCle %f\n" %duty, 'utf-8'))
        #self._frequency = freq
        
    def voltage(self, amplitude=None):
        """ Sets the output voltage of the device.
        NOTE: The device expects to be driving into a 50 Ohm load so.
        If driving loads of higher impedance you will get more voltage.
        """
        if amplitude is not None:
            self.HP.write(bytes("VOLT %f\n" % amplitude, 'utf-8'))
            self.amplitude = amplitude
        return self.amplitude
    def offset(self, offset):
        """ Sets the output offset to the given value
        """
        self.HP.write(bytes("VOLT:OFFS %f\n" %offset, 'utf-8'))
        
    def voltageU(self, unit):
        """ Sets the output voltage unit to the given value
        VPP|VRMS|DBM|DEF"""
              
        if unit.find('VPP') != -1:
            self.HP.write(bytes("VOLTage:UNIT VPP\n", 'utf-8'))
        elif unit.find('VRMS') != -1:
            self.HP.write(bytes("VOLTage:UNIT VRMS\n", 'utf-8'))
        elif unit.find('DBM') != -1:
            self.HP.write(bytes("VOLTage:UNIT DBM\n", 'utf-8'))
        elif unit.find('DEF') != -1:
            self.HP.write(bytes("VOLTage:UNIT DEF\n", 'utf-8'))
        else:
            print("Invalid voltage unit specified \n \
                  Please choose a unit from the list of: VPP|VRMS|DBM|DEF")
            sys.exit()

# ++++++++++++++++++++++++++++Burst waveform +++++++++++++++++++++++++++++++++++++++++++    
    
    def burstCycles(self, burstCycles):
        """ Sets the burst pulse count
                            Minimum Burst Count 
        10 mHz to 1 MHz     1
        >1 MHz to 2 MHz     2
        >2 MHz to 3 MHz     3 
        >3 MHz to 4 MHz     4
        >4 MHz to 5 MHz     5
        Burst Count/Carrier Frequency  ≤500seconds  ,  For Carrier ≤ 100 Hz
        """
        self.HP.write(bytes("BM:NCYCles %f\n" % burstCycles,'utf-8'))
    def burstPhase(self, phase):
        """ Sets the burst phase"""
        self.HP.write(bytes("BM:PHASe %f\n" % phase, 'utf-8'))
        
    def burstFreq(self, burstrate):
        """ Sets the burst frequency,
        10 mHz to 50 kHz. The default is 100 Hz.
        """
        self.HP.write(bytes("BM:INTernal:RATE %f\n" % burstrate, 'utf-8'))  
        
    def burstOn(self, enableBurst):
        if enableBurst:
            self.HP.write(bytes("BM:STAT ON\n", 'utf-8'))
        else:
            self.HP.write(bytes("BM:STAT OFF\n", 'utf-8'))
    
    def burstTig(self,enableBurstTrig):
        if enableBurstTrig:
            self.HP.write(bytes("BM:SOURce EXT\n", 'utf-8'))
        else:
            self.HP.write(bytes("BM:SOURce INT\n", 'utf-8'))
    
    def extTig(self,enableTrig):
        if enableTrig:
            self.HP.write(bytes("TRIG:SOUR EXT\n", 'utf-8'))
        else:
            self.HP.write(bytes("TRIG:SOUR IMM\n", 'utf-8'))
            
# ++++++++++++++++++++++++++++arbitrary waveform +++++++++++++++++++++++++++++++++++++++++++              
    def AWGbuiltIn(self, waveform):
        """Selects the built-in arbitrary waveform to output
        "SINC", “NEG_RAMP”, “EXP_RISE”, “EXP_FALL”, and “CARDIAC”
        
        """
        if waveform.find('SINC') != -1:
            self.HP.write(bytes("FUNC:USER SINC\n", 'utf-8'))
        elif waveform.find('NEG_RAMP') != -1:
            self.HP.write(bytes("FUNC:USER NEG_RAMP\n", 'utf-8'))
        elif waveform.find('“EXP_RISE”') != -1:
            self.HP.write(bytes("FUNC:USER EXP_RISE\n", 'utf-8'))
        elif waveform.find('EXP_FALL') != -1:
            self.HP.write(bytes("FUNC:USER EXP_FALL\n", 'utf-8'))
        elif waveform.find('CARDIAC') != -1:
            self.HP.write(bytes("FUNC:USER CARDIAC\n", 'utf-8'))    
        else:
            print("Invalid arbitrary waveform specified \n \
                  Please choose a unit from the list of: SINC| NEG_RAMP|EXP_RISE| EXP_FALL|CARDIAC")
            sys.exit()
            
    """To select the waveform currently stored in volatile memory, specifythe VOLATILE parameter. 
    The keyword “VOLATILE” does not have a short form. The correct syntax is:   "FUNC:USER VOLATILE"
    """        
    def AWGwave(self, wavepoints):
        """writes the waveform to the valatile memory, 
        “-1” corresponds to-5 volts and “+1” corresponds to +5 volts.
        """
        arr = wavepoints.tolist()
        arr = [format(a,".4f") for a in arr]
        arr = [float(i) for i in arr]

        print("waveform has %d points, transfering the data to the device...."%len(arr))
        # (bytes("DATA VOLATILE, %s\n" % (str(arr)[1:-1]), 'utf-8'))
        # ser.write(bytes("DATA VOLATILE, %s\n" % (str(arr)[1:-1]), 'utf-8'))

        self.HP.write(b"DATA VOLATILE")
        poiperround = 10 # points per round
        for i in np.arange(len(arr)/poiperround):
            self.HP.write(bytes(",%s"%(str(arr[int(poiperround*i+0):int(poiperround*(i+1))])[1:-1]), 'utf-8'))
        
            time.sleep(0.35)    
        self.HP.write(b"\n")
        
    def AWGselect(self ):
        self.HP.write(bytes("FUNC:USER VOLATILE \n", 'utf-8'))
        
    def AWGOut(self ):
        self.HP.write(bytes("FUNC:SHAP USER\n", 'utf-8'))

# ++++++++++++++++++++++++++++query information +++++++++++++++++++++++++++++++++++++++++++        
    def query_error(self):
        self.HP.write(bytes("SYSTem:ERRor?\n", 'utf-8'))
        g = self.HP.readline()
        print(g.decode("utf-8").rstrip())
    
    def query_frequency(self):
        self.HP.write(bytes("FREQ?\n", 'utf-8'))
        g = self.HP.readline()
        print(g.decode("utf-8").rstrip())
    def query_amplitude(self):
        self.HP.write(bytes("VOLT?\n", 'utf-8'))
        g = self.HP.readline()
        print(g.decode("utf-8").rstrip())
    def query_offset(self):
        self.HP.write(bytes("VOLT:OFFS?\n", 'utf-8'))
        g = self.HP.readline()
        print(g.decode("utf-8").rstrip())    
        
        