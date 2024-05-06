# -*- coding: utf-8 -*-
"""
Simple NI-DAQ modelling for scripted multichannel measurements with analog inputs and outputs
customized for potentiodynamic microscopy using a lock-in amplifier and NI DAQ as signal generator

Created on Thursday April 8, 2021
@authorr: Zhu Zhang z.zhang@uu.nl
"""

import numpy as np
from PyDAQmx import *
from ctypes import byref
from time import sleep
from scipy import signal
import time
import math


#==============================================================================
# Define the function of signal generetion to send signal out by output channel
#==============================================================================
class StepSinGenerator(Task):
    """ define a signal equal to low frq. triangle wave + high freq. sine wave 
    and a signal of sine reference signal
    freq, ampl: frequency and amplitude of sine wave
    off, period: offset and period of triangle wave
    """
    def __init__(self, m_freq, m_ampl, v_min, v_max, v_scanRate, CV=0, reverse= 1, step= 0.002, offset = 0 ):
        Task.__init__(self)
        # Wavegenerator properties:
        freq = m_freq
        ampl = m_ampl*1e-3
        self.wavegenOffsetNCycles = 1
        self.wavegenOffsetStart = v_min*1e-3
        self.wavegenOffsetEnd = v_max*1e-3
        period = abs(v_max-v_min)/v_scanRate*2
        self.wavegenStep = step # set to small enough then can generate sawtooth wave; if set it to larger ones e.g. 0.1, the wave will be stepwise
        if freq >1500:
            self.sampleRate =  62.0*freq # Samples/second, maxmium samplingrate is 250K per channel
            self.maxNsamples = 62.0*freq
        elif freq >1000:
            self.sampleRate =  80.0*freq # Samples/second, maxmium samplingrate is 250K per channel
            self.maxNsamples = 80.0*freq
        elif freq >400:
            self.sampleRate =  100.0*freq # Samples/second, maxmium samplingrate is 250K per channel
            self.maxNsamples = 100.0*freq
        else:
            self.sampleRate =  300.0*freq # Samples/second
            self.maxNsamples = 300.0*freq
        # Check wave for invalid values:
        if abs(ampl) + max(abs(self.wavegenOffsetStart),abs(self.wavegenOffsetEnd))>10.0:
            print("Tried to supply a potential over (-)10 V")
            return
        # Make array of wave:
        self.Nsamples = int(self.sampleRate/freq)
        self.wavedata = np.abs(np.linspace(2*ampl, -2*ampl, self.Nsamples, endpoint=False))
        
        self.t = np.linspace(0, 1, int(self.sampleRate*period), endpoint=False)
        self.sin = ampl*np.sin(2*np.pi *freq*period*self.t)
        self.tri = ampl * signal.sawtooth( 2*np.pi * freq*period*self.t, width=0.5)
        self.squ = abs(v_max-v_min)*1e-3*signal.square(2*np.pi *period*self.t, duty=0.5)
        # Setup DAQ:
        read = int32()
        
        self.steps = math.ceil(abs(self.wavegenOffsetEnd- self.wavegenOffsetStart)/self.wavegenStep)
        self.offsetArray = np.append(np.linspace(self.wavegenOffsetStart, self.wavegenOffsetEnd, num = self.steps)[:-1], 
                                     np.linspace(self.wavegenOffsetEnd, self.wavegenOffsetStart, num = self.steps )[:-1])
        print(len(self.offsetArray))
        # print("\n")
        self.wavegenOffsetArray =  np.repeat(self.offsetArray,int(self.sampleRate*period/len(self.offsetArray)))
        if len(self.wavegenOffsetArray) < self.sampleRate*period:
            self.wavegenOffsetArray = np.append(self.wavegenOffsetArray, \
                self.wavegenOffsetStart*np.ones(int(self.sampleRate*period)-len(self.wavegenOffsetArray)) )
#        self.wavegenOffsetArray = np.tile(np.concatenate((\
#                np.arange(0, self.wavegenOffsetEnd, np.sign(self.wavegenOffsetEnd)*self.wavegenStep), 
#                np.arange(self.wavegenOffsetEnd, self.wavegenOffsetStart, -np.sign(self.wavegenOffsetEnd)*self.wavegenStep), 
#                np.arange(self.wavegenOffsetStart, 0, np.sign(self.wavegenOffsetEnd)*self.wavegenStep) )), self.wavegenOffsetNCycles)
        self.ACStep = self.sin + self.wavegenOffsetArray*CV + offset*1e-3
        """the signal which will be sent to AO0 and AO1 are stacked because I choose the the fillmode of 'DAQmx_Val_GroupByChannel'
        in the WriteAnalogF64 function, which means the data is grouped by channel(non-interleaved), check the Interleaving on 
        https://zone.ni.com/reference/en-XX/help/370466AH-01/mxcncpts/interleaving/ for more details"""
