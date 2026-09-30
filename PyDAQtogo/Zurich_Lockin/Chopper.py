import clr
import sys
import time
# Load the .NET assembly (Update with the correct path)
dll_path = r"C:\Program Files\New Focus\New Focus Chopper Application\Samples\CmdLib3502.dll"
sys.path.append(dll_path)
clr.AddReference(dll_path)  # Load the .NET DLL

# Import the correct namespace and class
from NewFocus.ChopperApp import CmdLib3502

class C3502(object):
    def __init__(self):
        # Initialize the chopper library (False for no logging)
        self.chopper = CmdLib3502(False)

        # Discover devices
        self.chopper.DiscoverDevices()

        # Get number of connected devices
        num_devices = self.chopper.GetDeviceCount()
        print(f"Number of devices found: {num_devices}")

        device_keys = self.chopper.GetDeviceKeys()

        self.device_key = device_keys[0]  # Select first detected device
        self.p = self.chopper.GetPhaseDelay(self.device_key, 0.0)[1]

    def CON(self):
         self.chopper.SetSync(self.device_key, 1)

    def COFF(self):
         self.chopper.SetSync(self.device_key, 0)
    def autophase(self):
        self.chopper.SetSetButton(self.device_key, 1)
        i = 0
        if self.p<0:
            while i<18:
                self.chopper.SendKey(self.device_key, 2)
                i+=1
            self.p = self.chopper.GetPhaseDelay(self.device_key, 0.0)[1]
        else:
            while i<18:
                self.chopper.SendKey(self.device_key, 1)
                i+=1
            self.p = self.chopper.GetPhaseDelay(self.device_key, 0.0)[1]
    def phaseplus10(self):
        self.chopper.SetSetButton(self.device_key, 1)
        self.chopper.SendKey(self.device_key, 2)
        self.p = self.chopper.GetPhaseDelay(self.device_key, 0.0)[1]
    def phasemin10(self):
        self.chopper.SetSetButton(self.device_key, 1)
        self.chopper.SendKey(self.device_key, 1)
        self.p = self.chopper.GetPhaseDelay(self.device_key, 0.0)[1]
