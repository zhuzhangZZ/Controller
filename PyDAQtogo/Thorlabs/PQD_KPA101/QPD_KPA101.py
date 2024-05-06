
"""
KPA101
An example that uses the .NET Kinesis Libraries to connect to a KPA101.
Adapter from Thorlabs github, https://github.com/Thorlabs/Motion_Control_Examples/tree/main/Python/KCube/KPA101
with more option, like set the PID parameters, get the mode inofomration .......
@author: Zhu Zhang <zhuzhang101@gamil.com>
"""

import time
import clr ## do not pip install clr  !!!!!!
"""There is a package named clr while the pythonnet package's alias is also clr. 
So I removed clr by "pip uninstall clr" and then installed pythonnet by 'pip install pythonnet'. 
Finally, everything works well.
https://stackoverflow.com/questions/47913079/python-attributeerror-module-object-has-no-attribute-addreference"""

clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll.")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.KCube.PositionAlignerCLI.dll.")

from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.KCube.PositionAlignerCLI import *
from System import Decimal


#%%

class PQD_KPA101:
    def __init__(self, serial_no = "69251034"):
        """Initialized the calss
        serial_no: the serial number of the KPA101 which wants to connect
        if the setial_no is none, 
        will then connect to the first dtected device through the detected serial number
        """
        # Build device list so that the library can find yours
        import Thorlabs.MotionControl.DeviceManagerCLI as Device
        import Thorlabs.MotionControl.KCube.PositionAlignerCLI as PosAligner
        device_list = Device.DeviceManagerCLI.BuildDeviceList()
        # print(device_list)
        serialnumbers = [str(ser) for ser in
                         Device.DeviceManagerCLI.GetDeviceList(PosAligner.KCubePositionAligner.DevicePrefix)]
        print(f"Detected serialnumbers of the KPA is: {serialnumbers}" )
        # create new device
        if serial_no == None:
            serial_no = serialnumbers[0]
        self.serial_no = str(serial_no)  # Replace this line with your device's serial number
        self.kcube = KCubePositionAligner.CreateKCubePositionAligner(self.serial_no)
        
    def connect(self):
        """connect to the device through the provided serialnumber or detected serialnumber"""
        self.kcube.Connect(self.serial_no)
        time.sleep(0.25)
        self.kcube.StartPolling(250)
        time.sleep(0.25)  # wait statements are important to allow settings to be sent to the device
        
    def enable_it(self):
        """enable the device"""
        self.kcube.EnableDevice()
        time.sleep(0.25)  # Wait for device to enable
         
    def get_device_info(self):
        """Get the device infomration. Name"""
        self.device_info = self.kcube.GetDeviceInfo()
        print(self.device_info.Description)
    
    def settings_init(self):
        """# Wait for Settings to Initialise"""
        if not self.kcube.IsSettingsInitialized():
            self.kcube.WaitForSettingsInitialized(10000)  # 10 second timeout
            assert self.kcube.IsSettingsInitialized() is True
    
    def get_config(self):
        """get Device Configuration"""
        PositionAlignerTrakConfiguration = self.kcube.GetPositionAlignerConfiguration(self.serial_no,\
                           PositionAlignerConfiguration.DeviceSettingsUseOptionType.UseDeviceSettings)
        #Not used directly in example but illustrates how to obtain device settings
        currentDeviceSettings = self.kcube.PositionAlignerDeviceSettings
        time.sleep(1)
    
    def detector_select(self):
        """ Select the detector 
        PDQ80A = 0x01, PDQ30C = 0x02, PDP90A = 0x03, Other = 0xFF"""
       
        GUISettings.Detectors = 0x01
    def get_detector(self):
        #get the type of the detector
        detector = GUISettings.Detectors
        
    def mode_seting(self, mode = 'open'):
        """Set the mode of the PositionAlinger:
            mode:
                open open loop
                clode: close loop
                mointor: monitor mode
                auto: AutoOpenClose loop mode, based on the sum of the light intensity
        """
        if mode == "open":
            self.kcube.SetOperatingMode(PositionAlignerStatus.OperatingModes.OpenLoop, False)
        elif mode == 'close':
            self.kcube.SetOperatingMode(PositionAlignerStatus.OperatingModes.ClosedLoop, False)
        elif mode == "auto":
            self.kcube.SetOperatingMode(PositionAlignerStatus.OperatingModes.AutoOpenClosedLoop, False) ## need to check
        elif mode == "monitor":
            self.kcube.SetOperatingMode(PositionAlignerStatus.OperatingModes.Monitor, False)
        else:
            print("Set the Operating Mode: monitor; open; close; suto ")
    
    def get_mode_setting(self):
        """Get the operating mode state from the device"""
        mode = self.kcube.Status.Mode.value__
        if mode == 0:
            Mode = "ModeUndefined"
        elif mode == 1:
            Mode = "Monitor"
        elif mode ==2:
            Mode = "OpenLoop"
        elif mode == 3:
            Mode = "ClosedLoop"
        elif mode == 4:
            Mode = "AutoOpenClosedLoop"
        return Mode
    
    def set_PID(self, P = 1, I = 1, D = 1 ):
        """Set the PID value.
        P: ProportionalGain of the PID loop
        I: IntegralGain of the PID loop
        D: DerivativeGain of the PID loop
        """
        pid_settings = PositionAlignerPIDParameters()
        P_0, I_0, D_0 =  self.get_PID_value()
        if P is not None:
            pid_settings.ProportionalGain = P
        else:
            pid_settings.ProportionalGain = P_0
        if I is not None:
            pid_settings.IntegralGain = I
        else:
            pid_settings.IntegralGain = I_0
        if D is not None:
            pid_settings.DerivativeGain = D
        else:
            pid_settings.DerivativeGain = D_0
        self.kcube.SetPIDparams(pid_settings)
        print(self.get_PID_value())
        
    def get_PID_value(self):
        """get the PID value.
        return:
            P: ProportionalGain of the PID loop
            I: IntegralGain of the PID loop
            D: DerivativeGain of th ePID loop
        """
        PID = self.kcube.GetPIDparams()
        return PID.ProportionalGain, PID.IntegralGain, PID.DerivativeGain
    def set_Notch_Filter(self, CF = 60, Q = 0.2, NF_state = True):
        """Set the Notch filter parameters.
        
            CF: NotchFilterCenterFrequency of the notch filter 
            Q: Quality factor  of the the notch filter , Q = bandwidth/centerFreq
            NF_state: state of the notch filter, enable or not
        """
        NF_settings = PositionAlignerNotchFilterParameters()
        CF_0, Q_0, NF_state_0 = self.get_Notch_Filter()
        if CF is not None:
            NF_settings.NotchFilterCenterFrequency = CF
        else:
            NF_settings.NotchFilterCenterFrequency = CF_0
        if Q is not None:
            NF_settings.NotchFilterQ = Q
        else:
            NF_settings.NotchFilterQ = Q_0
        if NF_state is not None:
            NF_settings.NotchFilterEnabled = NF_state
        else:
            NF_settings.NotchFilterEnabled = NF_state_0
        self.kcube.SetNotchFilterparams(NF_settings)
        print(self.get_Notch_Filter())
        
    def get_Notch_Filter(self):
        """get the Notch filter parameters.
        return:
            NotchFilterCenterFrequency: NotchFilterCenterFrequency of the notch filter 
            NotchFilterQ: Quality factor  of the the notch filter , Q = bandwidth/centerFreq
            NotchFilterEnabled: state of the notch filter, enable or not
        """
        Notch = self.kcube.GetNotchFilterparams()
        return Notch.NotchFilterCenterFrequency, Notch.NotchFilterQ, Notch.NotchFilterEnabled
    def set_LowPass_Filter(self, Cutoff = 90, LowPass_state = True):
        """Set the Notch filter parameters.
        
            Cutfff: Cutoff Frequency of the low pass filter 
            LowPass_state: state of the notch filter, enable or not
        """
        LowPass_settings = PositionAlignerLowPassFilterParameters()
        Cutoff_0,  LowPass_state_0 = self.get_LowPass_Filter()
        if Cutoff is not None:
            LowPass_settings.LowPassFilterCutOffFreq = Cutoff
        else:
            LowPass_settings.LowPassFilterCutOffFreq = Cutoff_0
        if LowPass_state is not None:
            LowPass_settings.LowPassFilterEnabled = LowPass_state
        else:
            LowPass_settings.LowPassFilterEnabled = LowPass_state_0
        self.kcube.SetLowPassFilterparams(LowPass_settings)
        print(self.get_LowPass_Filter())
    
    def get_LowPass_Filter(self):
        """get the Low Pass filter parameters.
        return:
            LowPassFilterCutOffFreq: cut off Frequency of the low Pass filter 
            LowPassFilterEnabled: state of the low Pass filter , enable or not
        """
        LowPass = self.kcube.GetLowPassFilterparams()
        return LowPass.LowPassFilterCutOffFreq,  LowPass.LowPassFilterEnabled
    
    def set_XY_Feedback_Gain(self, X_gain = 0.11, XGainSense = "Forward",   Y_gain = 0, YGainSense = "Forward"):
        """Set the XY_Feedback_Gain.
            X_gain: feed back gain in X direction
            XGainSense: Forward or backward in X direction, backward (reserved) negative
            Y_gain: feed back gain in Y direction
            YGainSense: Forward or backward in Y direction, backward (reserved) negative
        """
        XY_FBGain_settings = PositionAlignerPosDemandParameters()
        X_gain_0, XGainSense_0, Y_gain_0,  YGainSense_0 = self.get_XY_Feedback_Gain()
        if X_gain is not None:
            XY_FBGain_settings.XFeedbackGain = X_gain
        else:
            XY_FBGain_settings.XFeedbackGain = X_gain_0
        
        if XGainSense == "Forward" or XGainSense == "forward" :
            XY_FBGain_settings.XGainSense = XY_FBGain_settings.DirectionSense.Forward 
            
        elif XGainSense == "Backward" or XGainSense == "backward" or  XGainSense == "reverse" :
            XY_FBGain_settings.XGainSense  = XY_FBGain_settings.DirectionSense.Backward
        
        if Y_gain is not None:
            XY_FBGain_settings.YFeedbackGain = Y_gain
        else:
            XY_FBGain_settings.YFeedbackGain = Y_gain_0
            
        if YGainSense == "Forward" or YGainSense == "forward" :
            XY_FBGain_settings.YGainSense  = XY_FBGain_settings.DirectionSense.Forward 
            
        elif YGainSense == "Backward" or YGainSense == "backward" or  YGainSense == "reverse" :
            XY_FBGain_settings.YGainSense = XY_FBGain_settings.DirectionSense.Backward
        self.kcube.SetPosDemandParams(XY_FBGain_settings)
        print(self.get_XY_Feedback_Gain())
    
    def get_XY_Feedback_Gain(self):
        """get the X Y feedback gain parameters.
        return:
            XFeedbackGain: feed back gain in X direction
            Feedback_gain: feed back gain in Y direction
            XGainSense: Forward or backward in X direction, backward (reserved) negative
            YGainSense: Forward or backward in Y direction, backward (reserved) negative
        """
        Feedback_gain = self.kcube.GetPosDemandParams()
        X_gain_sense = Feedback_gain.XGainSense.value__
        
        if X_gain_sense == 1:
            XGainSense = "Forward"
        elif X_gain_sense == 2:
            XGainSense = "Backward"
        else:
            print(Feedback_gain.XGainSense.value__)
        Y_gain_sense = Feedback_gain.YGainSense.value__
        
        if Y_gain_sense == 1:
            YGainSense = "Forward"
        elif Y_gain_sense == 2:
            YGainSense = "Backward"
        else:
            print(Feedback_gain.YGainSense.value__)
        return Feedback_gain.XFeedbackGain,  XGainSense,  Feedback_gain.YFeedbackGain, YGainSense
    def get_XYDiff(self):
        """get the X Y position difference in Voltage of the beam on PQD
        return:
            XDiff: position difference in X position (V)
            YDiff: position difference in Y position (V)
        """
        positionDiff = self.kcube.Status.PositionDifference
        XDiff = positionDiff.X
        YDiff = positionDiff.Y
        return XDiff, YDiff
    def get_sum(self):
        """get the total intensity in Voltage of the beam on PQD
        return:
            positionSum: beam total intensity on PQD (V)
        """
        positionSum = self.kcube.Status.Sum
        return positionSum
    
    def close(self):
        """Stop pulling and disconnect the device
        """
        self.kcube.StopPolling()
        self.kcube.Disconnect(True)
        
