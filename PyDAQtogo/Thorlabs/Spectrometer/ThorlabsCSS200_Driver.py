

# -*- coding: utf-8 -*-
"""
Example of C Libraries for CCS Spectrometers in Python with CTypes
Author: Zhu Zhang <z.zhang@uu.nl>
Copy from 
https://github.com/Thorlabs/Light_Analysis_Examples/blob/main/Python/Thorlabs%20CCS%20Spectrometers/CCS%20using%20ctypes%20-%20Python%203.py


"""
import  os
import time
import numpy as np
import  matplotlib . pyplot  as  plt
from ctypes import *
import glob, os
import tqdm
import ProgressBar as PB

class CCS200:
    
    def __init__(self, DeviceSerialNumber = None):
        
        if DeviceSerialNumber == None:
            self.DeviceSerialNumber = "M00440703" 
        else:
            self.DeviceSerialNumber = DeviceSerialNumber
        os.chdir(r"C:\Program Files\IVI Foundation\VISA\Win64\Bin")
        self.lib  =  cdll.LoadLibrary ( "TLCCS_64.dll" )
        self.ccs_handle=c_int(0)
    
        #documentation: C:\Program Files\IVI Foundation\VISA\Win64\TLCCS\Manual
        #Start Scan- Resource name will need to be adjusted
        #windows device manager -> NI-VISA USB Device -> Spectrometer -> Properties -> Details -> Device Instance Path -> M00xxxxxxxx
        #USB0::0x1313::0x8089::DEVICE-SERIAL-NUMBER::RAW   ,, DEVICE-SERIAL-NUMBER = M00440703
        self.DeviceName = 'USB0::0x1313::0x8089::' + self.DeviceSerialNumber +  '::RAW'
        self.lib.tlccs_init(bytes(self.DeviceName, 'utf-8'), 1, 1, byref(self.ccs_handle))
        self.manufacturerName = (c_char*256)()
        self.deviceName = (c_char*256)()
        self.serialNumber = (c_char*256)()     
        self.firmwareRevision =(c_char*256)()
        self.instrumentDriverRevision = (c_char*256)()
        self.lib.tlccs_identificationQuery(self.ccs_handle,byref(self.manufacturerName),
                                           byref(self.deviceName), 
                                           byref(self.serialNumber),
                                           byref(self.firmwareRevision), 
                                           byref(self.instrumentDriverRevision))
        
        print("The %s, %s %s is open." %(self.manufacturerName.value.decode("utf-8"), 
                                      self.deviceName.value.decode("utf-8"),
                                      self.serialNumber.value.decode("utf-8")))
    def close(self):
        return self.lib.tlccs_close (self.ccs_handle)
    
    def set_InteTime(self, integration_time = 100E-3):
        self.integration_time=c_double(integration_time)
        return self.lib.tlccs_setIntegrationTime(self.ccs_handle, self.integration_time)
    
    def start(self):
        return self.lib.tlccs_startScan(self.ccs_handle)
        
    def getWavelength(self):
        self.wavelengths=(c_double*3648)()
        self.lib.tlccs_getWavelengthData(self.ccs_handle, 0, byref(self.wavelengths), 
                                         c_void_p(None), c_void_p(None))
        return np.ctypeslib.as_array(self.wavelengths)
    
    def getData(self):
        self.data_array=(c_double*3648)()
        self.lib.tlccs_getScanData(self.ccs_handle, byref(self.data_array))
        return np.ctypeslib.as_array(self.data_array)
    
    def get_InteTime(self):
        self.Integr_time_check = c_double()
        self.lib.tlccs_getIntegrationTime(self.ccs_handle, byref(self.Integr_time_check))
        return  self.Integr_time_check.value
   
    
