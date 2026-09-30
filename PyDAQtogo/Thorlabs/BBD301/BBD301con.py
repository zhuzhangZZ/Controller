"""
BBDXXX Pythonnet Example
Date of Creation(YYYY-MM-DD): 2022-06-21
Date of Last Modification on Github: 2022-08-11
Python Version Used: python3
Kinesis Version Tested: 1.14.34

"""
import os
import time
import sys
import clr

clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.Benchtop.BrushlessMotorCLI.dll")
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.Benchtop.BrushlessMotorCLI import *
from System import Decimal  # necessary for real world units

class BBD301(object):

    def __init__(self, serial_number):
        """The main entry point for the application"""

        try:
            DeviceManagerCLI.BuildDeviceList()
            # create new device
            self.serial_no = serial_number  # Replace this line with your device's serial number
            self.lightspeed_mmps = Decimal(0.299792458/2)
            # Connect and retrieve a channel
            self.device = BenchtopBrushlessMotor.CreateBenchtopBrushlessMotor(self.serial_no)
            self.device.Connect(self.serial_no)

            self.channel = self.device.GetChannel(1)

            # Start polling and enable
            self.channel.StartPolling(250)  # 250ms polling rate
            time.sleep(0.25)
            self.channel.EnableDevice()


            time.sleep(0.25)  # Wait for device to enable

            # Get Device Information and display description
            self.device_info = self.channel.GetDeviceInfo()
            print(self.device_info.Description)

            # Load any configuration settings needed by the controller/stage
            print(self.channel)
            self.motor_config = self.channel.LoadMotorConfiguration(self.channel.DeviceID)  # Device ID is the serial no + channel
            self.device_settings = self.channel.MotorDeviceSettings

            self.motor_config.UpdateCurrentConfiguration()

            self.channel.SetSettings(self.device_settings, False)

            if not self.channel.IsSettingsInitialized():
                self.channel.WaitForSettingsInitialized(10000)  # 10 second timeout
                assert self.channel.IsSettingsInitialized() is True

            # Get parameters related to homing/zeroing/other
            self.home_params = self.channel.GetHomingParams()
            print(f'Homing Velocity: {self.home_params.Velocity}\n',
                  f'Homing Direction: {self.home_params.Direction}')

            self.channel.SetHomingParams(self.home_params)  # If changes are made
            # Home or Zero the device (if a motor/piezo)
            try:
                self.channel.MoveTo(Decimal(20.0), 60000) #Homes the delay stage only if it isn't homed
            except Exception as e:
                print(e)
                print("Homing Channel")
                self.channel.Home(60000)  # 60 second timeout
            print("Channel Homed")
            time.sleep(1)

            # Get velocity parameters
            self.vel_params = self.channel.GetVelocityParams()
            print(f'Move Maximum Velocity: {self.vel_params.MaxVelocity}\n',
                  f'Move Acceleration: {self.vel_params.Acceleration}')

            # Move the device to a new position
            self.start_pos = Decimal(5.0)  # in real units
            print(f'Moving to {self.start_pos}')
            self.channel.MoveTo(self.start_pos, 60000)# 60 second timeout
            self.position = self.start_pos/self.lightspeed_mmps
            self.Error=""

        except Exception as e:
            print(e)
    def disconnect(self):
        # Stop Polling and Disconnect
        try:
            self.channel.StopPolling()
            self.device.Disconnect()
        except Exception as e:
            print(e)

    def move(self, pos):
        if Decimal(0.0) <= pos <= Decimal(220.0):
            self.channel.MoveTo(pos, 60000)
            self.position = self.channel.DevicePosition/self.lightspeed_mmps #gets the position of the device in light picoseconds
            self.Error="Successfully moved"
        else:
            self.Error = "The position input is out of the delay stage bounds" #doesnt move the device if the input position is out of the device bounds


if __name__ == "__main__":
    x=BBD301("103347074")
    x.device.Connect("103347074")

    x.channel = x.device.GetChannel(1)

    # Start polling and enable
    x.channel.StartPolling(250)  # 250ms polling rate
    time.sleep(0.25)
    x.channel.EnableDevice()

    time.sleep(1)
    x.move(Decimal(50.0))
    print(x.channel.IsDeviceBusy)
    time.sleep(1)
    print(x.channel.DevicePosition)
    x.disconnect()