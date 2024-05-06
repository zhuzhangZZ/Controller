# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 11:46:35 2021

@author:Zhu Zhang <z.zhang@uu.nl>

Pyhton code to control Stanford research System SR830 lockin amplifier, DC-102KHz
Use Pyvisa library to make the connection between the computer and the instrument.
COMport should be in the form of 'ASRLx::INSTR', x is the number of the USB port number
connection is RS232 port
"""

import pyvisa as visa
import sys
import time
import numpy as np
from collections import OrderedDict
SENS = OrderedDict([
    ('2 nV/fA', 0),     ('5 nV/fA', 1),     ('10 nV/fA', 2),    ('20 nV/fA', 3),
    ('50 nV/fA', 4),    ('100 nV/fA', 5),    ('200 nV/fA', 6),    ('500 nV/fA', 7),
    ('1 uV/pA', 8),    ('2 uV/pA', 9),    ('5 uV/pA', 10),    ('10 uV/pA', 11),
    ('20 uV/pA', 12),    ('50 uV/pA', 13),    ('100 uV/pA', 14),    ('200 uV/pA', 15),
    ('500 uV/pA', 16),    ('1 mV/nA', 17),    ('2 mV/nA', 18),    ('5 mV/nA', 19),
    ('10 mV/nA', 20),    ('20 mV/nA', 21),    ('50 mV/nA', 22),    ('100 mV/nA', 23),
    ('200 mV/nA', 24),    ('500 mV/nA', 25),    ('1 V/uA', 26)])


TCONSTANTS = OrderedDict([
    ('10 us', 0),    ('30 us', 1),    ('100 us', 2),    ('300 us', 3),
    ('1 ms', 4),    ('3 ms', 5),    ('10 ms', 6),    ('30 ms', 7),
    ('100 ms', 8),    ('300 ms', 9),    ('1 s', 10),    ('3 s', 11),
    ('10 s', 12),    ('30 s', 13),    ('100 s', 14),    ('300 s', 15),
    ('1 ks', 16),    ('3 ks', 17),    ('10 ks', 18),    ('30 ks', 19)])

SAMPLE_RATES = OrderedDict([('62.5 mHz', 0),    ('125 mHz', 1),    ('250 mHz', 2),
    ('500 mHz', 3),    ('1 Hz', 4),    ('2 Hz', 5),    ('4 Hz', 6),    ('8 Hz', 7),
    ('16 Hz', 8),    ('32 Hz', 9),    ('64 Hz', 10),    ('128 Hz', 11),    ('256 Hz', 12),
    ('512 Hz', 13),    ('trigger', 14)])


class SR830:
   
    def __init__(self, COMPort, timeout):
        
        
       
        self.rm = visa.ResourceManager() # To connect the wraper to the USB driver
        print(self.rm.list_resources())
        self.lockin = self.rm.open_resource(COMPort, baud_rate = 19200 )
        self.lockin.timeout = timeout
        self.lockin.read_termination = '\r'
        self.lockin.write_termination = '\r'
        self.name = self.lockin.query("*IDN?")
        print("The %s is open." %self.name)
        
    def CLS(self):
        self.lockin.write("*CLS?")
    def close(self):
        self.lockin.close()
        print("The SR830 is close." )
    def control(self, control):
        if control.find('remote') != -1:
            self.lockin.write("LOCL 1") 
        elif control.find('local') != -1:
            self.lockin.write("LOCL 0") 
        elif control.find('lockloc') != -1:
            self.lockin.write("LOCL 2")     
    def query_control(self):
        b = int(self.lockin.query("LOCL?"))
        if b== 1:
            return 'remote'
        elif b==0:
            return 'local'
        else:
            return 'locklocal'
    """==============REFERENCE and PHASE COMMANDS===============
       +++++++++++++++++++++++++++++++++++++++++++++++++++++++"""
    def reference_phase_shift(self, ref_phase):
        self.lockin.write('PHAS{:.2f}'.format(ref_phase))
        
    def reference_source(self, ref_source):
        
        if ref_source.find('internal') != -1:
            self.lockin.write("FMOD 1") 
        elif ref_source.find('external') != -1:
            self.lockin.write("FMOD 0") 
        
        else:
            print("Invalid input configuration specified \n \
                  Please choose a waveform from the list of: 'internal'|'external'")
            sys.exit()
            
    def query_reference_source(self):
        b = int(self.lockin.query("FMOD?"))
        if b == 1:
            return "internal"
        else:
            return "external"
    def frequency(self, freq):
        self.lockin.write('FREQ{:.5f}'.format(freq))
    def query_frequency(self):
        return float(self.lockin.query("FREQ?"))
    
    def reference_trigger(self, ref_tri):
        
        if ref_tri.find('sin') != -1:
            self.lockin.write("RSLP 0") 
        elif ref_tri.find('TTL_r') != -1:
            self.lockin.write("RSLP 1") 
        elif ref_tri.find('TTL_f') != -1:
            self.lockin.write("RSLP 2")     
        else:
            print("Invalid input configuration specified \n \
                  Please choose a waveform from the list of: 'sin'|'TTL_r'|'TTL_f'")
            sys.exit()
    def query_reference_trigger(self):
        b = int(self.lockin.query("RSLP?"))
        if b== 0:
            return 'sin'
        elif b==1:
            return 'TTL_r'
        else:
            return 'TTL_f'
    def harmonic(self, harm):
        self.lockin.write('HARM {}'.format(harm))
    def query_harm(self):
        return int(self.lockin.query("HARM?"))
    
    def sine_output_amplitude(self, ref_amp):
        self.lockin.write('SLVL{:.2f}'.format(ref_amp))
        
        
    """==============INPUT and FILTER COMMANDS===============
       +++++++++++++++++++++++++++++++++++++++++++++++++++++++"""
   
    def input_config(self, input_value):
        """ Selects the input channel signal
        Possible values are:
            A     -> channel A
            A-B   -> channel A - channelB
            I     -> current channel A amplified 1E6
            I100  -> current channel A  amplified 1E8
        """
        if input_value == 'A':
            self.lockin.write("ISRC 0") 
        elif input_value=='A-B':
            self.lockin.write("ISRC 1") 
        elif input_value=='I1':
            self.lockin.write("ISRC 2") 
        elif input_value=='I100':
            self.lockin.write("ISRC 3") 
        
        else:
            print("Invalid input configuration specified \n \
                  Please choose a waveform from the list of: 'A'|'A-B'|'I0'|'I100'")
            sys.exit()
    def query_input_config(self):
        b =int( self.lockin.query('ISRC?'))
        if b == 0:
            return 'A'
        elif b== 1:
            return 'A-B'
        elif b== 2:
            return 'I1'
        else:
            return 'I100'
    def input_coupling(self, coupling_value):
        """ Selects the input channel signal
        Possible values are:
            AC     -> channel AC coulping
            DC  -> Channel DC coupling
            
        """
        if coupling_value.find('AC') != -1:
            self.lockin.write("ICPL 0")
        elif coupling_value.find('DC') != -1:
            self.lockin.write("ICPL 1")
        else:
            print("Invalid coupling specified \n \
                  Please choose a waveform from the list of: 'AC'|'DC'")
            sys.exit()
    def query_input_coupling(self):
         b = int(self.lockin.query('ICPL?'))
         if b==0:
             return 'AC'
         else:
             return 'DC'
    def input_shield(self, shield_value):
        """ Selects the shield mode
        Possible values are:
            float     -> input signal float
            ground  -> input signal grounded
            
        """
        if shield_value.find('float') != -1:
            self.lockin.write("IGND 0")
        elif shield_value.find('ground') != -1:
            self.lockin.write("IGND 1")
        else:
            print("Invalid coupling specified \n \
                  Please choose a waveform from the list of: 'float'|'ground'")
            sys.exit()
    def query_input_shield(self):
        b =int(self.lockin.query("IGND?"))
        if b==0:
            return 'float'
        else:
            return 'ground'
        
    def input_filter(self, filter_value):
        """ Selects the line filter mode, Q =4
        Possible values are:
            1-0     -> 50/60Hz rejected
            0-1     -> 120Hz rejected
            1-1     -> 50/60 and 120Hz rejected
            0-0     -> none
            
        """
        if filter_value.find('0-0') != -1:
            self.lockin.write("ILIN 0")
        elif filter_value.find('1-0') != -1:
            self.lockin.write("ILIN 1")
        elif filter_value.find('0-1') != -1:
            self.lockin.write("ILIN 2")    
        elif filter_value.find('1-1') != -1:
            self.lockin.write("ILIN 3")
        else:
            print("Invalid coupling specified \n \
                  Please choose a waveform from the list of: '1-0'|'0-1|'1-1'|'0-0'")
            sys.exit()
    def query_input_filter(self):
        b =int(self.lockin.query('ILIN?'))
        if b== 0:
            return '0-0'
        elif b==1:
            return '1-0'
        elif b==2:
            return '0-1'
        else:
            return '1-1'
    """==============GAIN and TIME CONSTANT COMMANDS==========
     +++++++++++++++++++++++++++++++++++++++++++++++++++++++"""            
    def time_constant(self, Tc):
        """ Selects the time constant
        """
        if Tc in list(TCONSTANTS.keys()):
            b = TCONSTANTS[Tc]
            self.lockin.write("OFLT {}".format(b))
        else:
            print("Invalid time constant specified \n \
            Please choose a waveform from the list of:{} ".format(list(TCONSTANTS)))
            sys.exit()        
    def query_time_constant(self):
        b = self.lockin.query("OFLT?")
        return list(TCONSTANTS.keys())[int(b)]
    
    def sensitivity(self, sen):
        """ Selects the time constanr
       
            
        """
        if sen in list(SENS.keys()):
            b = SENS[sen]
            self.lockin.write("SENS {}".format(b))
        else:
            print("Invalid sentivisity specified \n \
            Please choose a waveform from the list of:{} ".format(list(SENS)))
            sys.exit()
    def query_sensitivity(self):
        b = self.lockin.query("SENS?")
        return list(SENS.keys())[int(b)]
   
    def filter_slope(self, filter_slope):
        """ Selects the filter slope,
        Possible values are:
            6,12,18,24    
            
        """
        if filter_slope.find('6') != -1:
            self.lockin.write("OFSL 0")
        elif filter_slope.find('12') != -1:
            self.lockin.write("OFSL 1")
        elif filter_slope.find('18') != -1:
            self.lockin.write("OFSL 2")    
        elif filter_slope.find('24') != -1:
            self.lockin.write("OFSL 3")
        else:
            print("Invalid coupling specified \n \
                  Please choose a waveform from the list of: '6'|12|18|24'")
            sys.exit() 
    def query_filter_slope(self):
        return int(self.lockin.query("OFSL?"))*6+6
        
    def reserve_mode(self, reserve_mode):
        """ Selects the filter slope,
        Possible values are:
            high, normal, low    
            
        """
        if reserve_mode.find('high') != -1:
            self.lockin.write("RMOD 0")
        elif reserve_mode.find('normal') != -1:
            self.lockin.write("RMOD 1")
        elif reserve_mode.find('low') != -1:
            self.lockin.write("RMOD 2")    
       
        else:
            print("Invalid coupling specified \n \
                  Please choose reserve model the list of: '0'|1|2'")
            sys.exit() 
    def query_reserve_mode(self):
        b= int(self.lockin.query('RMOD?'))
        if b==0:
            return 'high'
        elif b==1:
            return 'normal'
        else:
            return 'low'
    def sync_filter(self, sync_filter):
        """ Selects the filter slope,
        Possible values are:
            False: 0
            True: 1
            
        """
        if sync_filter.find('False') != -1:
            self.lockin.write("SYNC 0")
        elif sync_filter.find('True') != -1:
            self.lockin.write("SYNC 1")
        else:
            print("Invalid coupling specified \n \
                  Please choose reserve model the list of: '0'|1'")
            sys.exit() 
    def query_sync_filter(self):
        b = int(self.lockin.query('SYNC?'))
        if b==0:
            return False
        else:
            return True
    """============== DISPLAY and OUTPUT COMMANDS=========="""
    """+++++++++++++++++++++++++++++++++++++++++++++++++++++++"""
    def CH1_display(self, display1):
        """ Selects the filter slope,
        Possible values are:
            X: 0
            R: 1
            X_noise: 2
            AUXin1:3
            AUXin2:4
            
        """
     
        if display1.find('X') != -1:
            self.lockin.write('DDEF 1, 0, 0')
        elif display1.find('R') != -1:
            self.lockin.write('DDEF 1, 1, 0')
        
        else:
            print("Invalid coupling specified \n \
                  Please choose reserve model the list of: '0'|1'")
            sys.exit() 

    def CH2_display(self, display2):
        """ Selects the filter slope,
        Possible values are:
            Y: 0
            Theta: 1
            Y_noise: 2
            AUXin3:3
            AUXin4:4
            
        """
        
        if display2.find('Y') != -1:
            self.lockin.write('DDEF 2, 0, 0')
        elif display2.find('Theta') != -1:
            self.lockin.write('DDEF 2, 1, 0')
        
        else:
            print("Invalid coupling specified \n \
                  Please choose reserve model the list of: '0'|1'")
            sys.exit() 
    def out_offset_exp(self,output):
        if output.find('X') != -1:
            self.lockin.write('OEXP 1, 0, 0')
        elif output.find('Y') != -1:
            self.lockin.write('OEXP 2, 0, 0')
        elif output.find('R') != -1:
            self.lockin.write('OEXP 3, 0, 0') 
        
        else:
            print("Invalid coupling specified \n \
                  Please choose reserve model the list of: 'X'|Y'|'R'")    
            
    def front_output1(self, output1):
        """ Selects the filter slope,
        Possible values are:
            display: 0
            X: 1    
        """
       
        if output1.find('display') != -1:
            self.lockin.write('FPOP 1, 0')
        elif output1.find('X') != -1:
            self.lockin.write('FPOP 1, 1')
        
        else:
            print("Invalid coupling specified \n \
                  Please choose reserve model the list of: '0'|1'")
            sys.exit()             

    def front_output2(self, output2):
        """ Selects the filter slope,
        Possible values are:
            display: 0
            Y: 1    
        """
       
        if output2.find('display') != -1:
            self.lockin.write('FPOP 2, 0')
        elif output2.find('Y') != -1:
            self.lockin.write('FPOP 2, 1')
        
        else:
            print("Invalid coupling specified \n \
                  Please choose reserve model the list of: '0'|1'")
            sys.exit()             


            
    """============== DATA STORAGE COMMANDS=========="""
    """+++++++++++++++++++++++++++++++++++++++++++++++++++++++"""
    def sample_rates(self, SR):
        """ Set the sampling rate
       
            
        """
        if SR in list(SAMPLE_RATES.keys()):
            b = SAMPLE_RATES[SR]
            self.lockin.write("SRAT {}".format(b))
        else:
            print("Invalid time constant specified \n \
            Please choose a waveform from the list of:{} ".format(list(SAMPLE_RATES)))
            sys.exit()        

    def query_sample_rates(self):
        b = self.lockin.query("SRAT?")
        return list(SAMPLE_RATES.keys())[int(b)]
    
    def buffer_mode(self, buffer_mode):
        """ Selects the buffer mode
            Shot: 0
            Loop: 1    
        """
       
        if buffer_mode.find('Shot') != -1:
            self.lockin.write('SEND 0')
        elif buffer_mode.find('Loop') != -1:
            self.lockin.write('SEND 1')
        
        else:
            print("Invalid coupling specified \n \
                  Please choose reserve model the list of: '0'|1'")
            sys.exit()             
    def trigger(self):
        """Software trigger.
        """
        self.lockin.write('TRIG')
                          
    def trigger_start_mode(self, triggermode):
        if triggermode !=1:
            triggermode =1
        else:
            triggermode = 0
        self.send('TSTR {}'.format(triggermode))

    def start_data_storage(self):
        """Start or resume data storage
        """
        self.lockin.write('STRT')
    def pause_data_storage(self):
        """Pause data storage
        """
        self.lockin.write('PAUS')            
    def reset_data_storage(self):
        """Reset data buffers. The command can be sent at any time -
        any storage in progress, paused or not. will be reset. The command
        will erase the data buffer.
        """
        self.lockin.writed('REST')       
            
    """============== DATA RANSFER  COMMANDS=========="""
    """+++++++++++++++++++++++++++++++++++++++++++++++++++++++"""
    def read_out(self, part):
        """
        X: 1    Y:2   R: 3,  Theta:4
        """
       
        if part.find('X') != -1:
            self.lockin.query('OUTP 1')
        elif part.find('Y') != -1:
            self.lockin.query('OUTP 2')
        elif part.find('R') != -1:
            self.lockin.query('OUTP 3')
        elif part.find('Theta') != -1:
            self.lockin.query('OUTP 4')
        else:
            print("Invalid XYR part specified \n \
            Please choose reserve model the list of: 'X'|Y'|'R'|Theta'")
            sys.exit()             
    def read_out_display(self, channel):
        """
        Read out values from the display
        1, channel 1
        2, channel 2
        """
        if channel==0:
            print("channel 1 is i=1, channel 2 is i=2")
            channel = 1
        return self.query('OUTR? {}'.format(channel))
            

      
   