# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 18:08:28 2026

@author: Zhang101
"""


"""
KPA101
An example that uses the .NET Kinesis Libraries to connect to a KPA101.
Adapter from Thorlabs github, https://github.com/Thorlabs/Motion_Control_Examples/tree/main/Python/KCube/KPA101
with more option, like set the PID parameters, get the mode inofomration .......
@author: Zhu Zhang <zhuzhang101@gamil.com>
"""

# import time
# import clr ## do not pip install clr  !!!!!!
# """There is a package named clr while the pythonnet package's alias is also clr. 
# So I removed clr by "pip uninstall clr" and then installed pythonnet by 'pip install pythonnet'. 
# Finally, everything works well.
# https://stackoverflow.com/questions/47913079/python-attributeerror-module-object-has-no-attribute-addreference"""

# clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll.")
# clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.KCube.PositionAlignerCLI.dll.")


# import Thorlabs.MotionControl.DeviceManagerCLI as Device
# import Thorlabs.MotionControl.KCube.PositionAlignerCLI as PosAligner



"""An example that uses the .NET Kinesis Libraries to connect to a KDC."""
import os
import time
import clr

clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.KCube.DCServoCLI.dll")
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.KCube.DCServoCLI import *
from System import Decimal



class KDC101:
    def __init__(self, serial_no = "27001253"):
        """Initialized the calss
        serial_no: the serial number of the KPA101 which wants to connect
        if the setial_no is none, 
        will then connect to the first dtected device through the detected serial number
        """
        # Build device list so that the library can find yours
        self.lightspeed_mmps = Decimal(0.299792458 / 2)
        device_list = DeviceManagerCLI.BuildDeviceList()
        print(device_list)
        serialnumbers = [str(ser) for ser in
                         DeviceManagerCLI.GetDeviceList()]
        print(f"Detected serialnumbers of the KPA is: {serialnumbers}" )
        # create new device
        if serial_no == None:
            serial_no = serialnumbers[0]
        self.serial_no = str(serial_no)  # Replace this line with your device's serial number
        # self.kcube = PosAligner.KCubePositionAligner.CreateKCubePositionAligner(self.serial_no)
        self.kcube = KCubeDCServo.CreateKCubeDCServo(self.serial_no)
        self.connect()
        self.enable_it()
        self.settings_init()
        self.get_config()
        self.Rotator_select()
        self.position=Decimal(0)
        try:
           # self.move(Decimal(0))
            self.Get_position()
        except Exception as e:
            print(e)
            print("Homing power rotator")
            self.Home_rotator()


        self.Get_position()
        print(f"power_rotation position: {self.positionOG}")
        self.Error=""
        
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
            self.kcube.WaitForSettingsInitialized(20000)  # 10 second timeout
            assert self.kcube.IsSettingsInitialized() is True
    
    def get_config(self):
        """get Device Configuration"""
        # PositionAlignerTrakConfiguration = self.kcube.GetPositionAlignerConfiguration(self.serial_no,\
        #                    PosAligner.PositionAlignerConfiguration.DeviceSettingsUseOptionType.UseDeviceSettings)
        
        self.m_config = self.kcube.LoadMotorConfiguration(self.serial_no,
                                                DeviceConfiguration.DeviceSettingsUseOptionType.UseFileSettings)    
        
        #Not used directly in example but illustrates how to obtain device settings
        # currentDeviceSettings = self.kcube.PositionAlignerDeviceSettings
        time.sleep(1)
    
    def Rotator_select(self):
        """ Select the detector 
        PRMTZ8,  """
       
        # PosAligner.GUISettings.Detectors = 0x01
        self.m_config.DeviceSettingsName = "PRM1Z8"
        self.m_config.UpdateCurrentConfiguration()
        self.kcube.SetSettings(self.kcube.MotorDeviceSettings, True, False)

    def Home_rotator(self):
        
        """Home the stage"""
        self.kcube.Home(60000)  # 10s timeout, blocking call
        print('Device Homed.')
    def move(self, f=50):
        # a = int(float(str(f).replace(",", "."))/360)
        #
        # f=f-a*360
        # if f < 0:
        #     f=f+360
        try:
            # Convert System.Decimal / Python float / string to normal Python float first
            f_float = float(str(f).replace(",", "."))
        except Exception as e:
            self.Error = f"Invalid angle input: {f}, error: {e}"
            print(self.Error)
            return

        # Wrap angle into 0-360 degrees
        f_float = f_float % 360.0
        if 0.0 <= f_float <= 360.0:
            self.kcube.MoveTo(Decimal(f_float), 10000)
            self.Error="Successfully moved"
        else:
            self.Error = "The position input is out of the delay stage bounds" #doesnt move the device if the input position is out of the device bounds
        time.sleep(0.5)
        self.Get_position()


    def Get_position(self):
        self.position  = self.kcube.Position/self.lightspeed_mmps
        self.positionOG = self.kcube.Position
        # print(f'Device now at position {position}')
        time.sleep(0.5)
    
    def close(self):
        """Stop pulling and disconnect the device
        """
        self.kcube.StopPolling()
        self.kcube.Disconnect(True)
     
#%%

            

#%%
if __name__ == "__main__":

    KDC = KDC101(serial_no = "27001253")
    KDC.connect()
    KDC.enable_it()
    KDC.get_device_info()
    KDC.settings_init()
    KDC.get_config()
    KDC.Rotator_select()
    KDC.Home_rotator()
    KDC.Rotate(f = 30)
   
    
    # PQD.close()
    
    