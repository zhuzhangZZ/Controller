# -*- coding: utf-8 -*-
"""
Created on Thu Oct 14 11:53:03 2021

@author: Zhang101
"""


import HPWaveGen_Driver

# import autoUL
import numpy
import time
# import win32api
# from pywinauto.application import Application
# import visa
import serial.tools.list_ports
# import pyautogui
ports = list(serial.tools.list_ports.comports())
for p in ports:
    if 'MyCDCDevice' in p.description:
        print(p)
        # Connection to port
        s = serial.Serial(p.device)
path_to_wavegen = 'COM6'
path_to_osc = "USB0::0x2A8D::0x2F01::MY54408800::0::INSTR"
# wavegen = HPWaveGen.agilent33120A(path_to_wavegen)
wavegen  = serial.Serial(p.device)
#%%


#%%
import visa     # pyvisa
import time
import numpy as np
rm = visa.ResourceManager() # To connect the wraper to the USB driver
rm.list_resources()
ser = rm.open_resource('ASRL3::INSTR')
print(rm.list_resources_info()) #
print(ser.query('*IDN?'))
ser.timeout = 5000
ser.write("SYST:REM")
ser.write("APPL:SIN  6 KHZ, 3.0 VPP, 0 V ")
time.sleep(1)
print("The Frequency is %sHz" %ser.query("FREQ?"))
#%%
print(ser.query('*IDN?'))
ser.write('FUNC:SHAP SIN' )  # Select sine wave function  
ser.write("FREQ 5.0E+3\n")   # Set frequency to 5 kHz  
ser.write("VOLT 3.0\n")   # Set amplitude to 3 Vpp  
ser.write("VOLT:OFFS 0\n")  #  Set offset to -2.5 Vdc
ser.write("FREQ 4.0E+3\n")
ser.write("BM:NCYCles 5\n")
ser.write("BM:PHASe 0\n")
ser.write("BM:INTernal:RATE 400\n")
ser.write("BM:SOURce INT\n")
ser.write("BM:STATe ON")
#%%
from math import pi
# allpy a arbitrary waveform
ser.write('\n*CLS\r')
ser.write("APPL:SIN  6.0E+3 HZ, 3.0 VPP, 0 V \r")
# arr = (st[:int(len(t)/f*1)]).tolist()
arr = np.linspace(0.1,1,5)
# arr = np.sin(2*pi*2*arr)
arr = [format(a,".3f") for a in arr]
arr = [float(i) for i in arr]

print(len(arr))
# bytes("DATA VOLATILE, %s" % (str(arr)[1:-1]), 'utf-8')
# ser.write("DATA VOLATILE, %s" % (str(arr)[1:-1]))
# ser.write("DATA VOLATILE,  0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2, 0.225, 0.25" )
ser.write("DATA VOLATILE,")
 
for i in np.arange(len(arr)):
    ser.write(",%s"%arr[i])
        
    time.sleep(0.3)            


    
time.sleep(2)
print(ser.query("SYSTem:ERRor?"))

       
ser.write("FUNC:USER VOLATILE ")
print(ser.query("DATA:ATTRibute:POINts?"))

time.sleep(2)
ser.write("FUNC:SHAP USER\n")
#%%
time.sleep(0.5)
print(ser.query("BM:STATe?"))
time.sleep(0.5)
print(ser.query("SYSTem:ERRor?"))
time.sleep(0.5)
#%%
ser.write("APPL:SIN  6 KHZ, 0.50 VPP, 0 V \r")
ser.write("SYST:lOC\r")
ser.close()
print(ser.is_open)


#%%
"""
===============================================================================
+++++++++++++++++++++++++++++++++++++VIA Pyhton serialport++++++++++++++++++++
"""
import serial
import time
import numpy as np
ser = serial.Serial()
ser.baudrate = 9600
ser.port = 'COM3'
ser.bytesize = 8
ser.parity='N'
ser.stopbits=2
ser.timeout=None 
ser.xonxoff=0 
ser.rtscts=0
# Serial<id=0xa81c10, open=False>(port='COM3', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=None, xonxoff=0, rtscts=0)
ser.open()
print(ser.is_open)
ser.write(b'\n*CLS\r\n')
ser.write(b"SYST:REM\n")
ser.write(b"APPL:SIN  6 KHZ, 3.0 VPP, 0 V \r\n")

# ser.write(b"SYST:loc\r\n")


#%%
import numpy as np
from math import pi
from scipy import signal 
import matplotlib.pyplot as plt
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
    
time.sleep(5)

#%%


#%%
ser.write(b'\n*CLS\r\n')
ser.write(b"APPL:SIN  5.0E+4 HZ, 3.0 VPP, 0 V \r\n")
arr = (st[:int(len(t)/f*1)]).tolist()
# arr = np.linspace(0,1,350)
# arr = np.sin(2*pi*2*arr)
arr = [format(a,".4f") for a in arr]
arr = [float(i) for i in arr]

