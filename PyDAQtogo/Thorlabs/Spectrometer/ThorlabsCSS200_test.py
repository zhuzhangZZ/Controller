
# -*- coding: utf-8 -*-
"""
Example of C Libraries for CCS Spectrometers in Python with CTypes
Author: Zhu Zhang <z.zhang@uu.nl>
Copy from 
https://github.com/Thorlabs/Light_Analysis_Examples/blob/main/Python/Thorlabs%20CCS%20Spectrometers/CCS%20using%20ctypes%20-%20Python%203.py

"""
    
#%%
import PyDAQtogo.config as config
import PyDAQtogo.NIDAQforPDSM as daq
import PyDAQtogo.SRSLockinAmplifier as SRS
import PyDAQtogo.ThorlabsCSS200_Driver as spectrum
import PyDAQtogo.ProgressBar as PB

import numpy as np
import matplotlib.pyplot as plt
import time
import math
import csv
import os
from datetime import date
import tqdm
import matplotlib as mpl
#Set the imitation in the number of points in the backend Agg.
mpl.rcParams['agg.path.chunksize'] = 100000
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
saveloc = 'C:\\Data\\Zhu\\Spectrometer\\2022-12-19-22_spectrum_100mMKCl+15mMFe(MeOH)2'
if not os.path.exists(saveloc):
    os.mkdir(saveloc)
    print("Directory " , saveloc ,  " Created ")
else:    
    print("Directory " , saveloc ,  " already exists")

savename = "ACV57"
try:
    del movieN
except:
    pass

#%%

v_min = -200
v_max = 400

#m_freqs = [10, 25, 50, 75, 100, 150, 200, 300, 500, 750, 1000]
# m_freqs = [ 10, 25, 45, 75, 95,  190, 300, 400, 500,750, 975][::-1]
m_freqs = [ 95]
# m_ampls = [105, 95, 85, 75, 65, 55 , 45, 35, 25 , 15][::-1]
m_ampls = [50]
# m_ampls = [100, 90, 80,  70, 60, 50, 40, 30, 20, 10][::-1]
# m_ampls = [150, 130,120,110,100, 90, 80,  70, 60, 50, 40, 30, 20, 10][::-1]
Extra_amp = 0 
# scanrates = [100, 90, 80, 70, 60, 50, 40, 30, 25, 20 , 15, 10][::-1]
# scanrates = [150,  130, 110, 100, 90, 80, 70, 60, 50, 40, 30, 20 ]
# scanrates = [150,  130, 110, 100, 90, 80, 70, 60, 50, 40 ]
scanrates = [80]
spectrums =  np.empty((0, 3648), float)
currents = np.array([])
# ofs = np.append( np.arange(-300,400, 35), np.arange(-300,400, 35)[::-1])

# ofs = np.append( aa, np.arange(-300,400, 35))
# ofs =  np.array(np.arange(-300,400, 35))+25
ofs =[0, 0, 0, 0, 0]
# ofs =  np.array(np.arange(60,80, 1))
if len(ofs)>10 or len(m_ampls)> 6 or len(m_freqs)>6:
    longscan = False
else:
    longscan = True

longscan = False
if longscan ==True:
    ofs =[-600]
    # m_freqs = [ 275]
