# -*- coding: utf-8 -*-
"""
Created on Mon Jan 17 12:21:34 2022

@author: Zhu Zhang
"""
#%%
"""
===================================================================================
++++++++++++++++++++++++++VIA Pyhton serialport with  Functions++++++++++++++++++++
"""
import HPWaveGen_Driver
import numpy as np
import numpy
import time

## check the COM port in your computer 
try:
    wgen = HPWaveGen.HP33120A(COMPort='COM6')
except:
    print("The HP33120A is alreday opended!")
wgen.CLS()       
wgen.control(control = 'remote')
#%%

## Sine wave
wgen.shape('sin')
wgen.voltage(amplitude= 0.1)
wgen.offset(offset= 0)

wgen.frequency(freq = 1000)
wgen.burstCycles(burstCycles =10)
wgen.burstFreq(burstrate = 1e3)
wgen.burstPhase(phase =0)
wgen.burstTig(enableBurstTrig = False)
wgen.burstOn(enableBurst = False)
time.sleep(2)
wgen.query_frequency()
wgen.query_amplitude()
wgen.query_error()
wgen.query_offset()

time.sleep(2)
wgen.query_error()
#%%

## call built-in wavefrom in the waveform generator
wgen.AWGbuiltIn(waveform = 'CARDIAC')
wgen.voltage(amplitude= 0.1)
wgen.offset(offset= 0)
wgen.frequency(freq = 100e3)
wgen.AWGOut()
time.sleep(1)
wgen.query_error()
#%%
## Arbitrary wave generator


import matplotlib.pyplot as plt
from math import pi
f = 1000
f_ca = 10
duty = 0.4
t = np.linspace(0,1, num=200*f, endpoint=True)

x =np.zeros(len(t))    
for n in  range(1,300):
    x += 1/n*np.sin(pi*n*duty)*np.cos(n*2*pi*f*t)
    
Mo = (duty + 2/pi*x)-max(duty + 2/pi*x)/2
st = np.zeros(len(t))
phase =pi*1/4

fig, ax = plt.subplots()

for n in range(1,7):
    st += -1/n * np.sin(2*pi*f*t*n )*1/pi
    ax.plot(st[:int(len(t)/f*1)])
    
wavepoints = (st[:int(len(t)/f*1)])
wgen.AWGwave(wavepoints = wavepoints)
wgen.AWGselect()
wgen.voltage(amplitude= 3)
wgen.offset(offset= 0)
wgen.frequency(freq = 100e3)
wgen.AWGOut()
time.sleep(1)
wgen.query_error()
#%%
wgen.query_error()

#%%
wgen.burstOn(enableBurst = False)
wgen.voltage(amplitude= 0.05)
wgen.control(control = 'local')
wgen.close()
