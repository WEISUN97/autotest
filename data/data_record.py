import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data.MK2000.MK2000 import MK2000
from data.MokuPro.MokuPro import MokuPro
from threading import Thread
from datetime import datetime


"""
For Moku: 
MokuPro IP: "[fe80::7269:79ff:feb0:9e0]", Moku Go IP: "[fe80::7269:79ff:feb9:4a22]"
Input 1 / Channel 1: Signal from AFM

For MK2000: temperature record sample rate: 10Hz
"""


class DataLogger(MK2000, MokuPro):
    # initialize the MK2000 and MokuPro
    def __init__(
        self,
        MokuIP="[fe80::7269:79ff:feb0:9e0]",
        output_format="csv",
        serial_port="COM3",
        duration=10,
        unable_device=[],
    ):
        device_dic = {"MK2000": True, "MokuPro": True}
        try:
            if len(unable_device) != 0:
                for i in range(len(unable_device)):
                    if unable_device[i] == "MK2000":
                        device_dic["MK2000"] = False
                    elif unable_device[i] == "MokuPro":
                        device_dic["MokuPro"] = False
        except ValueError as ve:
            print(ve)
            print("Please enter the correct device name")

        if len(unable_device) != 0:
            for i in range(len(unable_device)):
                if unable_device[i] not in device_dic:
                    print("Please enter the correct device name")
                    break
                else:
                    if unable_device[i] == "MK2000":
                        device_dic["MK2000"] = False
                    elif unable_device[i] == "MokuPro":
                        device_dic["MokuPro"] = False
        self.device_dic = device_dic
        self.moku_file = None
        self.temperatures = [[], []]  # store the temperature data [time, temperature]
        self.duration = duration
        self.mk2000_sample_rate = 20
        if device_dic["MK2000"]:
            MK2000.__init__(self, serial_port=serial_port)
        if device_dic["MokuPro"]:
            MokuPro.__init__(
                self,
                IP=MokuIP,
                output_format=output_format,
            )

    def moku_settings(
        self,
        mk2000_sample_rate=20,
        moku_sample_rate=100,
        channel_settings=[
            {"channel": 1, "impedance": "50Ohm", "coupling": "DC", "range": "400mVpp"},
            # {"channel": 2, "impedance": "1MOhm", "coupling": "DC", "range": "4Vpp"},
        ],
        acquisition_mode="Precision",
        waveform_settings=None,
    ):
        self.moku_sample_rate = moku_sample_rate
        self.mk2000_sample_rate = mk2000_sample_rate
        self.moku_parameters_settings(
            moku_sample_rate=moku_sample_rate,
            channel_settings=channel_settings,
            waveform_settings=waveform_settings,
            acquisition_mode=acquisition_mode,
        )
        print("Moku initialized")

    def signal_record(self, start_time=0, formatted_time="None"):
        moku_thread = Thread(target=self.moku_record, args=(self.duration, start_time))
        temperature_thread = (
            Thread(
                target=self.mk2000_read_temperature,
                args=(
                    self.duration,
                    self.mk2000_sample_rate,
                    self.temperatures,
                    start_time,
                    formatted_time,
                ),
            )
            if self.device_dic["MK2000"]
            else None
        )
        # Start both threads
        moku_thread.start()
        if self.device_dic["MK2000"]:
            temperature_thread.start()
        return moku_thread, temperature_thread

    def log_complete_work(self, moku_thread, temperature_thread, formatted_time):
        # Wait for both threads to complete
        moku_thread.join()
        if self.device_dic["MK2000"]:
            temperature_thread.join()
        # get the temperature data and the path of the moku file
        self.moku_file = self.moku_download(formatted_time)
        # print(f"MK2000 temperature data: {len(self.temperatures)}")
        return self.moku_file, self.temperatures


if __name__ == "__main__":
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y_%m_%d_%H_%M")
    os.makedirs(f"./result/{formatted_time}", exist_ok=True)
    dataLogger = DataLogger(duration=2)
    dataLogger.moku_settings(
        moku_sample_rate=1000,
        mk2000_sample_rate=25,
        waveform_settings=[
            {
                "channel": 1,
                "type": "Sine",
                "amplitude": 1,
                "frequency": 1,
                # "symmetry": 50,
            }
        ],
    )
    a, b = dataLogger.signal_record(formatted_time=formatted_time)
    dataLogger.log_complete_work(a, b, formatted_time)
