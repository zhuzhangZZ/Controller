"""An example that uses the .NET Kinesis Libraries to connect to a KDC."""
import os
import time
import sys
import clr

clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.KCube.BrushlessMotorCLI.dll")
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.KCube.BrushlessMotorCLI import *
from System import Decimal  # necessary for real world units

class KBD101(object):

    def __init__(self, serial_number):
        """The main entry point for the application"""

        try:
            DeviceManagerCLI.BuildDeviceList()
            # create new device
            self.serial_no = serial_number  # Replace this line with your device's serial number
            self.lightspeed_mmps = Decimal(0.299792458/2)
            # Connect and retrieve a channel
            self.device = KCubeBrushlessMotor.CreateKCubeBrushlessMotor(self.serial_no)
            self.device.Connect(self.serial_no)

            # Start polling and enable
            self.device.StartPolling(250)  # 250ms polling rate
            time.sleep(0.25)
            self.device.EnableDevice()
            time.sleep(0.25)  # Wait for device to enable

            # Get Device Information and display description
            self.device_info = self.device.GetDeviceInfo()
            print(self.device_info.Description)

            # Load any configuration settings needed by the controller/stage
            print(self.device)

            if not self.device.IsSettingsInitialized():
                self.device.WaitForSettingsInitialized(10000)  # 10 second timeout
                assert self.device.IsSettingsInitialized() is True

            m_config = self.device.LoadMotorConfiguration(self.serial_no, DeviceConfiguration.DeviceSettingsUseOptionType.UseDeviceSettings)
            time.sleep(1)
            try:
                self.device.MoveTo(Decimal(20.0), 60000) #Homes the delay stage only if it isn't homed
            except Exception as e:
                print(e)
                print("Homing Channel")
                self.device.Home(60000)  # 60 second timeout
            print("Channel Homed")
            time.sleep(1)
            self.device.SetVelocityParams(Decimal(100), Decimal(1000))
            self.vel_params = self.device.GetVelocityParams()
            print(f'Move Maximum Velocity: {self.vel_params.MaxVelocity}\n',
                  f'Move Acceleration: {self.vel_params.Acceleration}')


            # Move the device to a new position
            self.start_pos = Decimal(5.0)  # in real units
            print(f'Moving to {self.start_pos}')
            self.device.MoveTo(self.start_pos, 60000)# 60 second timeout
            self.position = self.start_pos/self.lightspeed_mmps
            self.Error=""

            self.start_time=0
            self.end_time=0

        except Exception as e:
            print(e)
    def disconnect(self):
        # Stop Polling and Disconnect
        self.device.StopPolling()
        self.device.Disconnect()

    def move(self, pos):
        if Decimal(0.0) <= pos <= Decimal(100):
            self.device.MoveTo(pos, 60000)
            self.position = self.device.DevicePosition/self.lightspeed_mmps #gets the position of the device in light picoseconds
            self.Error="Successfully moved"

        else:
            self.Error = "The position input is out of the delay stage bounds" #doesnt move the device if the input position is out of the device bounds
    def slowscan(self, startpos, finishpos, step):
        if Decimal(0.0) <= Decimal(startpos)*self.lightspeed_mmps <= Decimal(100):
            self.move(Decimal(startpos)*self.lightspeed_mmps)
            i=0
            n=int((finishpos-startpos)/step+1)
            while i<n:
                self.move((Decimal(startpos+(i+1)*step))*self.lightspeed_mmps)
                time.sleep(0.2)
                print(self.position)
                i+=1
            print("Done")




if __name__ == "__main__":
    x=KBD101("28252518")
    time.sleep(1)
    x.move(Decimal(30.0))
    time.sleep(1)
    x.slowscan(0, 330, 0.01)
    x.disconnect()