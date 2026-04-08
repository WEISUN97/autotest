from BCP303.BCP303 import BPC303
from Sourcemeter.sourcemeter import Sourcemeter2401
from tool.tools import post_process
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
6. 16px=1um at 20% 4096X3288
Clockwise: away from samples, up 
"""


def operation(stage_setting):
    repeat_number = stage_setting["repeat_number"]
    step_size = stage_setting["step_size"]
    step_number = stage_setting["step_number"]
    time_interval = stage_setting["time_interval"]
    start_position = stage_setting["start_position"]
    step_size_z = stage_setting["step_size_z"]
    result = {"position": [], "voltage": []}
    try:
        # initialize the data logger
        # height controller
        bcp303_z = BPC303(channel_id=2)
        bcp303_z.move_to_origin()
        # moving controller
        bcp303 = BPC303(channel_id=1)
        sm2401 = Sourcemeter2401(speed_nplc=0.1)
        bcp303.move_to_origin()
        position = bcp303.move_to_origin(start_position=start_position)
        for i in range(repeat_number):
            position_z = bcp303_z.bcp303_move_stage(
                step_size=step_size_z,
                current_position=position_z,
            )
            for step in range(step_number):
                step_start = time.perf_counter()
                position = bcp303.bcp303_move_stage(
                    step_size=step_size,
                    current_position=position,
                )
                result["position"].append(position)
                voltage = sm2401.measure_voltage(duration=time_interval / 4, dt=0.01)[
                    "voltage"
                ]
                result["voltage"].append(voltage)
                # remaining time to wait until the next step
                elapsed = time.perf_counter() - step_start
                remaining = time_interval - elapsed
                if remaining > 0:
                    time.sleep(remaining)
            sm2401_settings = sm2401.getSettings()
            settings = {"stage": setting, "sourcemeter": sm2401_settings}
            post_process(
                chip_name="chip_test",
                sample_name="beam_test",
                result=result,
                config=settings,
                repeat=repeat_number,
                position_z=position_z,
            )
        # stop the stage and sourcemeter
    except Exception as e:
        print(f"Exception occurred: {e}")
    finally:
        time.sleep(0.5)
        sm2401.close()
        bcp303.bcp303_stop(ifback=True)
        return result, settings


if __name__ == "__main__":
    # Define default values for the stage movement
    setting = {
        "start_position": 0,
        "repeat_number": 1,
        "step_size": 0.005,
        "step_number": 500,
        "time_interval": 2,
        "step_size_z": 1,
    }
    operation(setting)