#%%       
    def main_test():
        """The main entry point for the application"""
        # Uncomment this line if you are using Simulations
        # SimulationManager.Instance.InitializeSimulations()
        try:
    
            # Build device list so that the library can find yours
            device_list = DeviceManagerCLI.BuildDeviceList()
            # create new device
            serial_no = str(serial_no)  # Replace this line with your device's serial number
            kcube = KCubePositionAligner.CreateKCubePositionAligner(serial_no)
    
            # Connect, begin polling, and enable
            kcube.Connect(serial_no)
            time.sleep(0.25)
            kcube.StartPolling(250)
            time.sleep(0.25)  # wait statements are important to allow settings to be sent to the device
    
            kcube.EnableDevice()
            time.sleep(0.25)  # Wait for device to enable
    
            # Get Device information
            device_info = kcube.GetDeviceInfo()
            print(device_info.Description)
    
            # Wait for Settings to Initialise
            if not kcube.IsSettingsInitialized():
                kcube.WaitForSettingsInitialized(10000)  # 10 second timeout
                assert kcube.IsSettingsInitialized() is True
    
            #get Device Configuration
            PositionAlignerTrakConfiguration = kcube.GetPositionAlignerConfiguration(serial_no, PositionAlignerConfiguration.DeviceSettingsUseOptionType.UseDeviceSettings)
            #Not used directly in example but illustrates how to obtain device settings
            currentDeviceSettings = kcube.PositionAlignerDeviceSettings
    
            time.sleep(1)
            
            #Select the detector 
            #PDQ80A = 0x01, PDQ30C = 0x02, PDP90A = 0x03, Other = 0xFF
            GUISettings.Detectors = 0x01 
            
            # flag = True
            # while flag:
            #     a = input("Select the Detector Type: 1.PDQ80A; 2.PDQ300C; 3.PDP90A; 4.Other ")
            #     if a == "1":
            #         GUISettings.Detectors = 0x01
            #         flag = False
            #     elif a == "2":
            #         GUISettings.Detectors = 0x02
            #         flag = False
            #     elif a == "3":
            #         GUISettings.Detectors = 0x03
            #         flag = False
            #     elif a == "4":
            #         GUISettings.Detectors = 0xFF
            #         flag = False
            #     else:
            #         print("Invaild input")
            
            #Set the operating mode
            
            kcube.SetOperatingMode(PositionAlignerStatus.OperatingModes.OpenLoop, False)
            # flag = True
            # while flag:
            #     a = input("Set the Operating Mode: 1.Monitor; 2.Open Loop; 3.Close Loop;4. AUTOOPENCLOSEDLOOP ")
            #     if a == "1":
            #         kcube.SetOperatingMode(PositionAlignerStatus.OperatingModes.Monitor, False)
            #         flag = False
            #     elif a == "2":
            #         kcube.SetOperatingMode(PositionAlignerStatus.OperatingModes.OpenLoop, False)
            #         flag = False
            #     elif a == "3":
            #         kcube.SetOperatingMode(PositionAlignerStatus.OperatingModes.CloseLoop, False)
            #         flag = False
            #     elif a == "4":
            #         kcube.SetOperatingMode(PositionAlignerStatus.OperatingModes.AUTOOPENCLOSEDLOOP, False) ## need to check
            #         flag = False
            #     else:
            #         print("Invaild input")
            
            time.sleep(1)
            
            #get the type of the detector
            detector = GUISettings.Detectors
            
            #Display the Voltage or Position
            positionDiff = kcube.Status.PositionDifference
            positionSum = kcube.Status.Sum
            if detector == 3: # only PDP series can display the position difference in "mm"
                print("X position: ",positionDiff.X * 5 /positionSum," mm") #5 is half the length of the sensor
                print("Y position: ",positionDiff.Y * 5 /positionSum," mm")
            else:
                print("X Diff: ",positionDiff.X," V") #For PDQ series, the voltage difference CANNOT be converted to real position.
                print("Y Diff: ",positionDiff.Y," V")
            print("Sum: ",positionSum," V")
    
            # Stop polling and close device
            kcube.StopPolling()
            kcube.Disconnect(True)
        except Exception as e:
            print(e)
            

