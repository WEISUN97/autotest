from data.data_record import DataLogger
from stage_control.BPC301 import BPC301
from threading import Thread
from tool.tools import plot_data
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


def operation(origin, repeat_number, step_size, step_number, time_interval):
    try:

        # initialize the data logger
        dataLogger = DataLogger(duration=21)
        # initialize the stage controller
        bcp301 = BPC301(origin=origin)
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
        # Start time of the experiment
        start_time = time.perf_counter()
        current_time = datetime.now()
        # Format the date and time as 'year_month_day_hour_min'
        formatted_time = current_time.strftime("%Y_%m_%d_%H_%M")
        os.makedirs(f"./result/{formatted_time}", exist_ok=True)
        bcp301_stageThread = Thread(
            target=bcp301.bcp301_move_stage,
            args=(
                repeat_number,
                step_size,
                step_number,
                time_interval,
                start_time,
                formatted_time,
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
            moku_thread, temperature_thread, formatted_time
        )
        # Plot the data
        plot_data(
            moku_file,
            moku_channels=[1],
            temperatures=temperatures,
            stagePositions=bcp301_position,
            formatted_time=formatted_time,
        )

    except Exception as e:
        print(f"Exception occurred: {e}")


# Define default values for the stage movement
origin = 0  # origin position of the stage
repeat_number = 2  # number of times the stage will move
step_size = 0.2  # step size in um
step_number = 10  # number of steps
time_interval = 1  # time interval in seconds
operation(origin, repeat_number, step_size, step_number, time_interval)
