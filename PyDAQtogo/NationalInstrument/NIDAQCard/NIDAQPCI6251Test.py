# -*- coding: utf-8 -*-
"""
Created on Wed Feb 23 00:39:22 2022

@author: PDSM
"""

import PyDAQtogo.config as config
import PyDAQtogo.NIDAQPCI6251_Driver as daq
# import PyDAQtogo.SRSLockinAmplifier as SRS

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
saveloc = 'C:\\Data\\Zhu\\PDSMwithNI\\2022-12-03_PCITest'
if not os.path.exists(saveloc):
    os.mkdir(saveloc)
    print("Directory " , saveloc ,  " Created ")
else:    
    print("Directory " , saveloc ,  " already exists")

savename = "ACV2"

try:
    del movieN
    
except:
    pass

#%%
v_min = -50
v_max = 50

#m_freqs = [10, 25, 50, 75, 100, 150, 200, 300, 500, 750, 1000]
# m_freqs = [ 10, 25, 45, 75, 95, 160, 210, 300, 400, 500,750, 1000]
m_freq = 800
# m_ampls = [105, 95, 85, 75, 65, 55 , 45, 35, 25 , 15][::-1]
#m_ampls = [105, 85,  65, 45, 25 , 15]
m_ampl = 50
Extra_amp = 0 
# scanrates = [100, 90, 80, 70, 60, 50, 40, 30, 25, 20 , 15, 10][::-1]
# scanrates = [100, 90, 80, 70, 60, 50, 40, 30, 20 , 10][::-1]
scanrates = [200]

Tcs = ['1 s', '300 ms', '100 ms', '30 ms']
sens = ['10 mV/nA', '5 mV/nA',    '10 mV/nA',    '50 mV/nA',    '200 mV/nA']
Ampl_lockins = np.array([]); phases = np.array([])
Ampl_lockin_as =np.array([]); pds = np.array([])
currents = np.array([])
of = 50
i=0

try:
    taskMod.StopTask()
    taskMod.ClearTask()
    time.sleep(1)
except:
    pass
    
rt =1/m_freq*5
time_start=time.process_time()
"""CV : choose 0 or 1, 0 just do sine oscillation, 1 do AC voltammetry`
   reverse: 1 or -1, 1 not reverse when use dualPicostat, 1 reverse for Picostat with range of larger current input 
   have tested the pico, the voltage output to cell is correct, the output to daq is reserved """
taskMod = daq.StepSinGenerator(step =2*1e-3,m_freq=m_freq,m_ampl=m_ampl+ Extra_amp,v_min= v_min,v_max=v_max,v_scanRate=scanrate, CV=0,offset=of,reverse=1)

taskMod.StartTask()

#%%
rt =1/m_freq*200

taskM = daq.MeasureTask(m_freq, rt)
taskM.StartTask()
# PB.ShowBar(Barname = "ScanProgress", runtime = rt)
time.sleep(rt)
taskM.StopTask()
taskM.ClearTask()


mdata = np.array(taskM.a).reshape(-1,taskM.inputchannelsN)
# np.save(savefileandpath, mdata)
if m_freq > 400:
    samplerate = 100.0*m_freq  # maxmium sampling rate is 400K in total(all channel combined)
    if m_freq>800:
        samplerate = 80.0*m_freq
        if m_freq>1500:
                    samplerate = 50.0*m_freq
else:
    samplerate = 100.0*m_freq 
## STEP 5: save the log file and the config file in the same directory as data


## STEP 6: plot the output to check if measurement was successful


# savefileandpath = (saveloc+"\\"+savename+"_m"+str(movieN))
# # Get and save measured data:
# mdata = np.array(taskM.a).reshape(-1,taskM.inputchannelsN)
  
# ## STEP 6: plot the output to check if measurement was successful
        
# DAC=np.load(saveloc+"\\"+savename+"_m"+str(movieN)+".npy")


C = (mdata[int(samplerate*0):int(samplerate*rt),1])
V =  (mdata[int(samplerate*0):int(samplerate*rt),0])
C0 = (mdata[int(samplerate*0):,1])
V0 =  (mdata[int(samplerate*0):,0])
# try:
#     phase2 =  (mdata[int(samplerate*0):,5])
# except:
#     pass
   
fig, ax = plt.subplots(figsize=(16,8))
#%matplotlib qt
ax.plot(C, 'r',label= 'lockinR')
 
ax2= ax.twinx()
ax2.plot(V, 'b', label ='lockin')
fig, ax = plt.subplots(figsize=(16,8))
#%matplotlib qt
ax.plot(C0, 'r',label= 'lockinR')
 
ax2= ax.twinx()
ax2.plot(V0, 'b', label ='lockin')


#%%

v_min = -50
v_max = 50

#m_freqs = [10, 25, 50, 75, 100, 150, 200, 300, 500, 750, 1000]
# m_freqs = [ 10, 25, 45, 75, 95, 160, 210, 300, 400, 500,750, 1000]
m_freqs = [10000]
# m_ampls = [105, 95, 85, 75, 65, 55 , 45, 35, 25 , 15][::-1]
#m_ampls = [105, 85,  65, 45, 25 , 15]
m_ampls = [5]
Extra_amp = 0 
# scanrates = [100, 90, 80, 70, 60, 50, 40, 30, 25, 20 , 15, 10][::-1]
# scanrates = [100, 90, 80, 70, 60, 50, 40, 30, 20 , 10][::-1]
scanrates = [200]