#%%
if __name__ == "__main__":
    from tqdm import tqdm
    PQD = PQD_KPA101(serial_no = "69251034")
    PQD.connect()
    PQD.enable_it()
    PQD.get_device_info()
    PQD.settings_init()
    PQD.get_config()
    PQD.detector_select()
    PQD.get_detector()
    PQD.mode_seting(mode = 'open')
    Diffx_ = []; Diffy_ = []; SUM_=[]
    DiffX_N = []; DiffY_N = []
    sleep_time =0.25
    mode = PQD.get_mode_setting()
    PQD.set_PID(P= 0.11, I =0.01, D = 0)
    PID = PQD.get_PID_value()
    print(PID)
    print(PQD.get_Notch_Filter())
    PQD.set_Notch_Filter(CF = 60, Q = 0.2, NF_state = True)
    print(PQD.get_Notch_Filter())
    print(PQD.get_LowPass_Filter())
    PQD.set_LowPass_Filter( Cutoff = 90, LowPass_state = True)
    print(PQD.get_XY_Feedback_Gain())
    PQD.set_XY_Feedback_Gain(X_gain = 0.12, XGainSense = "Forward",   Y_gain = 0, YGainSense = "Backward")
    
    # PQD.mode_seting(mode = 'close')
    sleep_time = 0.1
    minute = 0.5
    for i in tqdm(range(int(60*minute/sleep_time))):
        # PQD.mode_seting(mode = 'close')
        DiffX, DiffY = PQD.get_XYDiff()
        SUM = PQD.get_sum()
        print("X Diff: ",DiffX," V") #For PDQ series, the voltage difference CANNOT be converted to real position.
        print("Y Diff: ",DiffY," V")
        print("Sum: ",SUM," V")
        print("X Diff/SUM: ",DiffX/SUM," V") #For PDQ series, the voltage difference CANNOT be converted to real position.
        print("Y Diff/SUM: ",DiffY/SUM," V\n")
        Diffx_.append(DiffX)
        Diffy_.append(DiffY)
        SUM_.append(SUM)
        
        DiffX_N.append(DiffX/SUM)
        DiffY_N.append(DiffY/SUM)
        time.sleep(sleep_time)
    
    PQD.close()
    
    
    #%%
    import matplotlib.pyplot as plt
    import numpy as np
    fig, ax = plt.subplots() 
    ax_twin = ax.twinx() 
    ax.plot(Diffx_, 'r' , label =f'X Std: {np.var(Diffx_):.3e}', zorder =2) 
    ax_twin.plot(Diffy_, 'b' , label  =f'Y Std: {np.var(Diffy_):.3e}', alpha =0.3, zorder = 1)
    ax.legend(loc= "upper left")
    ax_twin.legend(loc= "upper right")
    DiffX_N = np.array(DiffX_N)
    DiffY_N = np.array(DiffY_N)
    ax.set_ylim(-0.05,0.05)           
       
    fig, ax = plt.subplots() 
    ax_twin = ax.twinx() 
    ax.plot(np.array(DiffX_N)*np.mean(SUM_), 'r', 
            label = f'X/sum Std: {np.var(DiffX_N*np.mean(SUM_)):.3e}', zorder =2) 
    ax.legend(loc= "upper left")
    ax_twin.plot(np.array(DiffY_N)*np.mean(SUM_), 'b', 
                 label = f'Y/sum Std: {np.var(DiffY_N*np.mean(SUM_)):.3e}')
    
    ax_twin.legend(loc= "upper right")
    ax.set_ylim(-0.05,0.05)    
    
    
    fig, ax = plt.subplots() 
    ax_twin = ax.twinx() 
    ax.plot(np.array(DiffX_N)*np.mean(SUM_) - Diffx_, 'r', 
            label = f'Diffx_N - Diffx_', zorder =2) 
    ax.legend(loc= "upper left")
    # ax_twin.plot( np.array(DiffY_N)*np.mean(SUM_) - Diffy_, 'b',
                 # label = 'DiffY_N - Diffy_')
    
    ax_twin.legend(loc= "upper right")
    ax.set_ylim(-0.0001,0.0001)    
    
    
    fig, ax = plt.subplots() 
    ax_twin = ax.twinx() 
    ax.plot(SUM_/np.mean(SUM_) -1,  label=f'Std: {np.std(SUM_):.6f}') 
    ax.legend(loc= "upper left")
    ax_twin.plot(SUM_, 'b',label=f'SUM')
    ax_twin.legend(loc= "upper right")
    