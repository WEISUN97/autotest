from BCP303.BCP303 import BPC303
from Sourcemeter.sourcemeter import Sourcemeter2401
from tool.tools import plot_data, plot_data_stage
import time
from datetime import datetime
import os

"""
Operation process:
1. Initialize the Scourcemeter and BCP303 stage
2. Start loop
    a. Move the stage and record the position
    b. Record the voltage data
4. Stop recording
5. Plot the data
"""


def operation(
    repeat_number,
    step_size,
    step_number,
    time_interval,
    display_plt=True,
):
    result = {"position": [], "voltage": []}
    try:
        # initialize the data logger
        bcp301 = BPC303()
        sm2401 = Sourcemeter2401(speed_nplc=0.05)
        formatted_time = datetime.now().strftime("%Y_%m_%d_%H_%M")
        for i in range(repeat_number):
            for step in range(repeat_number):
                step_start = time.perf_counter()
                position = bcp301.bcp303_move_stage(
                    step_size=step_size,
                    time_interval=time_interval,
                    step_number=step_number,
                )
                result["position"].append(position)
                time.sleep(0.25)
                voltage = sm2401.measure_voltage(duration=time_interval / 2, dt=0.01)
                result["voltage"].append(voltage)
                # remaining time to wait until the next step

                elapsed = time.perf_counter() - step_start
                remaining = time_interval - elapsed

                if remaining > 0:
                    time.sleep(remaining)
        # stop the stage and sourcemeter
        bcp301.bcp301_stop()
        sm2401.close()
        # save the data
        os.makedirs(f"./result/{formatted_time}", exist_ok=True)
        plot_data_stage(result, f"./result/{formatted_time}/data.png")
        with open(f"./result/{formatted_time}/data.txt", "w") as f:
            f.write(str(result))
    except Exception as e:
        print(f"Exception occurred: {e}")


# n = 19 # 18*0.25 = 4.5
n = 2
display_plt = False if n > 1 else True
for i in range(n):
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
