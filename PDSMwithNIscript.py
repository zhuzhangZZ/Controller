# -*- coding: utf-8 -*-
"""
Script for measuring and displaying potentiodynamic measurements controlled by a NIDAQ card

- Optical signal is obtained from a lock-in amplifier reading out a photodetector
- Reference signal for the lock-in and all waveforms for the potential are set by NIDAQ card
- The current through the cell is measured by an EDAQ potentiostat, but values are read out is through NIDAQ
Use the NI DAQ generate triangle + sine wavefoem for AC cyclic voltammatry,
and read data from edaq and photodiode

Annlog Output0(tri+sine) is sent to potentialstat, 
Analog Output1(sine) is sent to lockin-Amp. to server as a reference signal
AI0 is the voltage from EDaq which is the potential of CV
AI1 is the current from EDaq which is the Redox current of CV 
AI2 is the voltage from lockin X output
AI3 is the voltage from FEMTO photodiode which is the potential modulated optical signal
AI4 is the voltage from lockin Y output
AI5 is the voltage from lockin phase output(optional: just for checking)
Last modified Nov 10, 2021
@author: Zhu Zhang z.zhang@uu.nl
+ contributor: Sanli Faez s.faez@uu.nl

"""
import PyDAQtogo.config as config
import PyDAQtogo.NIDAQforPDSM as daq

import numpy as np
import matplotlib.pyplot as plt
import time
import math
import csv
from datetime import date
import os
import PyDAQtogo.HPWaveGen as HPWaveGen

import matplotlib as mpl
mpl.rcParams['agg.path.chunksize'] = 1000000
## STEP 1: read parameters from a config file

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
saveloc = 'C:\\Data\\Zhu\\PDSMwithNI\\2022-02-10_nanohole_Cr_Au_100mKCl_modulation'
if not os.path.exists(saveloc):
    os.mkdir(saveloc)
    print("Directory " , saveloc ,  " Created ")
else:    
    print("Directory " , saveloc ,  " already exists")

savename = "ACV1"

try:
    del movieN
except:
    pass

#%%
#m_freqs = [10, 25, 50, 75, 100, 150, 200, 300, 500, 750, 1000]
m_freqs = [ 10, 25,   45, 75, 95, 160, 210, 300, 400, 500, 750, 1000]
m_freqs = [ 75]
m_ampls = [150, 135, 120, 105, 90, 75, 60 , 45, 30, 25, 10][::-1]
# m_ampls = [150,140,130,120, 110, 100, 90, 80, 70, 60 , 50][::-1]
#m_ampls = [105, 85,  65, 45, 25 , 15]
m_ampls = [75]
#
#scanrates = [100, 90, 80, 70, 60, 0, 40,30, 25, 20 , 15, 10][::-1]
scanrate = 20
# ofs =np.append( np.arange(-250,250, 25)[::-1], np.arange(-250,250, 25))
ofs = np.append( np.arange(-400,400, 25), np.arange(-400,400, 25)[::-1])
ofs = np.arange(-400,300, 25)
ofs =[0]
Ampl_lockins = np.array([]); phases = np.array([])
Ampl_lockin_as = np.array([]); pds = np.array([])
currents = np.array([])

for of in ofs:
    for m_freq in m_freqs:
            
        for m_ampl in m_ampls:
    
            """CV : choose 0 or 1, 0 just do sine oscillation, 1 do AC voltammetry`
               reverse: 1 or -1, 1 not reverse when use dualPicostat, -1 reverse for Picostat with range of larger current input 
               have tested the pico, the voltage output to cell is correct, the output to daq is reserved"""
            taskG = daq.StepSinGenerator(step =2*1e-3,m_freq=m_freq,m_ampl=m_ampl,v_min= v_min,v_max=v_max,v_scanRate=scanrate, CV=0,offset=of,reverse=1)
            taskM = daq.MeasureTask(m_freq)
            
            try:
                wgen = HPWaveGen.HP33120A(COMPort='COM6')
            except:
                print("The HP33120A is alreday opended!")
            time.sleep(0.5)
            wgen.CLS()
            time.sleep(0.5)
            wgen.control(control = 'remote')
            time.sleep(1)
            wgen.shape('sin')
            wgen.voltage(amplitude= m_ampl*1e-3)
            wgen.offset(offset=of*1e-3)
            
            wgen.frequency(freq = m_freq)
            
            time.sleep(1)
            wgen.query_frequency()
            wgen.query_error()
        ## STEP 3: start the measurement
         
            taskG.StartTask()
            taskM.StartTask()
            time_start=time.process_time()
        #    PressStop=input('Acquiring samples continuously. Press Enter to interrupt\n')
            
