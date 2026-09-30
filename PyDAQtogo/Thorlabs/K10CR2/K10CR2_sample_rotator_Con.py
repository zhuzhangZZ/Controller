
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 18:08:28 2026
@author: Zhang101
"""
"""
K10CR2
An example that uses the .NET Kinesis Libraries to connect to a KPA101.
Adapter from Thorlabs github, https://github.com/Thorlabs/Motion_Control_Examples/tree/main/Python/KCube/KPA101
with more option, like set the PID parameters, get the mode inofomration .......
@author: Zhu Zhang <zhuzhang101@gamil.com>
"""
"""
Example Title: K10CR1_pythonnet.py
Example Date of Creation(YYYY-MM-DD) 2023-02-23
Example Date of Last Modification on Github 2025-04-09
Version of Python: 3.11
Version of the Thorlabs SDK used: 1.14.52
==================
Example Description
Using the .NET Dlls
Example runs the K10CR1 or K10CR2 stage. It shows how to initialize, home and move.
Tested with K10CR2
https://github.com/Thorlabs/Motion_Control_Examples/blob/main/Python/Kinesis/Integrated%20Stages/Cage%20Rotator/K10CR1_pythonnet.py
"""


import os
import time
import clr
# Write in file paths of dlls needed. 
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.IntegratedStepperMotorsCLI.dll")

# Import functions from dlls. 
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import MotorDirection
from Thorlabs.MotionControl.IntegratedStepperMotorsCLI import *
from System import Decimal 

# 2026-06-22 11:58:18.143 	Info 	55543194 	MoveToPosition Requested 	Position = 0

class K10CR2:
    def __init__(self, serial_no = "55543194"):
        """Initialized the calss
        serial_no: the serial number of the KPA101 which wants to connect
        if the setial_no is none, 
        will then connect to the first dtected device through the detected serial number
        """
        # Build device list so that the library can find yours
        device_list = DeviceManagerCLI.BuildDeviceList()
        print(device_list)
        self.lightspeed_mmps = Decimal(0.299792458 / 2)
        serialnumbers = [str(ser) for ser in
                         DeviceManagerCLI.GetDeviceList()]
        print(f"Detected serialnumbers of the K10CR2 is: {serialnumbers}" )
        # create new device
        if serial_no == None:
            serial_no = serialnumbers[0]
        self.serial_no = str(serial_no)  # Replace this line with your device's serial number
        # self.kcube = PosAligner.KCubePositionAligner.CreateKCubePositionAligner(self.serial_no)
        self.CRotator =  CageRotator.CreateCageRotator(self.serial_no)
        self.position = Decimal(0)
        self.connect()
        self.enable_it()
        self.settings_init()
        self.get_config()
   #     self.Rotator_select()
        self.position=Decimal(0)
        try:
         #   self.move(Decimal(0))
            self.Get_position()
        except Exception as e:
            print(e)
            print("Homing sample rotator")
            self.Home_rotator()


        self.Get_position()
        print(f"sample_rotation position: {self.positionOG}")
        self.Error=""
    def connect(self):
        """connect to the device through the provided serialnumber or detected serialnumber"""
        self.CRotator.Connect(self.serial_no)
        time.sleep(0.25)
        self.CRotator.StartPolling(250)
        time.sleep(0.25)  # wait statements are important to allow settings to be sent to the device
        
    def enable_it(self):
        """enable the device"""
        self.CRotator.EnableDevice()
        time.sleep(0.25)  # Wait for device to enable
         
    def get_device_info(self):
        """Get the device infomration. Name"""
        self.device_info = self.CRotator.GetDeviceInfo()
        print(self.device_info.Description)
    
    def settings_init(self):
        """# Wait for Settings to Initialise"""
        if not self.CRotator.IsSettingsInitialized():
            self.CRotator.WaitForSettingsInitialized(20000)  # 10 second timeout
            assert self.CRotator.IsSettingsInitialized() is True
    
    def get_config(self):
        """get Device Configuration"""
        # PositionAlignerTrakConfiguration = self.kcube.GetPositionAlignerConfiguration(self.serial_no,\
        #                    PosAligner.PositionAlignerConfiguration.DeviceSettingsUseOptionType.UseDeviceSettings)
        
        self.m_config = self.CRotator.LoadMotorConfiguration(self.serial_no, DeviceConfiguration.DeviceSettingsUseOptionType.UseFileSettings)    
        
        #Not used directly in example but illustrates how to obtain device settings
        # currentDeviceSettings = self.kcube.PositionAlignerDeviceSettings
        time.sleep(1)
    
 #   def Rotator_select(self):
   #      """ Select the detector
   #      PRMTZ8,  """
       
   #      PosAligner.GUISettings.Detectors = 0x01
    #     self.m_config.DeviceSettingsName = "PRM1Z8"
   #      self.m_config.UpdateCurrentConfiguration()
   #      self.CRotator.SetSettings(self.CRotator.MotorDeviceSettings, True, False)
    def set_direction(self, direction = 'forward'):
        if direction == "forward":
            self.CRotator.MoveContinuous(MotorDirection.Forward) # Set direction of Move
        elif direction == "backword":
            self.CRotator.MoveContinuous(MotorDirection.Backward)
        else:
            self.CRotator.MoveContinuous(MotorDirection.Forward)
    def Home_rotator(self):
        
        """Home the stage"""
        print("Homing Actuator")
        self.CRotator.Home(600000)  # 10s timeout, blocking call
        print('Device Homed.')
        
    def move(self, f=50):
        # a = int(float(str(f).replace(",", "."))/360)
        #
        # f= f-a*360
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
        if 0.0 <= f_float  <= 360.0:
            self.CRotator.MoveTo(Decimal(f_float ), 30000)
            self.Error="Successfully moved"
        else:
            self.Error = "The position input is out of the delay stage bounds" #doesnt move the device if the input position is out of the device bounds
        time.sleep(0.5)
        self.Get_position()


    def Get_position(self):
        self.position  = self.CRotator.Position/self.lightspeed_mmps
        self.positionOG = self.CRotator.Position
        # print(f'Device now at position {position}')
        time.sleep(0.5)
    
    def close(self):
        """Stop pulling and disconnect the device
        """
        self.CRotator.StopPolling()
        self.CRotator.Disconnect(True)
     
#%%

            

#%%
if __name__ == "__main__":
    CRotator = K10CR2(serial_no = "55543194")

    CRotator.move(Decimal(30))
    print(CRotator.positionOG)
    #CRotator.close()
    # PQD.close()
