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
AI3 is the voltage from lockin
AI4 is the voltage from FEMTO photodiode which is the potential modulated optical signal
Last modified April 10, 2021
@author: Zhu Zhang z.zhang@uu.nl
+ contributor: Sanli Faez s.faez@uu.nl

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
saveloc = 'C:\\Data\\Zhu\\PDSMwithNI\\2024-04-26_Au_20nm_LiClO4'
if not os.path.exists(saveloc):
    os.mkdir(saveloc)
    print("Directory " , saveloc ,  " Created ")
else:    
    print("Directory " , saveloc ,  " already exists")

savename = "ACV22_with_voltage_lock_notch_filter_150nmhole_amplitude_scan"
try:
    del movieN
except:
    pass


#%%
try:
    lockinA = SRS.SR830(COMPort='ASRL8::INSTR', timeout=5000)
except:
    print("The SR830 is alreday opended!")
lockinA.CLS()       
# lockin.control(control = 'remote')

lockinA.reference_source(ref_source="external")
lockinA.reference_phase_shift(ref_phase=0)
lockinA.reference_trigger(ref_tri = 'sin')
lockinA.harmonic( harm = 1)

lockinA.input_config(input_value= "A")
# lockin.lockin.write("ISRC 1") 
lockinA.input_coupling(coupling_value="AC")
lockinA.input_shield(shield_value= "ground")
lockinA.input_filter(filter_value= "0-0")

lockinA.time_constant(Tc = "3 s")
# lockinA.time_constant(Tc = "10 ms")
# lockinA.sensitivity(sen = '500 uV/pA')
lockinA.sensitivity(sen = '5 mV/nA')
lockinA.filter_slope(filter_slope= "24")
lockinA.reserve_mode(reserve_mode= "high")
lockinA.sync_filter(sync_filter="True")
lockinA.CH1_display(display1= "R")
lockinA.out_offset_exp(output='R')
lockinA.CH2_display(display2= "Theta")

lockinA.front_output1(output1="display")
lockinA.front_output2(output2="Y")
time.sleep(4)

v_min = -500
v_max = 300

#m_freqs = [10, 25, 50, 75, 100, 150, 200, 300, 500, 750, 1000]
# m_freqs = [1, 2.5, 4.5, 10, 25, 45, 75, 95,  190, 300, 400, 500, 750, 975][::-1]
m_freqs = [ 35]
# m_ampls = [105, 95, 85, 75, 65, 55 , 45, 35, 25 , 15][::-1]
# m_ampls = [200]
# m_ampls = [100, 90, 80,  70, 60, 50, 40, 30, 20, 10][::-1]
m_ampls = [200, 175, 150, 130, 120,110,100, 90, 80,  70, 60, 50, 40, 30, 20, 10][::-1]
Extra_amp = 0 
# scanrates = [100, 90, 80, 70, 60, 50, 40, 30, 25, 20 , 15, 10][::-1]
# scanrates = [150,  130, 110, 100, 90, 80, 70, 60, 50, 40, 30, 20 ]
# scanrates = [150,  130, 110, 100, 90, 80, 70, 60, 50, 40 ]
scanrates = [ 125, 100,75, 50]
scanrates = [500]
Tcs = ['1 s', '300 ms', '100 ms', '30 ms']
sens = ['10 mV/nA', '5 mV/nA',    '10 mV/nA',    '50 mV/nA',    '200 mV/nA']
Ampl_lockins = np.array([]); phases = np.array([])
Ampl_lockin_as =np.array([]); pds = np.array([])
currents = np.array([])
# aa = [-75, -110, -145, -180, -215, -250]
ofs = np.append( np.arange(-300,400, 35), np.arange(-300,400, 35))

# ofs = np.append( aa, np.arange(-300,400, 35))
ofs =  np.array(np.arange(250,-350, -35))
ofs =[ 0 ]
if len(ofs)>10 or len(m_ampls)> 6 or len(m_freqs)>6:
    longscan = False
else:
    longscan = True

longscan = False
if longscan ==True:
    ofs =[-300]
    m_freqs = [ 500]
i=0

