"""
BPC3XX Pythonnet Example
Date of Creation(YYYY-MM-DD): 2023-07-28
Date of Last Modification on Github: 2023-07-28
Python Version Used: python 3.10.5
Kinesis Version Tested: 1.14.40

Pizo controller: BPC303
"""

from datetime import datetime
import os
import time
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# from tool.tools import save_data_to_csv

import clr

clr.AddReference(
    "C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll"
)
clr.AddReference(
    "C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericPiezoCLI.dll"
)
clr.AddReference(
    "C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.Benchtop.PiezoCLI.dll"
)
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericPiezoCLI import *
from Thorlabs.MotionControl.GenericPiezoCLI import Piezo
from Thorlabs.MotionControl.GenericPiezoCLI import DeviceUnits
from Thorlabs.MotionControl.Benchtop.PiezoCLI import *
from System import Decimal  # necessary for real world units


class BPC303:
    def __init__(
        self,
        serial_no="71492464",
        origin=0,
        need_initialized=[True, True],
        channel_id=1,
        device=None,
        # self, serial_no="41845229", origin=0, back=False, need_initialized=[True, True]
    ):
        self.serial_no = serial_no
        self.origin = origin
        self.device = device
        self.need_initialized = need_initialized
        self.channel_id = channel_id
        try:
            if not device:
                # create new device.
                self.device = BenchtopPiezo.CreateBenchtopPiezo(serial_no)
                """The main entry point for the application"""
                # Uncomment this line if you are using
                SimulationManager.Instance.InitializeSimulations()
                DeviceManagerCLI.BuildDeviceList()

                # Set output voltage.
                voltage = 50
                self.device.Connect(self.serial_no)
                # Retrieve channel for the device. Can call multiple times for (X) channels.
            channel = self.device.GetChannel(self.channel_id)
            self.channel = channel
            # attributes = dir(channel)
            # print(attributes)

            # Ensure that the device settings have been initialized.
            if not channel.IsSettingsInitialized():
                channel.WaitForSettingsInitialized(10000)  # 10 second timeout
                assert channel.IsSettingsInitialized() is True
            # Start polling and enable.
            """
            The polling rate refers to how frequently a system checks for updates or retrieves data from a device, sensor, or system. 
            In your context, channel.StartPolling(250) means that the system is set to check or poll the device for new data every 250 milliseconds
            """
            channel.StartPolling(250)  # 250ms polling rate
            # default is 25s
            time.sleep(5)
            channel.EnableDevice()
            time.sleep(0.25)  # Wait for device to enable

            # Get Device Information and display description.
            device_info = channel.GetDeviceInfo()
            print(device_info.Description + " initialized")
            # Load any configuration settings needed by the controller/stage.
            motor_config = channel.GetPiezoConfiguration(channel.DeviceID)
            time.sleep(0.5)
            # Move the stage to the origin
            self.channel.SetPosition(Decimal(self.origin))
            time.sleep(0.5)
        except Exception as e:
            print(e)

    def move_to_origin(self, start_position=0):
        try:
            self.channel.SetPosition(Decimal(start_position))
            time.sleep(2)
            return float(str(self.channel.GetPosition()))
        except Exception as e:
            print(e)

    # Move the stage
    def bcp303_move_stage(
        self,
        step_size=1,
        current_position=0,
    ):
        # step_size in um, time_interval in seconds
        try:
            position = current_position + step_size
            self.channel.SetPosition(Decimal(position))
            time.sleep(0.5)
            currentPosition = float(str(self.channel.GetPosition()))
            return currentPosition
        except Exception as e:
            print(e)

    def bcp303_stop(self, ifback=True):
        try:
            print("Stage Moving Done")
            if ifback:
                self.move_to_origin()
            # Stop Polling and Disconnect.
            self.channel.StopPolling()
            self.device.Disconnect()
            print("Stage disconnected")

        except Exception as e:
            # Stop Polling and Disconnect.
            self.channel.StopPolling()
            self.device.Disconnect()
            print("Stage disconnected")
            print(e)

    def get_device(self):
        return self.device


if __name__ == "__main__":
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y_%m_%d_%H_%M")
    os.makedirs(f"./result/{formatted_time}", exist_ok=True)
    bcp303 = BPC303(channel_id=2)
    bcp303.bcp303_move_stage(step_size=1, current_position=0)
    bcp303.bcp303_stop()