#        self.AC_ref = np.append(self.ACStep,self.sin/max(self.sin)*0.5, axis=0) #self.sin/max(self.sin)*1.0 is the reference signal to lockin
        self.AC_ref = np.append(self.ACStep*reverse,(self.sin-np.mean(self.sin))/max((self.sin-np.mean(self.sin)))*0.5, axis=0)
        self.CreateAOVoltageChan("Dev1/ao0", "", -1.5, 1.50, DAQmx_Val_Volts, None)
        self.CreateAOVoltageChan("Dev1/ao1", "", -1.50, 1.50, DAQmx_Val_Volts, None)
        self.CfgSampClkTiming("", int(self.sampleRate), DAQmx_Val_Rising, DAQmx_Val_ContSamps, int(self.sampleRate))
        # self.sampleRate ----The sampling rate in samples per second per channel
        #self.Num ----The number of samples to acquire or generate for each channel in the task( in every period)   self.num*signal_frq=self.N
        self.WriteAnalogF64(int(self.sampleRate*period),bool32(False),-1, DAQmx_Val_GroupByChannel,self.AC_ref,byref(read),None)
        # self.sampleRate ---The number of samples, per channel, to write


class StepWave(Task):
    """ define a signal equal to low frq. triangle wave + high freq. sine wave 
    and a signal of sine reference signal
    freq, ampl: frequency and amplitude of sine wave
    off, period: offset and period of triangle wave
    """
    def __init__(self, period, v_min, v_max,  reverse= 1, wave="sque" ):
        Task.__init__(self)
        # Wavegenerator properties:
        freq = 1/period
        ampl = abs(v_max-v_min)*1e-3
        self.wavegenOffsetNCycles = 1
        self.wavegenOffsetStart = v_min*1e-3
        self.wavegenOffsetEnd = v_max*1e-3
        
        if freq >400:
            self.sampleRate =  200.0*freq # Samples/second, maxmium samplingrate is 250K per channel
        else:
            self.sampleRate =  500.0*freq # Samples/second
        # Check wave for invalid values:
        if abs(ampl) + max(abs(self.wavegenOffsetStart),abs(self.wavegenOffsetEnd))>10.0:
            print("Tried to supply a potential over (-)10 V")
            return
        # Make array of wave:
        # self.Nsamples = int(self.sampleRate/freq)
        # self.wavedata = np.abs(np.linspace(2*ampl, -2*ampl, self.Nsamples, endpoint=False))
        
        self.t = np.linspace(0, 1, int(self.sampleRate*period), endpoint=False)
        self.sin = ampl/2*np.sin(2*np.pi *freq*self.t*period) + abs(v_max+v_min)*1e-3/2
        self.tri = ampl/2 * signal.sawtooth( 2*np.pi * freq*self.t*period, width=0.5) + abs(v_max+v_min)*1e-3/2
        self.squ = ampl/2 * signal.square(2*np.pi *freq*self.t*period, duty=0.5) + abs(v_max+v_min)*1e-3/2
        # Setup DAQ:
        read = int32()
        if wave == 'sque':
            self.Step = self.squ
        elif wave == 'tria':
            self.Step = self.tri
        elif wave == 'sine':
            self.Step = self.sin
        """the signal which will be sent to AO0 and AO1 are stacked because I choose the the fillmode of 'DAQmx_Val_GroupByChannel'
        in the WriteAnalogF64 function, which means the data is grouped by channel(non-interleaved), check the Interleaving on 
        https://zone.ni.com/reference/en-XX/help/370466AH-01/mxcncpts/interleaving/ for more details"""
#        self.AC_ref = np.append(self.ACStep,self.sin/max(self.sin)*0.5, axis=0) #self.sin/max(self.sin)*1.0 is the reference signal to lockin
        self.AC_ref = np.append(self.Step*reverse,(self.sin-np.mean(self.sin))/max((self.sin-np.mean(self.sin)))*0.5, axis=0)
        self.CreateAOVoltageChan("Dev1/ao0", "", -1.5, 1.5, DAQmx_Val_Volts, None)
        self.CreateAOVoltageChan("Dev1/ao1", "", -1.5, 1.5, DAQmx_Val_Volts, None)
        self.CfgSampClkTiming("", int(self.sampleRate), DAQmx_Val_Rising, DAQmx_Val_ContSamps, int(self.sampleRate))
        # self.sampleRate ----The sampling rate in samples per second per channel
        #self.Num ----The number of samples to acquire or generate for each channel in the task( in every period)   self.num*signal_frq=self.N
        self.WriteAnalogF64(int(self.sampleRate*period),bool32(False),-1, DAQmx_Val_GroupByChannel,self.AC_ref,byref(read),None)
        # self.sampleRate ---The number of samples, per channel, to write