for of in tqdm.tqdm(ofs, desc = "Offset"):
    for m_freq in tqdm.tqdm(m_freqs, desc = "Frequency"):
        for scanrate in tqdm.tqdm(scanrates, desc = "ScanRates"):
            for m_ampl in tqdm.tqdm(m_ampls, desc = "Amplitudes",bar_format='{desc:<15}{percentage:3.0f}%|{bar:30}{r_bar}', colour  = 'green', nrows  = 40):
            
                # lockinA.time_constant(Tc = Tcs[i])
                # lockinA.sensitivity(sen = sens[0])
                # time.sleep(2)
                # i +=1
                if longscan == True:
                    lockinA.time_constant(Tc = "1 s")
                    rt = 20
                elif m_freq > 550:
                    lockinA.time_constant(Tc = "30 ms")
                    rt = 20*2
                    if of < 100:
                        rt = 20
                elif m_freq> 300:
                    lockinA.time_constant(Tc = "100 ms")
                    rt = 30*2
                elif m_freq > 93: #100
                    lockinA.time_constant(Tc = "300 ms") #100ms
                    rt = 50*2 #80
                elif m_freq > 50:
                    lockinA.time_constant(Tc = "1 s")
                    rt = 80*2  
                elif m_freq > 10:
                    lockinA.time_constant(Tc = "3 s")
                    rt = 150
                elif m_freq > 0.9:
                    lockinA.time_constant(Tc = "10 s")
                    rt = 500

                time_start=time.process_time()
                """CV : choose 0 or 1, 0 just do sine oscillation, 1 do AC voltammetry`
                   reverse: 1 or -1, 1 not reverse when use dualPicostat, 1 reverse for Picostat with range of larger current input 
                   have tested the pico, the voltage output to cell is correct, the output to daq is reserved """
                ## STEP 3.0: Sine Modulation  
                taskMod = daq.StepSinGenerator(step =2*1e-3,m_freq=m_freq,m_ampl=m_ampl+ Extra_amp,v_min= v_min,v_max=v_max,v_scanRate=scanrate, CV=0,offset=of,reverse=1)
                taskM = daq.MeasureTask(m_freq, rt)
                taskMod.StartTask()
                taskM.StartTask()
                PB.ShowBar(Barname = "ScanProgress", runtime = rt)
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
                    PB.ShowBar(Barname = "CVScan", runtime = (v_max-v_min)/scanrate*2*4+1) 
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
                time_stop=time.process_time()
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
                param['Lock-in']['input_config']=lockinA.query_input_config()  ## this is an example of reading from a dictionary, fill in the rest as necessary
                param['Lock-in']['input_coupling']=lockinA.query_input_coupling()
                param['Lock-in']['input_shield']=lockinA.query_input_shield()
                param['Lock-in']['input_filter']=lockinA.query_input_filter()
                
                param['Lock-in']['time_constant']=lockinA.query_time_constant()
                param['Lock-in']['sensitivity']=lockinA.query_sensitivity()
                param['Lock-in']['filter_slope']=lockinA.query_filter_slope()
                param['Lock-in']['reserve_mode']=lockinA.query_reserve_mode()
                param['Lock-in']['sync_filter']=lockinA.query_sync_filter()
                
                param['Lock-in']['frequency']=lockinA.query_frequency()
                param['Lock-in']['reference_source']=lockinA.query_reference_source()
                param['Lock-in']['reference_trigger']=lockinA.query_reference_trigger()
                param['Lock-in']['harm']=lockinA.query_harm()
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
                Ampl_lockin_x = np.mean(mdata[int(samplerate*ave_t):,2])
                Ampl_lockin_y = np.mean(mdata[int(samplerate*ave_t):,4])
                Ampl_lockin_a = np.sqrt(Ampl_lockin_x*Ampl_lockin_x+Ampl_lockin_y*Ampl_lockin_y)
                Ampl_lockin_as = np.append(Ampl_lockin_as, Ampl_lockin_a)
                Ampl_lockin = np.mean(Ampl_lockin_a)/np.mean(mdata[int(samplerate*ave_t):,3])
                Ampl_lockins = np.append(Ampl_lockins, Ampl_lockin)
                phase = np.arctan2(Ampl_lockin_y,Ampl_lockin_x)*180/np.pi
                phases = np.append(phases, phase)
                print('Continously record data for %.3f seconds. \nThe shape of the data is %s.' %(runtime, np.shape(mdata)))
                print('%s' %(savename+"_m"+str(movieN)))
                print("Frequency is %d Hz, amplitude is %d mV, scanrate is %d mV/s, offset is %d mV. Done" %(m_freq,m_ampl,scanrate,of))
                # savefileandpath = (saveloc+"\\"+savename+"_m"+str(movieN))
                # # Get and save measured data:
                # ## STEP 6.1: plot the output to check if measurement was successful
            
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
                fig, ax = plt.subplots(figsize=(10,4))
                #%matplotlib qt
                ax.plot(lockin[::10], 'r',label= 'lockinR')
                ax.plot(lockiny[::10],'k-.',lw=0.5)
                ax.plot(lockinx[::10],'y-.',lw=1)
                ax2= ax.twinx()
                #ax2.plot(lockinR, 'b', label ='lockin')
                ax2.plot(V[::10]-4)
                ax2.plot(C[::10]-3)
                ax2.set_ylim(None,1)
                ax.set_ylabel("Lockin Amp.", color= 'r', fontsize = 15)
                ax2.set_ylabel("Currents_volatge", color= 'b', fontsize = 15)
                ax.legend(["Freq= %d Hz\n Amp. =  %d mV\n scanrate = %d mV/s\nave=%.3f" 
                           %(m_freq,m_ampl,scanrate, Ampl_lockin)], loc = 'upper right', fontsize =15).set_zorder(5)
                plt.show()
                if figuresave == True:
                    figs_name = saveloc+"\\"+savename+"_m"+str(movieN) 
                    fig.savefig(fname = figs_name+ "CV.png", dpi=600, format='png') 
                fig, ax = plt.subplots(figsize=(10,4))
                #%matplotlib qt
                ax.plot(lockin[::10], 'r',label= 'lockinR')
                
                ax2= ax.twinx()
                #ax2.plot(lockinR, 'b', label ='lockin')
                ax2.plot(abs(phase[::10]))
                # ax2.plot(phase2[::10]*180/10)
                ax2.set_ylim(0,None)
                ax.set_ylabel("Lockin Amp.", color= 'r', fontsize = 15)
                ax2.set_ylabel("Phase", color= 'b', fontsize = 15)
                ax.legend(["Freq= %d Hz\n Amp. =  %d mV\n scanrate = %d mV/s" 
                           %(m_freq,m_ampl,scanrate)], loc = 'best', fontsize =15).set_zorder(5)
                plt.show()
                if figuresave == True:
                    figs_name = saveloc+"\\"+savename+"_m"+str(movieN) 
                    fig.savefig(fname = figs_name+ "lockins.png", dpi=600, format='png') 
                
                fig, ax = plt.subplots(figsize=(10,4))
                #%matplotlib qt
                ax.plot(pd[::10], 'r',label= 'PD intensity')
                ax2= ax.twinx()
                #ax2.plot(lockinR, 'b', label ='lockin')
                ax2.plot(lockin[::10]-2, 'r',label= 'lockinR')
                ax2.plot(V[::10]-2)
                ax2.set_ylim(None,4)
                ax.legend(["Freq= %d Hz\n Amp. =  %d mV\n scanrate = %d mV/s\nave=%.3f\noffset =%d mV" 
                           %(m_freq,m_ampl,scanrate, Ampl_lockin, of)], loc = 'upper right', fontsize =15).set_zorder(5)
                plt.show()
                # time.sleep(1)
                # del lockinx; lockiny; lockin; C; V; pd; mdata; figuresave
               

