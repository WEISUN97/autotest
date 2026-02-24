from data.data_record import DataLogger
from stage_control.BPC301 import BPC301
from threading import Thread
from tool.tools import plot_data, plot_data_stage
import time
from datetime import datetime
import os

"""
Operation process:
1. Record moku/temperature data
2. Start moving the stage
3. Wait for the stage to complete the movement
4. Stop the moku/temperature recording
5. Plot the data
"""


def operation(
    duration,
    origin,
    repeat_number,
    step_size,
    step_number,
    time_interval,
    wafeform_settings,
    display_plt=True,
):
    try:
        # initialize the data logger
        dataLogger = DataLogger(duration=duration, disable_device=["MK2000"])
        # initialize the stage controller
        bcp301 = BPC301(origin=origin, back=False)
        MDT693_voltage = wafeform_settings[0]["dc_level"]
        dataLogger.moku_settings(
            moku_sample_rate=10000,
            mk2000_sample_rate=1,
            waveform_settings=wafeform_settings,
            channel_settings=[
                {
                    "channel": 1,
                    "impedance": "50Ohm",
                    "coupling": "DC",
                    "range": "400mVpp",
                },
                # {"channel": 2, "impedance": "1MOhm", "coupling": "DC", "range": "4Vpp"},
            ],
        )
        # Start time of the experiment
        start_time = time.perf_counter()
        current_time = datetime.now()
        # Format the date and time as 'year_month_day_hour_min'
        formatted_time = current_time.strftime("%Y_%m_%d_%H_%M")
        os.makedirs(f"./result/{formatted_time}_{MDT693_voltage}V", exist_ok=True)
        bcp301_stageThread = Thread(
            target=bcp301.bcp301_move_stage,
            args=(
                repeat_number,
                step_size,
                step_number,
                time_interval,
                start_time,
                formatted_time,
                MDT693_voltage,
            ),
        )
        # Record the moku and temperature data
        moku_thread, temperature_thread = dataLogger.signal_record(
            start_time, formatted_time
        )
        # Start the stage movement
        bcp301_stageThread.start()

        # Wait for all threads to complete
        bcp301_position = bcp301.bcp301_complete_work(bcp301_stageThread)
        moku_file, temperatures = dataLogger.log_complete_work(
            moku_thread, temperature_thread, formatted_time, MDT693_voltage
        )
        # Plot the data
        # temperature included
        if temperatures[0]:
            plot_data(
                moku_file,
                moku_channels=[1],
                temperatures=temperatures,
                stagePositions=bcp301_position,
                formatted_time=formatted_time,
                step_size=step_size,
            )

        # temperature not included
        if not temperatures[0]:
            plot_data_stage(
                moku_file,
                moku_channels=[1],
                stagePositions=bcp301_position,
                formatted_time=formatted_time,
                step_size=step_size,
                MDT693_voltage=MDT693_voltage,
                display_plt=display_plt,
            )

    except Exception as e:
        print(f"Exception occurred: {e}")


# Define default values for the waveform settings
wafeform_settings = [
    {
        "channel": 1,
        "type": "DC",
        "dc_level": 0,
    }
]

# n = 19 # 18*0.25 = 4.5
n = 2
display_plt = False if n > 1 else True
for i in range(n):
    wafeform_settings[0]["dc_level"] = i * 0.25
    # Define default values for the stage movement
    origin = 0
    repeat_number = 1
    step_size = 0.05
    step_number = 2
    time_interval = 1
    running_time = repeat_number * step_number * time_interval
    operation(
        running_time,
        origin,
        repeat_number,
        step_size,
        step_number,
        time_interval,
        wafeform_settings,
        display_plt,
    )


# # Define default values for the stage movement
# origin = 3.8  # origin position of the stage
# repeat_number = 1  # number of times the stage will move
# step_size = 0.01  # step size in um
# step_number = 200  # number of steps
# time_interval = 1  # time interval in seconds
# running_time = repeat_number * step_number * time_interval  # total running time