def runSpectrum(save = True, method = "Time", runTime = 30, cycles=10, integTime = 100E-3, savename = 'darkcounts', saveloc = None  ):
    spectrum = CCS200(DeviceSerialNumber = None)
    savename = savename
    saveloc = saveloc
    integration_time = integTime
    spectrum.set_InteTime(integration_time = integration_time)
    spectrumArray =  np.empty((0, 3648), float)
    scantime = runTime
    cycleN = 0
    Ttime = time.time()
    if method == "Time":        
        while (time.time()-Ttime)< scantime:
            spectrum.start()
            data_array = spectrum.getData()
            spectrum.get_InteTime()
            spectrumArray = np.append(spectrumArray, np.array([data_array]), axis=0)
            # print("Time is %.2f s, data shape is %s"%((time.time()-Ttime), spectrumArray.shape))
            PB.update_progress((time.time()-Ttime)/scantime, Barname = "Progress", runtime=scantime)
        paras = "_InteTime_"+ str(integration_time*1000)+"ms_runnigTime_" +str(scantime)+"s"
    elif method == 'Cycles':
        for  cycleN in tqdm.tqdm(np.arange(cycles), desc = "CycNumber"):
            spectrum.start()
            data_array = spectrum.getData()
            spectrum.get_InteTime()
            spectrumArray = np.append(spectrumArray, np.array([data_array]), axis=0)
            # if cycleN%10 == 0:
            #     print("CycleNumber is %d, data shape is %s"%(cycleN, spectrumArray.shape))
            
        paras = "_InteTime_"+ str(integration_time*1000)+"ms_CyclesNumber_" +str(cycles)
    else:
        print("method is wrong, choose method from Time|cycles")
    wavelengths = spectrum.getWavelength()
    filelist = sorted(glob.glob(saveloc+"\\"+savename + paras + '_*.npy'),key=os.path.getmtime)
    # print(filelist)
    count = len(filelist)
    
    if count == 0:
        Number = 0
    else:
        for i in range(0,7):
            char = filelist[-1][-i-4]
            if char == 'm':
                break
        numberE = filelist[-1][-i-3:-4]
        print(numberE)    
        Number = int(numberE) + 1
    savefileandpath = saveloc+"\\"+savename + paras+"_m"+str(Number)
    if save == True:
        np.save(savefileandpath, spectrumArray)
    else:
        pass
    print(spectrum.close())
    
    return wavelengths, spectrumArray

if __name__ == "__main__":
    wavelengths, spectrumArray =\
    runSpectrum(method = "Time", runTime = 10, cycles=500, integTime = 2E-3, savename = 'darkcounts', saveloc = 'C:\\Data\\Zhu\\Spectrometer\\2022-11-08_spectrum_test'  )
    
    fig, ax = plt.subplots(figsize =(15,6))
    ax.fill_between(wavelengths, np.min(spectrumArray, axis=0), np.max(spectrumArray, axis=0), alpha =0.5)
    
    ax.plot(wavelengths, np.mean(spectrumArray, axis = 0), color = 'r', lw =1)
    ax.set_xlabel("Wavelength [nm]", fontsize =30)
    ax.set_ylabel("Intensity [a.u.]", fontsize =30)
    ax.set_xticks(np.arange(200,1100, 20))
    ax.grid(True)
    ax.set_xlim(400, 950)
    plt.show()
#%%
if __name__  == '__main__':
    
        
    saveloc = 'C:\\Data\\Zhu\\Spectrometer\\2022-11-08_spectrum_test'
    method = "Time"
    runTime = 5
    integTime = 2E-3
    savename = 'darkcounts'
    paras = "_InteTime_"+ str(integTime*1000)+"ms_runnigTime_" +str(runTime)+"s"
    filelist = sorted(glob.glob(saveloc+"\\"+savename + paras + '_*.npy'),key=os.path.getmtime)
    print(filelist)
    count = len(filelist)
    
    if count == 0:
        Number = 0
    else:
        for i in range(0,7):
            char = filelist[-1][-i-4]
            if char == 'm':
                break
        numberE = filelist[-1][-i-3:-4]
        print(numberE)    
        Number = int(numberE) + 1
        
#%%




#%%


#%%