#==============================================================================
# Define the function of acquirement to get data from analog input  channel
#==============================================================================
class MeasureTask(Task):
    def __init__(self, freq, rt):
        Task.__init__(self)
        # Create data storages:
        if freq > 400:
            self.samplerate = 100.0*freq  # maxmium sampling rate is 400K in total(all channel combined)
            if freq>800:
                self.samplerate = 80.0*freq
                if freq>1000:
                    self.samplerate = 20.0*freq   
        else:
            self.samplerate = 100.0*freq 
        self.updatadataevery = 10
        self.inputchannelsN = 5
        # if freq< 600:
        #     self.inputchannelsN = 6
        self.data = np.zeros(self.inputchannelsN*self.updatadataevery)
        self.a = []
        self.CreateAIVoltageChan("Dev1/ai0","Voltage",DAQmx_Val_Diff,-2.0,2.0,DAQmx_Val_Volts,None)# from Edaq waveform
        self.CreateAIVoltageChan("Dev1/ai1","Current",DAQmx_Val_Diff,-10.0,10.0,DAQmx_Val_Volts,None)# from eDaq currents
        self.CreateAIVoltageChan("Dev1/ai3","LockinX",DAQmx_Val_Diff,-10.0,10.0,DAQmx_Val_Volts,None) #from lockin output x
        self.CreateAIVoltageChan("Dev1/ai4","PD",DAQmx_Val_Diff,-10.0,10.0,DAQmx_Val_Volts,None) #from femto PD
        self.CreateAIVoltageChan("Dev1/ai5","LockinY",DAQmx_Val_Diff,-10.0,10.0,DAQmx_Val_Volts,None) #from lockin output y
        # if freq< 600:
        #     self.inputchannelsN = 6
        #     self.CreateAIVoltageChan("Dev1/ai6","Phase",DAQmx_Val_Diff,-10.0,10.0,DAQmx_Val_Volts,None) #from lockin phase
        # refer to http://zone.ni.com/reference/en-XX/help/370471AA-01/daqmxcfunc/daqmxcreateaivoltagechan/
        self.CfgInputBuffer(int(self.samplerate *(rt+1)))
        self.CfgSampClkTiming("",self.samplerate,DAQmx_Val_Rising,DAQmx_Val_ContSamps,1000) # 1000.0 is the sampling rate
        # refer to http://zone.ni.com/reference/en-XX/help/370471AA-01/daqmxcfunc/daqmxcfgsampclktiming/
                 
        self.AutoRegisterEveryNSamplesEvent(DAQmx_Val_Acquired_Into_Buffer, self.updatadataevery, 0)
        # refer to http://zone.ni.com/reference/en-XX/help/370471AM-01/daqmxcfunc/daqmxregistereverynsamplesevent/
        self.AutoRegisterDoneEvent(0)
    def EveryNCallback(self):
        read = int32()
        # Handle data, done every "updatadataevery" measurements
        self.ReadAnalogF64(self.updatadataevery, 10.0, DAQmx_Val_GroupByScanNumber, self.data, self.inputchannelsN*self.updatadataevery, byref(read), None)
        self.a.extend(self.data.tolist())
        return 0 # The function should return an integer
    def DoneCallback(self, status):
        # print("Status",status.value)
        print("Status")
        return 0 # The function should return an integer



#==============================================================================
# Define the function to zero the optput channels atfer the measurement is done
#==============================================================================
class ZeroOutput(Task):
    def __init__(self):
        Task.__init__(self)
        self.CreateAOVoltageChan("Dev1/ao0","",-10.0,10.0,DAQmx_Val_Volts,None)
        self.CreateAOVoltageChan("Dev1/ao1","",-10.0,10.0,DAQmx_Val_Volts,None)
        self.CfgSampClkTiming("", int(10), DAQmx_Val_Rising, DAQmx_Val_ContSamps, int(10))
        self.WriteAnalogF64(int(10),bool32(False),-1,DAQmx_Val_GroupByChannel,np.zeros((1,20)),byref(int32()),None)
#        self.WriteAnalogScalarF64(1,10.0, np.zeros((1,1))*0.00, None)
#        self.WriteAnalogScalarF64(1,10.0, 0.0,None)
    
class InitialOutput(Task):
    def __init__(self, voltage=-0.2):
        Task.__init__(self)
        self.CreateAOVoltageChan("Dev1/ao0","",-10.0,10.0,DAQmx_Val_Volts,None)
        self.CreateAOVoltageChan("Dev1/ao1","",-10.0,10.0,DAQmx_Val_Volts,None)
        self.CfgSampClkTiming("", int(10), DAQmx_Val_Rising, DAQmx_Val_ContSamps, int(10))
        self.WriteAnalogF64(int(10),bool32(False),-1,DAQmx_Val_GroupByChannel,voltage*np.ones((1,20)),byref(int32()),None)
#        self.WriteAnalogScalarF64(1,10.0, np.zeros((1,1))*0.00, None)
#        self.WriteAnalogScalarF64(1,10.0, 0.0,None)
