import os
import time
from moku.instruments import Datalogger

# Connect to the Moku device with force_connect=True to override any existing connections
i = Datalogger("[fe80::7269:79ff:feb9:4a22]")
print("1")
try:
    # Configure the frontend settings
    i.set_frontend(channel=2, impedance="1MOhm", coupling="DC", range="10Vpp")

    # Set the sampling rate
    i.set_samplerate(1000)

    # Set acquisition mode
    i.set_acquisition_mode(mode="Precision")

    # Generate a Sine wave on Output1
    # i.generate_waveform(channel=2, type="Sine", amplitude=0.1, frequency=10)

    # Ensure any existing logs are stopped before starting a new one
    i.stop_logging()

    # Start logging with immediate triggering to avoid waiting for a trigger event
    logFile = i.start_logging(
        duration=1,
        trigger_source="Immediate",  # Use immediate trigger
        comments="Sample_script",
    )

    # Track the progress of the logging session
    is_logging = True
    while is_logging:
        time.sleep(0.5)  # Wait for the logging session to progress
        progress = i.logging_progress()

        # Check if the 'time_remaining' key is available
        if "time_remaining" in progress:
            remaining_time = int(progress["time_remaining"])
            is_logging = remaining_time > 1
            print(f"Remaining time {remaining_time} seconds")
        else:
            print("Logging in progress, but 'time_remaining' not available.")
            is_logging = False

    # Download the log file from the Moku device
    i.download(
        "persist", logFile["file_name"], os.path.join(os.getcwd(), logFile["file_name"])
    )
    print("Downloaded log file to the local directory.")

except Exception as e:
    print(f"Exception occurred: {e}")

finally:
    # Ensure the connection to the Moku device is properly closed
    i.relinquish_ownership()
    print("Closed the connection to the device.")
