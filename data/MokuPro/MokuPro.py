#
# moku example: Basic Datalogger
#
# This example demonstrates use of the Datalogger instrument to log time-series
# voltage data to a (Binary or CSV) file.
#
# (c) 2021 Liquid Instruments Pty. Ltd.
#
import os
import time
import subprocess
from moku.instruments import Datalogger

"""
Output format can be: ([csv, mat, npy])
Samples for MokuPro:
waveform_settings = [
{'channel': 1, 'type': 'Sine', 'amplitude': 1, 'frequency': 100, 'symmetry': 50},
{'channel': 2, 'type': 'Ramp', 'amplitude': 0.5, 'frequency': 50, 'symmetry': 70}]

"""


class MokuPro:
    def __init__(self, IP="[fe80::7269:79ff:feb0:9e0]", output_format="csv"):
        self.i = None
        self.logFile = None
        self.output_format = output_format
        try:
            self.i = Datalogger(IP, force_connect=False)
        except Exception as e:
            # Close the connection to the Moku device
            # This ensures network resources and released correctly
            self.i.relinquish_ownership()
            print("Close the connection")
            print(f"Exception occurred: {e}")

    # Parameters suitable for MokuPro only (for mokuGo, check API list)
    def moku_parameters_settings(
        self,
        moku_sample_rate=100,
        channel_settings=[
            {"channel": 1, "impedance": "1MOhm", "coupling": "DC", "range": "400mVpp"},
            {"channel": 2, "impedance": "1MOhm", "coupling": "DC", "range": "4Vpp"},
        ],
        acquisition_mode="Precision",
        waveform_settings=None,
    ):

        try:
            # Configure input channels
            if channel_settings:
                for settings in channel_settings:
                    self.i.set_frontend(
                        channel=settings.get("channel", 1),
                        impedance=settings.get("impedance", "1MOhm"),
                        coupling=settings.get("coupling", "DC"),
                        range=settings.get("range", "40Vpp"),
                    )
                    # print(
                    #     f"Configured input channel {settings.get('channel')} with settings: {settings}"
                    # )

            # Configure waveform generation if provided
            if waveform_settings:
                for settings in waveform_settings:
                    self.i.generate_waveform(
                        channel=settings.get("channel", 1),
                        type=settings.get("type", "Sine"),
                        amplitude=settings.get("amplitude", 0),
                        frequency=settings.get("frequency", 10),
                        symmetry=settings.get("symmetry", 50),
                        offset=settings.get("offset", 0),
                        duty=settings.get("duty", 50),
                    )
            # Set the sample rate
            self.i.set_samplerate(moku_sample_rate)

            # Set acquisition mode
            self.i.set_acquisition_mode(mode=acquisition_mode)

        except Exception as e:
            # Close the connection to the Moku device
            # This ensures network resources and released correctly
            self.i.relinquish_ownership()
            print("Close the connection")
            print(f"Exception occurred: {e}")

    def moku_record(
        self,
        duration=1,
        start_time=0,
    ):
        try:
            # Configure the frontend
            start_time1 = time.perf_counter() - start_time
            print(f"Moku start: {start_time1}")
            self.logFile = self.i.start_logging(
                duration,
                trigger_source="Input2",
                trigger_level=0,
            )

            # Wait for the logging session to complete
            # delay = duration if duration >= 5 else duration + 1
            delay = duration
            time.sleep(delay)
            end_time1 = time.perf_counter() - start_time
            print(f"Moku end: {end_time1}")
            print(f"Moku worked: {end_time1-start_time1}s")
        except Exception as e:
            # Close the connection to the Moku device
            # This ensures network resources and released correctly
            self.i.relinquish_ownership()
            print("Close the connection")
            print(f"Exception occurred: {e}")

    def convert_li(self, input_file, output_format="csv"):
        try:
            # Construct the command as a list of arguments
            command = ["mokucli", "convert", input_file, f"--format={output_format}"]

            # Optionally specify output file path
            # command.extend(['--output', 'output.csv'])

            # Run the command using subprocess
            result = subprocess.run(command, capture_output=True, text=True)

            # Check if the command was successful
            if result.returncode == 0:
                print(f"Conversion successful: {result.stdout}")
            else:
                print(f"Error during conversion: {result.stderr}")
        except Exception as e:
            print(f"An exception occurred: {e}")

    def moku_download(self):
        # Download log from Moku, use liconverter to convert this .li file to .csv
        try:
            self.i.download(
                "ssd",
                self.logFile["file_name"],
                os.path.join(os.getcwd(), self.logFile["file_name"]),
            )
            print("Downloaded log file to local directory.")
            # Convert the .li file to .csv/.mat/.npy
            input_file = "./" + self.logFile["file_name"]  # Path to .li file
            self.convert_li(input_file, output_format=self.output_format)
            return input_file[:-2] + self.output_format

        except Exception as e:
            print(f"Exception occurred: {e}")
        finally:
            self.i.relinquish_ownership()
            print("Close the connection")


if __name__ == "__main__":
    MokuPro = MokuPro()
    MokuPro.moku_parameters_settings(
        waveform_settings=[
            {
                "channel": 1,
                "type": "Ramp",
                "amplitude": 0.5,
                "frequency": 1,
                "symmetry": 50,
            }
        ]
    )
    MokuPro.moku_record()
    MokuPro.moku_download()