i=0
sleep= 0
spectrumName = savename
integTime =2E-3 #s
method = ["Time", "cycles"][0]
cycles = 150
runtime = 10
rt = runtime
for of in tqdm.tqdm(ofs, desc = "Offset"):
    for m_freq in tqdm.tqdm(m_freqs, desc = "Frequency"):
        for scanrate in tqdm.tqdm(scanrates, desc = "ScanRates"):
            for m_ampl in tqdm.tqdm(m_ampls, desc = "Amplitudes", bar_format='{desc:<15}{percentage:3.0f}%|{bar:30}{r_bar}', colour  = 'green'):
                
                time_start=time.time()
                """CV : choose 0 or 1, 0 just do sine oscillation, 1 do AC voltammetry`
                   reverse: 1 or -1, 1 not reverse when use dualPicostat, 1 reverse for Picostat with range of larger current input 
                   have tested the pico, the voltage output to cell is correct, the output to daq is reserved """
                ## STEP 3.0: Sine Modulation  
                taskMod = daq.StepSinGenerator(step =2*1e-3,m_freq=m_freq,m_ampl=m_ampl+ Extra_amp,v_min= v_min,v_max=v_max,v_scanRate=scanrate, CV=0,offset=of,reverse=1)
                taskM = daq.MeasureTask(m_freq, rt)
                taskMod.StartTask()
                taskM.StartTask()
                wavelengths, spectrumArray =\
                    spectrum.runSpectrum(save= True, method = method, runTime = rt, cycles=cycles, \
                                         integTime = integTime, savename = spectrumName, saveloc = saveloc )

                # PB.ShowBar(Barname = "ScanProgress", runtime = rt)
                try:
                    taskMod.StopTask()
                except:
                    pass
                taskMod.ClearTask()
                
                
          #####  STEP 3.1: Voltage Scan
            ###===================================================================###################     
                if longscan ==True:
                    
                    taskG = daq.StepSinGenerator(step =2*1e-3, m_freq=m_freq, m_ampl=m_ampl,v_min= v_min, v_max=v_max,v_scanRate=scanrate, CV=1, reverse=1)
                    taskG.StartTask()
                                        
                    # time.sleep((v_max-v_min)/scanrate*2*4+1)
                    PB.ShowBar(Barname = "CVScan", runtime = abs(v_max-v_min)/scanrate*2*10+1) 
                    try:
                        taskG.StopTask()
                    except:
                        pass
                    taskG.ClearTask()
                    
                  ## STEP 3.2: back to  Sine Modulation  
                ###===================================================================###################     
                    taskModEnd = daq.StepSinGenerator(step =2*1e-3,m_freq=m_freq,m_ampl=m_ampl+Extra_amp,v_min= v_min,v_max=v_max,v_scanRate=scanrate, CV=0,offset=of,reverse=1)
                    taskModEnd.StartTask()
                    PB.ShowBar(Barname = "ScanProgress", runtime = rt)
                    try:
                        taskModEnd.StopTask()
                    except:
                        pass
                    taskModEnd.ClearTask()
                    figuresave = True   
                else:
                    figuresave = False
                
           ###===================================================================###################   
                try:
                    taskM.StopTask()
                except:
                    pass
                taskM.ClearTask()
                time_stop=time.time()
                runtime=time_stop-time_start
                
                ## STEP 4: readout the data from DAQ and store it in proper format
            #sn = None
                try:
                    movieN += 1
                except:
                    movieN = 0
                    sn = savename
                savefileandpath = (saveloc+"\\"+savename+"_m"+str(movieN))
                
             ## STEP 5: save the log file and the config file in the same directory as data
               
                param['Measurement']['v_offset'] = int(of)
                param['Measurement']['v_scanRate'] = scanrate
                param['Measurement']['a_modulate'] = m_ampl
                param['Measurement']['f_modulate'] = m_freq
                param['Measurement']['v_max'] = v_max
                param['Measurement']['v_min'] = v_min
                try:
                    param['Measurement']['v_step'] = int(ofs[1]-ofs[0])
                except:
                    param['Measurement']['v_step'] = 0
                config.save_config( param,saveloc+"\\"+savename+"_m"+str(movieN))
                
                # Get and save measured data:
                mdata = np.array(taskM.a).reshape(-1,taskM.inputchannelsN)
                np.save(savefileandpath, mdata)
                if m_freq > 400:
                    samplerate = 100.0*m_freq  # maxmium sampling rate is 400K in total(all channel combined)
                    if m_freq>800:
                        samplerate = 80.0*m_freq
                        if m_freq>1000:
                            samplerate = 20.0*m_freq   
                else:
                    samplerate = 100.0*m_freq 

                ## STEP 6.0: plot the output to check if measurement was successful
                if len(ofs)>15:
                    ave_t = 1
                else:
                    ave_t = 10
                
                
                print('Continously record data for %.3f seconds. \nThe shape of the data is %s.' %(runtime, np.shape(mdata)))
                print('%s' %(savename+"_m"+str(movieN)))
                print("Frequency is %d Hz, amplitude is %d mV, scanrate is %d mV/s, offset is %d mV. Done" %(m_freq,m_ampl,scanrate,of))
                # savefileandpath = (saveloc+"\\"+savename+"_m"+str(movieN))
                # # Get and save measured data:
                # ## STEP 6.1: plot the output to check if measurement was successful
            
                C = (mdata[int(samplerate*0):,1])
                V =  (mdata[int(samplerate*0):,0])
                currents = np.append(currents, np.mean(abs(C)))
                spectrums = np.append(spectrums, np.array([np.mean(spectrumArray, axis=0)]),axis=0)
                fig, ax = plt.subplots(figsize=(10,4))
                ax.plot(V[::10], color ='r')
                ax2= ax.twinx()
                #ax2.plot(lockinR, 'b', label ='lockin')
                
                ax2.plot(C[::10], color = 'b')
                ax.set_ylabel("Voltage", color= 'r', fontsize = 15)
                ax2.set_ylabel("Currents", color= 'b', fontsize = 15)
                # ax.legend(["Freq= %d Hz\n Amp. =  %d mV\n scanrate = %d mV/s\nave=%.3f" 
                #            %(m_freq,m_ampl,scanrate, Ampl_lockin)], loc = 'upper right', fontsize =15).set_zorder(5)
                plt.show()
                if figuresave == True:
                    figs_name = saveloc+"\\"+savename+"_m"+str(movieN) 
                    fig.savefig(fname = figs_name+ "CV.png", dpi=600, format='png') 

                fig, ax = plt.subplots(figsize =(15,6))
                ax.fill_between(wavelengths, np.min(spectrumArray, axis=0), np.max(spectrumArray, axis=0), alpha =0.5)
                
                ax.plot(wavelengths, np.mean(spectrumArray, axis = 0), color = 'r', lw =1)
                ax.set_xlabel("Wavelength [nm]", fontsize =30)
                ax.set_ylabel("Intensity [a.u.]", fontsize =30)
                ax.set_xticks(np.arange(200,1100, 20))
                ax.grid(True)
                ax.set_xlim(400, 950)
                ax.legend(["Freq= %d Hz\n Amp. =  %d mV\n scanrate = %d mV/s\noffset =%d mV" 
                           %(m_freq,m_ampl,scanrate, of)], loc = 'upper right', fontsize =15).set_zorder(5)
                plt.show()
                time.sleep(sleep)
                # del lockinx; lockiny; lockin; C; V; pd; mdata; figuresave
               