taskZ = daq.ZeroOutput()
taskZ.StartTask()
taskZ.StopTask()
taskZ.ClearTask()

if len(m_freqs) > 5:
    x_plot = np.array(m_freqs); x_label = 'Frequency [Hz]'
    figs_name = saveloc+"\\"+savename+"_m"+str(movieN) + "_Freq_Scan_"
elif len(ofs)>10:
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
ax.plot( pds, 'k')
ax2= ax.twinx()
ax2.plot( currents, 'b')   
ax.set_ylabel("PD Intensity", color= 'k', fontsize = 30)
ax.set_xlabel('counts','', color= 'k', fontsize = 30)
ax2.set_ylabel("Currents", color= 'b', fontsize = 30)
fig.savefig(fname = figs_name+ "pds.png", dpi=600, format='png') 
print("Frequency run is done")    

fig, ax = plt.subplots(figsize=(10,5))
ax.plot(x_plot, Ampl_lockins, 'r')
ax.plot(x_plot, Ampl_lockin_as/np.mean(pds), 'g')
# ax.plot(pds/3, 'k')
ax2= ax.twinx()
ax2.plot(x_plot, abs(phases), 'b')
ax.set_ylabel("Lockin Amp.", color= 'r', fontsize = 30)
ax.set_xlabel(x_label, color= 'k', fontsize = 30)
ax2.set_ylabel("Phase", color= 'b', fontsize = 30)
fig.savefig(fname = figs_name+ "lockins.png", dpi=600, format='png') 

fig, ax = plt.subplots(figsize=(10,5))
ax.plot( Ampl_lockins, 'r')
ax.plot(Ampl_lockin_as/np.mean(pds), 'g')
ax2= ax.twinx()
ax2.plot( abs(phases), 'b')
fig.savefig(fname = figs_name+ "lockins-2.png", dpi=600, format='png') 

lockinA.control(control= 'local')
lockinA.query_control()
lockinA.close()



#%%
