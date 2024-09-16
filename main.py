from data.data_record import DataLogger
from stage_control.BPC301 import BPC301
from threading import Thread
from tool.tools import plot_data
import time

"""
Operation process:
1. Record moku/temperature data
2. Start moving the stage
3. Wait for the stage to complete the movement
4. Stop the moku/temperature recording
5. Plot the data
"""

# Define default values for the stage movement
origin = 0
repeat_number = 2
step_size = 0.2
step_number = 10
time_interval = 1


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
    bcp301_stageThread = Thread(
        target=bcp301.bcp301_move_stage,
        args=(repeat_number, step_size, step_number, time_interval, start_time),
    )
    # Record the moku and temperature data
    moku_thread, temperature_thread = dataLogger.signal_record(start_time)
    # Start the stage movement
    bcp301_stageThread.start()

    # Wait for all threads to complete
    bcp301_position = bcp301.bcp301_complete_work(bcp301_stageThread)
    moku_file, temperatures = dataLogger.log_complete_work(
        moku_thread, temperature_thread
    )
    # Plot the data
    plot_data(
        moku_file,
        moku_channels=[1, 2],
        temperatures=temperatures,
        stagePositions=bcp301_position,
    )


except Exception as e:
    print(f"Exception occurred: {e}")