# np.save(saveloc+"\\"+"wavelengths", wavelengths)

taskI = daq.InitialOutput()
taskI.StartTask()
taskI.StopTask()
taskI.ClearTask()

if len(m_freqs) > 5:
    x_plot = np.array(m_freqs); x_label = 'Frequency [Hz]'
    figs_name = saveloc+"\\"+savename+"_m"+str(movieN) + "_Freq_Scan_"
elif len(ofs)>15:
    x_plot = np.array(ofs); x_label = 'Offset [mV]'
    figs_name = saveloc+"\\"+savename+"_m"+str(movieN) + "_Offset_Scan_"
elif len(m_ampls)>5:
    x_plot = np.array(m_ampls); x_label = 'Modul Ampl. [mV]'
    figs_name = saveloc+"\\"+savename+"_m"+str(movieN) + "_Amp_Scan_"  
elif len(scanrates)>5:
    x_plot = np.array(scanrates); x_label = 'scanrates [mV/s]'
    figs_name = saveloc+"\\"+savename+"_m"+str(movieN) + "_Amp_Scan_"  
else:
    x_plot = np.array([1]); x_label = 'Modul Ampl. [mV]'
    figs_name = saveloc+"\\"+savename+"_m"+str(movieN) + "_Continueous_" 
fig, ax = plt.subplots(figsize=(10,5))

ax2= ax.twinx()
ax2.plot( currents, 'b')   
ax.set_ylabel("PD Intensity", color= 'k', fontsize = 30)
ax.set_xlabel('counts','', color= 'k', fontsize = 30)
ax2.set_ylabel("Currents", color= 'b', fontsize = 30)
fig.savefig(fname = figs_name+ "pds.png", dpi=600, format='png') 
print("Frequency run is done")    

fig, ax = plt.subplots(figsize=(10,5))
ax2= ax.twinx()
for i in np.arange(spectrums.shape[0]):
    ax2.plot(wavelengths,  spectrums[i,:]+ i*(1/spectrums.shape[0]))   
ax.set_ylabel(" Counts", color= 'k', fontsize = 30)
ax.set_xlabel('wavelengths','', color= 'k', fontsize = 30)
ax2.set_ylabel("Counts", color= 'b', fontsize = 30)
fig.savefig(fname = figs_name+ "pds.png", dpi=600, format='png') 
ax.set_xticks(np.arange(200,1100, 20))
ax.grid(True)
ax.set_xlim(300, 850)
print("Frequency run is done")    



#%%


#%%


import time
import numpy as np
import  matplotlib . pyplot  as  plt
import ThorlabsCSS200 as spectrum


wavelengths, spectrumArray =\
spectrum.runSpectrum(save= True, method = "Time", runTime = 10, cycles=500, integTime = 2E-3, savename = 'darkcounts', saveloc = "C:\\Data\\Zhu\\Spectrometer"  )

fig, ax = plt.subplots(figsize =(15,6))
ax.fill_between(wavelengths, np.min(spectrumArray, axis=0), np.max(spectrumArray, axis=0), alpha =0.5)

ax.plot(wavelengths, np.mean(spectrumArray, axis = 0), color = 'r', lw =1)
ax.set_xlabel("Wavelength [nm]", fontsize =30)
ax.set_ylabel("Intensity [a.u.]", fontsize =30)
ax.set_xticks(np.arange(200,1100, 20))
ax.grid(True)
ax.set_xlim(400, 950)
plt.show()
