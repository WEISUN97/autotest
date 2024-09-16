# Echo_WeiSUN_Issue

import os
import time

import json
from moku.instruments import Datalogger

i = Datalogger("[fe80::7269:79ff:feb0:9e0]", force_connect=True)

# Configure instruments to desired states
try:
    # Start logging session and read the file name from response
    response = i.start_logging(duration=10)
    # i.start_logging(duration=10,comments="Sample_script")
    file_name = response["file_name"]
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
        "persist",
        response["file_name"],
        os.path.join(os.getcwd(), response["file_name"]),
    )
    print("Downloaded log file to local directory.")
# Download file to local directory
# i.download("persist",file_name,f"~/Desktop/{file_name}")
except Exception as e:
    print(f"Exception occurred: {e}")
finally:
    # Close the connection to the Moku device
    # This ensures network resources are released correctly
    i.relinquish_ownership()
