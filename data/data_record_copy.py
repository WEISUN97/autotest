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


def convert_li(input_file, output_format="csv"):
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


def data_record(duration=1, mk2000=None):
    # Connect to your Moku by its ip address using Datalogger('[fe80::7269:79ff:feb0:9e0]')
    # or by its serial number using Datalogger(serial=000607)
    # i = Datalogger("[fe80::7269:79ff:feb9:4a22]", force_connect=False)
    i = Datalogger("[fe80::7269:79ff:feb0:9e0]", force_connect=False)

    try:
        # Configure the frontend
        i.set_frontend(channel=2, impedance="1MOhm", coupling="DC", range="4Vpp")
        # Log 100 samples per second
        samplerate = 100
        i.set_samplerate(samplerate)

        i.set_acquisition_mode(mode="Precision")

        # Generate Sine wave on Output1
        i.generate_waveform(
            channel=1, type="Ramp", amplitude=1, frequency=10, symmetry=50
        )

        # Stop an existing log, if any, then start a new one. 10 seconds of both
        # channels
        logFile = i.start_logging(
            duration=duration,
            trigger_source="Input2",
            trigger_level=0,
            comments="",
        )

        # temperatures = []
        # for _ in range(10):
        #     start_time = time.perf_counter()  # Start high-resolution timer

        #     # Call the temperature recording function
        #     temperature_record.read_temperature(mk2000, temperatures)

        #     # Calculate elapsed time
        #     elapsed_time = time.perf_counter() - start_time

        #     # Sleep for the remaining time of the interval if needed
        #     sleep_time = 0.1 - elapsed_time
        #     if sleep_time > 0:
        #         time.sleep(sleep_time)  # Adjust sleep to maintain precise timing
        #     else:
        #         print("Warning: Function execution took longer than the interval.")

        # Download log from Moku, use liconverter to convert this .li file to .csv
        i.download(
            "ssd", logFile["file_name"], os.path.join(os.getcwd(), logFile["file_name"])
        )
        print("Downloaded log file to local directory.")

        # Convert the .li file to .csv/.mat/.npy
        input_file = "./" + logFile["file_name"]  # Path to .li file
        output_format = "csv"  # Output format ([csv, mat, npy])
        convert_li(input_file, output_format="csv")

    except Exception as e:
        # Close the connection to the Moku device
        # This ensures network resources and released correctly
        i.relinquish_ownership()
        print("Close the connection")
        print(f"Exception occurred: {e}")
    finally:
        # Close the connection to the Moku device
        # This ensures network resources and released correctly
        i.relinquish_ownership()
        print("Close the connection")
    return input_file[:-2] + output_format


if __name__ == "__main__":
    a = data_record()
    print(a)
