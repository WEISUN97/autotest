"""
BPC3XX Pythonnet Example
Date of Creation(YYYY-MM-DD): 2023-07-28
Date of Last Modification on Github: 2023-07-28
Python Version Used: python 3.10.5
Kinesis Version Tested: 1.14.40

Pizo controller: BPC301
"""

from datetime import datetime
import os
import time
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tool.tools import save_data_to_csv

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


class BPC301:
    def __init__(self, serial_no="41845229", origin=0, back=False):
        self.serial_no = serial_no
        self.origin = origin
        self.device = None
        self.channel = None
        self.bcp301_position = [[], []]
        self.back = back

        try:
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
            channel = self.device.GetChannel(1)
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
            time.sleep(0.25)
            # Move the stage to the origin
            self.channel.SetPosition(Decimal(self.origin))

        except Exception as e:
            print(e)

    # Move the stage
    def bcp301_move_stage(
        self,
        repeat_number=1,
        step_size=0.1,
        step_number=10,
        time_interval=1,
        start_time=0,
        formatted_time="None",
        back=False,
    ):
        # step_size in um, time_interval in seconds
        try:
            start_time1 = time.perf_counter() - start_time
            print(f"Stage Moving Started: {start_time1}")
            for k in range(repeat_number):
                position = self.origin
                bcp301_record_time = time.perf_counter() - start_time
                currentPosition = float(str(self.channel.GetPosition()))
                self.bcp301_position[1] += [currentPosition]
                self.bcp301_position[0] += [bcp301_record_time]
                for i in range(step_number):
                    position += step_size
                    self.channel.SetPosition(Decimal(position))
                    time.sleep(time_interval)
                    bcp301_record_time = time.perf_counter() - start_time
                    currentPosition = float(str(self.channel.GetPosition()))
                    self.bcp301_position[1] += [currentPosition]
                    self.bcp301_position[0] += [bcp301_record_time]
                # back
                if self.back:
                    for i in range(step_number):
                        position -= step_size
                        self.channel.SetPosition(Decimal(position))
                        time.sleep(time_interval)
                        bcp301_record_time = time.perf_counter() - start_time
                        currentPosition = float(str(self.channel.GetPosition()))
                        self.bcp301_position[1] += [currentPosition]
                        self.bcp301_position[0] += [bcp301_record_time]
                        # print(f"Current Position: {currentPosition}")
                self.channel.SetPosition(Decimal(self.origin))
                time.sleep(time_interval)
            end_time1 = time.perf_counter() - start_time
            print(f"Stage moved: {end_time1-start_time1}s")
            print("Stage Moving Done")
            # Stop Polling and Disconnect.
            self.channel.StopPolling()
            self.device.Disconnect()
            print("Stage disconnected")
            current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_data_to_csv(
                f"./result/{formatted_time}/StageBCP301_data{current_date}_ss{step_size}_sn{step_number}_ti{time_interval}.csv",
                self.bcp301_position,
                titles=["Time", "Position(um)"],
            )

        except Exception as e:
            # Stop Polling and Disconnect.
            self.channel.StopPolling()
            self.device.Disconnect()
            print("Stage disconnected")
            print(e)

        # Uncomment this line if you are using Simulations
        # SimulationManager.Instance.UninitializeSimulations()

    def bcp301_complete_work(self, bcp301_thread):
        # Wait for both threads to complete
        bcp301_thread.join()
        return self.bcp301_position


if __name__ == "__main__":
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y_%m_%d_%H_%M")
    os.makedirs(f"./result/{formatted_time}", exist_ok=True)
    bcp301 = BPC301()
    bcp301.bcp301_move_stage(formatted_time=formatted_time)
