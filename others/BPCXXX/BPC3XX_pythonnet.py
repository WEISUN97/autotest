"""
BPC3XX Pythonnet Example
Date of Creation(YYYY-MM-DD): 2023-07-28
Date of Last Modification on Github: 2023-07-28
Python Version Used: python 3.10.5
Kinesis Version Tested: 1.14.40

"""
import os
import time
import sys
import clr

clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericPiezoCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.Benchtop.PiezoCLI.dll")
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericPiezoCLI import *
from Thorlabs.MotionControl.GenericPiezoCLI import Piezo
from Thorlabs.MotionControl.GenericPiezoCLI import DeviceUnits
from Thorlabs.MotionControl.Benchtop.PiezoCLI import *
from System import Decimal  # necessary for real world units

def main():
    """The main entry point for the application"""

    # Uncomment this line if you are using
    SimulationManager.Instance.InitializeSimulations()

    try:

        DeviceManagerCLI.BuildDeviceList()

        # create new device.
        serial_no = "41845229"  # Replace this line with your device's serial number.
        # Set output voltage. 
        voltage = 50
        # Connect
        device = BenchtopPiezo.CreateBenchtopPiezo(serial_no)
        device.Connect(serial_no)
        # Retrieve channel for the device. Can call multiple times for (X) channels.
        channel = device.GetChannel(1)


        # attributes = dir(channel)
        # print(attributes)


        # Ensure that the device settings have been initialized.
        if not channel.IsSettingsInitialized():
            channel.WaitForSettingsInitialized(10000)  # 10 second timeout
            assert channel.IsSettingsInitialized() is True
        # Start polling and enable.
        channel.StartPolling(250)  #250ms polling rate
        time.sleep(25)
        channel.EnableDevice()
        time.sleep(0.25)  # Wait for device to enable

        # Get Device Information and display description.
        device_info = channel.GetDeviceInfo()
        print(device_info.Description)
        # Load any configuration settings needed by the controller/stage.
        motor_config = channel.GetPiezoConfiguration(channel.DeviceID)
        time.sleep(0.25)

        currentDeviceSettings = channel.PiezoDeviceSettings
        
        # Get Max voltage that is accessible.
        # maxVolts = channel.GetMaxOutputVoltage()


        print("Moving 10 times")
        pos = 0.1
        for i in range(10):
           pos += 0.1 
           channel.SetPosition(Decimal(pos))
           time.sleep(1) 
        print("Done", 'final pos = ', pos)

        # if Decimal(voltage) != Decimal(0) and Decimal(voltage) <= maxVolts:
        # #Update voltage if required using real world methods.
        #     # doesn't work
        #     # channel.SetOutputVoltage(Decimal(75))
        #     newVolts = channel.GetOutputVoltage()
        #     print(f"Voltage set to {maxVolts}", newVolts)
            


        # Stop Polling and Disconnect.
        channel.StopPolling()
        device.Disconnect()

    except Exception as e:
        print(e)

    # Uncomment this line if you are using Simulations
    # SimulationManager.Instance.UninitializeSimulations()
    ...


if __name__ == "__main__":
    main()