Tcs = ['1 s', '300 ms', '100 ms', '30 ms']
sens = ['10 mV/nA', '5 mV/nA',    '10 mV/nA',    '50 mV/nA',    '200 mV/nA']
Ampl_lockins = np.array([]); phases = np.array([])
Ampl_lockin_as =np.array([]); pds = np.array([])
currents = np.array([])
of = 50
i=0
for m_freq in tqdm.tqdm(m_freqs, desc = "Frequency"):
    for m_ampl in tqdm.tqdm(m_ampls, desc = "Amplitudes",bar_format='{desc:<15}{percentage:3.0f}%|{bar:30}{r_bar}', colour  = 'green', nrows  = 40):
        for scanrate in tqdm.tqdm(scanrates, desc = "ScanRates"):
            
            # lockinA.time_constant(Tc = Tcs[i])
            # lockinA.sensitivity(sen = sens[0])
            # time.sleep(2)
            # i +=1
            
            rt =1/m_freq*100
            
            """CV : choose 0 or 1, 0 just do sine oscillation, 1 do AC voltammetry`
               reverse: 1 or -1, 1 not reverse when use dualPicostat, 1 reverse for Picostat with range of larger current input 
               have tested the pico, the voltage output to cell is correct, the output to daq is reserved """
            taskMod = daq.StepSinGenerator(step =2*1e-3,m_freq=m_freq,m_ampl=m_ampl+ Extra_amp,v_min= v_min,v_max=v_max,v_scanRate=scanrate, CV=0,offset=of,reverse=1)
            taskMod.StartTask()
            time.sleep(5)
            taskM = daq.MeasureTask(m_freq, rt)
            time_start=time.time()
            taskM.StartTask()
            # PB.ShowBar(Barname = "ScanProgress", runtime = rt)
            time.sleep(rt)
            
           
            
        ## STEP 3: start the measurement
        ###===================================================================###################     
        #     taskG = daq.StepSinGenerator(step =2*1e-3, m_freq=m_freq, m_ampl=m_ampl,v_min= v_min, v_max=v_max,v_scanRate=scanrate, CV=1, reverse=1)
        #     taskG.StartTask()
            
            
        # #    PressStop=input('Acquiring samples continuously. Press Enter to interrupt\n')
            
        #     # time.sleep((v_max-v_min)/scanrate*2*4+1)
        #     PB.ShowBar(Barname = "CVScan", runtime = (v_max-v_min)/scanrate*2*1+1) 
            
        #     taskG.StopTask()
        #     taskG.ClearTask()
            
            
            # taskModEnd = daq.StepSinGenerator(step =2*1e-3,m_freq=m_freq,m_ampl=m_ampl+Extra_amp,v_min= v_min,v_max=v_max,v_scanRate=scanrate, CV=0,offset=of,reverse=1)
            # taskModEnd.StartTask()
            # # PB.ShowBar(Barname = "ScanProgress", runtime = rt)
            # time.sleep(rt)
            # taskModEnd.StopTask()
            # taskModEnd.ClearTask()
            
            taskM.StopTask()
            taskM.ClearTask()
            time_stop=time.time()
            
            taskMod.StopTask()
            taskMod.ClearTask()
           
       ###===================================================================###################   
            
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
                sn = savename
            savefileandpath = (saveloc+"\\"+savename+"_m"+str(movieN))
            
          
            
            # config.save_config( param,saveloc+"\\"+savename+"_m"+str(movieN))
            
            # Get and save measured data:
            mdata = np.array(taskM.a).reshape(-1,taskM.inputchannelsN)
            # np.save(savefileandpath, mdata)
            if m_freq > 400:
                samplerate = 100.0*m_freq  # maxmium sampling rate is 400K in total(all channel combined)
                if m_freq>800:
                    samplerate = 80.0*m_freq
            else:
                samplerate = 100.0*m_freq 
            ## STEP 5: save the log file and the config file in the same directory as data
            
            
            ## STEP 6: plot the output to check if measurement was successful

            
            # savefileandpath = (saveloc+"\\"+savename+"_m"+str(movieN))
            # # Get and save measured data:
            # mdata = np.array(taskM.a).reshape(-1,taskM.inputchannelsN)
              
            # ## STEP 6: plot the output to check if measurement was successful
                    
            # DAC=np.load(saveloc+"\\"+savename+"_m"+str(movieN)+".npy")
            
            
            C = (mdata[int(samplerate*0):int(samplerate*rt),1])
            V =  (mdata[int(samplerate*0):int(samplerate*rt),0])
            C0 = (mdata[int(samplerate*0):,1])
            V0 =  (mdata[int(samplerate*0):,0])
            # try:
            #     phase2 =  (mdata[int(samplerate*0):,5])
            # except:
            #     pass
           
            fig, ax = plt.subplots(figsize=(16,8))
            #%matplotlib qt
            ax.plot(C, 'r',label= 'lockinR')
         
            ax2= ax.twinx()
            ax2.plot(V, 'b', label ='lockin')
            fig, ax = plt.subplots(figsize=(16,8))
            #%matplotlib qt
            ax.plot(C0, 'r',label= 'lockinR')
         
            ax2= ax.twinx()
            ax2.plot(V0, 'b', label ='lockin')
            print('rt is %f' %rt)
            print('runtime is %f' %runtime)
            print(samplerate*rt)

# fig, ax = plt.subplots(figsize=(10,5))
# ax.plot(pds, 'k')
# ax2= ax.twinx()
# ax2.plot(currents, 'b')    
# print("Frequency run is done")    
# fig, ax = plt.subplots(figsize=(10,5))
# ax.plot(Ampl_lockins, 'r')
# ax.plot(Ampl_lockin_as/np.mean(pds), 'g')
# # ax.plot(pds/3, 'k')
# ax2= ax.twinx()
# ax2.plot((phases), 'b')


