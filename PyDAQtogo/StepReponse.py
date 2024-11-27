# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 15:00:58 2022

@author: PDSM
"""
import PyDAQtogo.config as config
import PyDAQtogo.NIDAQforPDSM as daq
import PyDAQtogo.SRSLockinAmplifier as SRS

import numpy as np
import matplotlib.pyplot as plt
import time
import math
import csv
import os
from datetime import date
import tqdm
import ProgressBar as PB

## STEP 1: read parameters from a config file
np.set_printoptions(threshold=20)
configfile = config.find_configfile("config_Zhu.yml")
param = config.read_config(configfile)

## STEP 2: prepare DAQ for executing the experiment

m_freq = param['Measurement']['f_modulate']  ## this is an example of reading from a dictionary, fill in the rest as necessary
m_ampl = param['Measurement']['a_modulate']
v_max = param['Measurement']['v_max']
v_min = param['Measurement']['v_min']
scanrate = param['Measurement']['v_scanRate']
savename = param['Saving']['filename_video']
saveloc = param['Saving']['directory']
saveloc = 'C:\\Data\\Zhu\\PDSMwithNI\\2022-02-28_Ti_Au__SiO2_100mKCl'
if not os.path.exists(saveloc):
    os.mkdir(saveloc)
    print("Directory " , saveloc ,  " Created ")
else:    
    print("Directory " , saveloc ,  " already exists")

savename = "ACV0"

try:
    del movieN
    
except:
    pass
#%%


v_min = 0
v_max = 100

period = 10
Ampl_lockins = np.array([]); phases = np.array([])
Ampl_lockin_as =np.array([]); pds = np.array([])
currents = np.array([])


if m_freq > 500:
    rt =80
else:
    rt =100
time_start=time.process_time()
"""CV : choose 0 or 1, 0 just do sine oscillation, 1 do AC voltammetry`
    reverse: 1 or -1, 1 not reverse when use dualPicostat, 1 reverse for Picostat with range of larger current input 
    have tested the pico, the voltage output to cell is correct, the output to daq is reserved """
taskM = daq.MeasureTask(m_freq, rt)
taskStep = daq.StepWave(period=period, v_min=v_min, v_max=v_max,  reverse= 1, wave="sque" )
taskStep.StartTask()
taskM.StartTask()
PB.ShowBar(Barname = "ScanProgress", runtime = rt)
taskStep.StopTask()
taskStep.ClearTask()
 
 
## STEP 3: start the measurement
###===================================================================###################     
#     taskG = daq.StepSinGenerator(step =2*1e-3, m_freq=m_freq, m_ampl=m_ampl,v_min= v_min, v_max=v_max,v_scanRate=scanrate, CV=1, reverse=1)
#     taskG.StartTask()

 
# #    PressStop=input('Acquiring samples continuously. Press Enter to interrupt\n')

#     # time.sleep((v_max-v_min)/scanrate*2*4+1)
#     PB.ShowBar(Barname = "CVScan", runtime = (v_max-v_min)/scanrate*2*2+1) 

#     taskG.StopTask()
#     taskG.ClearTask()

###===================================================================###################     
#     taskModEnd = daq.StepSinGenerator(step =2*1e-3,m_freq=m_freq,m_ampl=m_ampl+Extra_amp,v_min= v_min,v_max=v_max,v_scanRate=scanrate, CV=0,offset=of,reverse=1)
#     taskModEnd.StartTask()
#     PB.ShowBar(Barname = "ScanProgress", runtime = rt)
#     taskModEnd.StopTask()
#     taskModEnd.ClearTask()

taskM.StopTask()
taskM.ClearTask()
##===================================================================###################   
time_stop=time.process_time()
runtime=time_stop-time_start
taskZ = daq.ZeroOutput()
taskZ.StartTask()
taskZ.StopTask()
taskZ.ClearTask()
## STEP 4: readout the data from DAQ and store it in proper format
#sn = None
try:
    movieN += 1
except:
    movieN = 0

savefileandpath = (saveloc+"\\"+savename+"_m"+str(movieN))

param['Measurement']['v_max'] = v_max  
param['Measurement']['v_min'] = v_min   
param['Measurement']['period'] = period   

config.save_config( param,saveloc+"\\"+savename+"_m"+str(movieN))

# Get and save measured data:
mdata = np.array(taskM.a).reshape(-1,taskM.inputchannelsN)
np.save(savefileandpath, mdata)
if m_freq > 400:
    samplerate = 100.0*m_freq  # maxmium sampling rate is 400K in total(all channel combined)
if m_freq>800:
    samplerate = 80.0*m_freq
else:
    samplerate = 100.0*m_freq 
## STEP 5: save the log file and the config file in the same directory as data


## STEP 6: plot the output to check if measurement was successful
Ampl_lockin_x = np.mean(mdata[int(samplerate*15):,2])
Ampl_lockin_y = np.mean(mdata[int(samplerate*15):,4])
Ampl_lockin_a = np.sqrt(Ampl_lockin_x*Ampl_lockin_x+Ampl_lockin_y*Ampl_lockin_y)
Ampl_lockin_as = np.append(Ampl_lockin_as, Ampl_lockin_a)
Ampl_lockin = np.mean(Ampl_lockin_a)/np.mean(mdata[int(samplerate*10):,3])
Ampl_lockins = np.append(Ampl_lockins, Ampl_lockin)
phase = np.arctan2(Ampl_lockin_y,Ampl_lockin_x)*180/np.pi
phases = np.append(phases, phase)
print('Continously record data for %.3f seconds. \nThe shape of the data is %s.' %(runtime, np.shape(mdata)))
print('%s' %(savename+"_m"+str(movieN)))
print("Frequency is %d Hz, amplitude is %d mV, scanrate is %d mV/s. Done\n" %(m_freq,m_ampl,scanrate))
# savefileandpath = (saveloc+"\\"+savename+"_m"+str(movieN))
# # Get and save measured data:
# mdata = np.array(taskM.a).reshape(-1,taskM.inputchannelsN)
  
# ## STEP 6: plot the output to check if measurement was successful

# DAC=np.load(saveloc+"\\"+savename+"_m"+str(movieN)+".npy")

lockinx = (mdata[int(samplerate*0):,2])
lockiny =(mdata[int(samplerate*0):,4])
lockin = np.sqrt(lockinx*lockinx+lockiny*lockiny)
C = (mdata[int(samplerate*0):,1])/10
V =  (mdata[int(samplerate*0):,0])
pd =  (mdata[int(samplerate*0):,3])
# try:
#     phase2 =  (mdata[int(samplerate*0):,5])
# except:
#     pass
pds = np.append(pds, np.mean(pd))
currents = np.append(currents, np.mean(abs(C)))
phase =np.arctan2(lockiny,lockinx)*180/np.pi
fig, ax = plt.subplots(figsize=(16,5))
#%matplotlib qt
ax.plot(lockin[::10], 'r',label= 'lockinR')
ax.plot(V[::10]-1)
ax2= ax.twinx()
#ax2.plot(lockinR, 'b', label ='lockin')
ax2.plot(C[::10]-2)
ax2.set_ylim(None,1)
ax.legend(["Frequency= %d Hz\n Amplitude =  %d mV\n scanrate = %d mV/s\nave=%.3f" %(m_freq,m_ampl,scanrate, Ampl_lockin)], loc = 'upper right', fontsize =20)
plt.show()

fig, ax = plt.subplots(figsize=(16,5))
#%matplotlib qt
ax.plot(lockin[::10], 'r',label= 'lockinR')
ax2= ax.twinx()
#ax2.plot(lockinR, 'b', label ='lockin')
ax2.plot(phase[::10])
# ax2.plot(phase2[::10]*180/10)
ax2.set_ylim(None,None)
ax.legend(["Frequency= %d Hz\n Amplitude =  %d mV\n scanrate = %d mV/s" %(m_freq,m_ampl,scanrate)], loc = 'best', fontsize =20)
plt.show()

fig, ax = plt.subplots(figsize=(16,5))
#%matplotlib qt
ax.plot(pd[::10], 'r',label= 'PD intensity')
ax2= ax.twinx()
#ax2.plot(lockinR, 'b', label ='lockin')
ax2.plot(lockin[::10]-2, 'r',label= 'lockinR')
ax2.plot(V[::10]-2)
ax2.set_ylim(None,4)
ax.legend(["Frequency= %d Hz\n Amplitude =  %d mV\n scanrate = %d mV/s\nave=%.3f" %(m_freq,m_ampl,scanrate, Ampl_lockin)], loc = 'upper right', fontsize =20)
plt.show()

 # ## STEP 5: save the log file and the config file in the same directory as data

del lockinx 
del lockiny 
del lockin 
del C 
del V 
del pd
del mdata
fig, ax = plt.subplots(figsize=(10,5))
ax.plot(pds, 'k')
ax2= ax.twinx()
ax2.plot(currents, 'b')    
print("Frequency run is done")    
fig, ax = plt.subplots(figsize=(10,5))
ax.plot(Ampl_lockins, 'r')
ax.plot(Ampl_lockin_as/np.mean(pds), 'g')
# ax.plot(pds/3, 'k')
ax2= ax.twinx()
ax2.plot((phases), 'b')