#            time.sleep((v_max-v_min)/scanrate*2*5+1)
            time.sleep(100)
            time_stop=time.process_time()
            runtime=time_stop-time_start
            taskG.StopTask()
            taskM.StopTask()
            taskM.ClearTask()
            taskG.ClearTask()
            taskZ = daq.ZeroOutput()
            taskZ.StartTask()
            taskZ.StopTask()
            taskZ.ClearTask()
            
            wgen.voltage(amplitude= 0.05)
            wgen.control(control = 'local')
            
            ## STEP 4: readout the data from DAQ and store it in proper format
       
            try:
                movieN += 1
                
            except:
                movieN = 0
                sn = savename
                                    
            savefileandpath = (saveloc+"\\"+savename+"_m"+str(movieN))
            # Get and save measured data:
            mdata = np.array(taskM.a).reshape(-1,taskM.inputchannelsN)
            if m_freq > 400:
                samplerate = 100.0*m_freq  # maxmium sampling rate is 400K in total(all channel combined)
                if m_freq>800:
                    samplerate = 80.0*m_freq
            else:
                samplerate = 100.0*m_freq 
            ## STEP 5: save the log file and the config file in the same directory as data
            np.save(savefileandpath, mdata)
            
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
            print("Frequency is %d Hz, amplitude is %d mV, offset is %d mV. Done\n" %(m_freq,m_ampl,of))
            
        
            DAC=np.load(saveloc+"\\"+savename+"_m"+str(movieN)+".npy")
            
            lockinx = DAC[:,2]
            lockiny = DAC[:,4]
            lockin = np.sqrt(lockinx*lockinx+lockiny*lockiny)
            C = -DAC[:,1]
            V = -DAC[:,0]
            pd = DAC[:,3]
            # try:
            #     phase2 =  DAC[:,5]
            # except:
            #     pass
            pds = np.append(pds, np.mean(pd))
            currents = np.append(currents, np.mean(abs(C)))
            phase =np.arctan2(lockiny,lockinx)*180/np.pi
            fig, ax = plt.subplots(figsize=(16,5))
            #%matplotlib qt
            ax.plot(lockin[::10], 'r',label= 'lockinR')
            ax2= ax.twinx()
            #ax2.plot(lockinR, 'b', label ='lockin')
            ax2.plot(C[::10])
            ax2.set_ylim(None,1)
            ax.legend(["Frequency= %d Hz\n Amplitude =  %d mV\n Offset = %d mV\nave=%.3f" %(m_freq,m_ampl,of, Ampl_lockin)], loc = 'upper right', fontsize =20)
            plt.show()
            
            fig, ax = plt.subplots(figsize=(16,5))
            #%matplotlib qt
            ax.plot(lockin[::10], 'r',label= 'lockinR')
            ax2= ax.twinx()
            #ax2.plot(lockinR, 'b', label ='lockin')
            ax2.plot(phase[::10])
            # ax2.plot(phase2[::10]*180/10)
            ax2.set_ylim(None,None)
            ax.legend(["Frequency= %d Hz\n Amplitude =  %d mV\n Offset = %d mV" %(m_freq,m_ampl,of)], loc = 'best', fontsize =20)
            plt.show()
            
            fig, ax = plt.subplots(figsize=(16,5))
            #%matplotlib qt
            ax.plot(pd[::10], 'r',label= 'PD intensity')
            ax2= ax.twinx()
            #ax2.plot(lockinR, 'b', label ='lockin')
            ax2.plot(V[::10]-2)
            ax2.set_ylim(None,1)
            ax.legend(["Frequency= %d Hz\n Amplitude =  %d mV\n Offset = %d mV\nave=%.3f" %(m_freq,m_ampl,of, Ampl_lockin)], loc = 'upper right', fontsize =20)
            plt.show()
            time.sleep(5)
            if of == 200:
                time.sleep(120)

    
print("Frequency run is done")   
fig, ax = plt.subplots(figsize=(10,5))
ax.plot(Ampl_lockins, 'r')
ax.plot(Ampl_lockin_as/np.mean(pds), 'g')
# ax.plot(pds/3, 'k')
ax2= ax.twinx()
ax2.plot((phases), 'b')
# ax.set_ylim(0,0.4) 

fig, ax = plt.subplots(figsize=(10,5))
ax.plot(pds, 'k')
ax2= ax.twinx()
ax2.plot(currents, 'b')

wgen.close()
#%%


#%%

#%%