print(len(arr))
(bytes("DATA VOLATILE, %s\n" % (str(arr)[1:-1]), 'utf-8'))
# ser.write(bytes("DATA VOLATILE, %s\n" % (str(arr)[1:-1]), 'utf-8'))

ser.write(b"DATA VOLATILE")
poiperround = 10 # points per round
for i in np.arange(len(arr)/poiperround):
    ser.write(bytes(",%s"%(str(arr[int(poiperround*i+0):int(poiperround*(i+1))])[1:-1]), 'utf-8'))
        
    time.sleep(0.35)    
ser.write(b"\n")
time.sleep(2)
ser.write(b"SYSTem:ERRor?\n")
g = ser.readline()
print(g.decode("utf-8").rstrip())
       
ser.write(bytes("FUNC:USER VOLATILE \n", 'utf-8'))
ser.write(b"DATA:ATTRibute:POINts?\n")
g = ser.readline()
print(g.decode("utf-8").rstrip())
time.sleep(2)
ser.write(bytes("FUNC:SHAP USER\n", 'utf-8'))

ser.write(b"VOLT 2.0\n")   # Set amplitude to 3 Vpp  
ser.write(b"VOLT:OFFS 0\n")  #  Set offset to -2.5 Vdc
ser.write(b"FREQ 10E+5\n")  # Set frequency to 5 kHz  
ser.write(b"BM:NCYCles 1000\n")
ser.write(b"BM:PHASe 0\n")
ser.write(b"BM:INTernal:RATE 1.5E+3\n")
ser.write(b"BM:SOURce INT\n")
ser.write(b"BM:STATe ON\n")
#%%
ser.write(b"APPL:SIN  6 KHZ, 0.05 VPP, 0 V \r\n")
ser.write(b"SYST:lOC\r\n")
ser.close()
print(ser.is_open)
# False

#%%
ser.write(b'FUNC:SHAP SIN\n' )  # Select sine wave function    
ser.write(b"VOLT 3.0\n")   # Set amplitude to 3 Vpp  
ser.write(b"VOLT:OFFS 0\n")  #  Set offset to -2.5 Vdc
ser.write(b"FREQ 5.0E+6\n")  # Set frequency to 5 kHz  
ser.write(b"BM:NCYCles 50\n")
ser.write(b"BM:PHASe 0\n")
ser.write(b"BM:INTernal:RATE 5.0E+4\n")
ser.write(b"BM:SOURce INT\n")
ser.write(b"BM:STATe ON\n")



#%%
ser.write(b"FREQ?\n")
print( "The Freq is %s Hz" %ser.readline().decode("utf-8").rstrip())
ser.write(b"BM:INTernal:RATE?\n")
print( "The Modulation Freq is %s Hz" %ser.readline().decode("utf-8").rstrip())
b=ser.write(b"BM:PHASe?\n")
c = ser.readline()
ser.write(b"BM:STATe?\n")
print( "The BM state is %s" %ser.readline().decode("utf-8").rstrip())
ser.write(b'*IDN?\n')
f = ser.readline()
ser.write(b"SYSTem:ERRor?\n")
g = ser.readline()
print(g.decode("utf-8").rstrip())
ser.write(b"DATA:ATTRibute:POINts?\n")
h = ser.readline()
print(h.decode("utf-8").rstrip())

ser.write(b"DATA:CATalog?\n")
l = ser.readline()
print(l.decode("utf-8").rstrip())

# ser.write(b"DATA:DELete ARB1\n")



#%%
for i in range(50,100):
    ser.write(bytes("APPL:SIN  %s KHZ, 3 VPP, 0 V \r\n"%(i+1), 'utf-8'))
    ser.write(b"BM:NCYCles 10\n")
    ser.write(b"BM:PHASe 0\n")
    ser.write(b"BM:INTernal:RATE 5.0E+3\n")
    ser.write(b"BM:SOURce INT\n")
    ser.write(b"BM:STATe ON\n")
    time.sleep(1)
    ser.write(b"FREQ?\n")
    print( "The Freq is %s Hz" %ser.readline().decode("utf-8").rstrip())
    ser.write(b"BM:INTernal:RATE?\n")
    print( "The Modulation Freq is %s Hz" %ser.readline().decode("utf-8").rstrip())
    b=ser.write(b"BM:PHASe?\n")
    c = ser.readline()
    ser.write(b"BM:STATe?\n")
    print( "The BM state is %s" %ser.readline().decode("utf-8").rstrip())
    ser.write(b'*IDN?\n')
    f = ser.readline()
    ser.write(b"SYSTem:ERRor?\n")
    g = ser.readline()
    print(g.decode("utf-8").rstrip())
    print("\n")
    time.sleep(3)
#%%
"""
===================================================================================
++++++++++++++++++++++++++VIA Pyhton serialport with  Functions++++++++++++++++++++
"""
import HPWaveGen
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
