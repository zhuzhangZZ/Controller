# -*- coding: utf-8 -*-
"""
Created on Sun May  5 12:00:01 2024

@author: PDSM
"""
#%%# Get the assembly objects
import System
device_manager_assembly = System.Reflection.Assembly.LoadFile("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
kcube_assembly = System.Reflection.Assembly.LoadFile("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.KCube.PositionAlignerCLI.dll")

# Function to save all types and their members in an assembly to a file
def save_types_and_members(assembly, file):
    writer = open(file, 'a')  # Open file in append mode
    for type in assembly.GetTypes():
        writer.write(f"Type: {type.FullName}\n")
        for method in type.GetMethods():
            writer.write(f"  Method: {method.Name}\n")
        for prop in type.GetProperties():
            writer.write(f"  Property: {prop.Name}\n")
    writer.close()  # Close the file

# File paths
device_manager_file = "DeviceManagerDetails.txt"
kcube_file = "KCubeDetails.txt"

# Get the assembly objects
device_manager_assembly = System.Reflection.Assembly.LoadFile("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
kcube_assembly = System.Reflection.Assembly.LoadFile("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.KCube.PositionAlignerCLI.dll")

# Save details of the Device Manager assembly
save_types_and_members(device_manager_assembly, device_manager_file)

# Save details of the KCube Position Aligner assembly
save_types_and_members(kcube_assembly, kcube_file)

print("All types, methods, and properties have been saved to their respective files.")