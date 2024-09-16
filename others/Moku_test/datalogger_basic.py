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

from moku.instruments import Datalogger

# Connect to your Moku by its ip address using Datalogger('[fe80::7269:79ff:feb0:9e0]')
# or by its serial number using Datalogger(serial=000607)
# i = Datalogger("[fe80::7269:79ff:feb9:4a22]", force_connect=False)
i = Datalogger("[fe80::7269:79ff:feb0:9e0]", force_connect=False)


try:
    # Configure the frontend
    i.set_frontend(channel=2, impedance="1MOhm", coupling="DC", range="400mVpp")
    # Log 100 samples per second
    i.set_samplerate(1000)

    i.set_acquisition_mode(mode="Precision")

    # Generate Sine wave on Output1
    i.generate_waveform(channel=2, type="Sine", amplitude=0.1, frequency=10)

    # Stop an existing log, if any, then start a new one. 10 seconds of both
    # channels
    logFile = i.start_logging(
        duration=10,
        trigger_source="Input2",
        trigger_level=-0.200000,
        comments="Sample_script",
    )

    # Track progress percentage of the data logging session
    is_logging = True
    while is_logging:
        # Wait for the logging session to progress by sleeping 0.5sec
        time.sleep(0.5)
        # Get current progress percentage and print it out
        progress = i.logging_progress()
        remaining_time = int(progress["time_remaining"])
        is_logging = remaining_time > 1
        print(f"Remaining time {remaining_time} seconds")

    # Download log from Moku, use liconverter to convert this .li file to .csv
    i.download(
        "persist", logFile["file_name"], os.path.join(os.getcwd(), logFile["file_name"])
    )
    print("Downloaded log file to local directory.")

# except Exception as e:
#     print(f"Exception occurred: {e}")
finally:
    # Close the connection to the Moku device
    # This ensures network resources and released correctly
    i.relinquish_ownership()
    print("Close the connection")
