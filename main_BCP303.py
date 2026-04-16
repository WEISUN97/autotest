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


def operation(
    stage_settings=None,
    chip_name="chip_test",
    sample_name="beam_test",
):
    repeat_number = stage_settings["repeat_number"]
    step_size = stage_settings["step_size"]
    step_number = stage_settings["step_number"]
    time_interval = stage_settings["time_interval"]
    start_position = stage_settings["start_position"]
    step_size_z = stage_settings["step_size_z"]
    total_steps = repeat_number * step_number
    count = 1
    formatted_time = datetime.now().strftime("%Y%m%d%H%M")
    try:
        # initialize the data logger
        # height controller
        bcp303_z = BPC303(channel_id=2)
        bcp303_device = bcp303_z.get_device()
        # moving controller
        bcp303 = BPC303(channel_id=1, device=bcp303_device)
        # Sourcemeter
        sm2401 = Sourcemeter2401(speed_nplc=0.1)
        position_z = bcp303_z.move_to_origin(
            start_position=stage_settings["position_z"]
        )
        allData = [_ for _ in range(repeat_number)]
        for i in range(repeat_number):
            allData[i] = {"position": [], "voltage": []}
            bcp303.move_to_origin()
            time.sleep(1)
            if i > 0:
                position_z = bcp303_z.bcp303_move_stage(
                    step_size=step_size_z,
                    current_position=position_z,
                )
            time.sleep(1)
            position = bcp303.move_to_origin(start_position=start_position)
            time.sleep(1)
            allData[i]["position"].append(position)
            voltage = sm2401.measure_voltage(duration=time_interval / 2, dt=0.01)[
                "voltage"
            ]
            allData[i]["voltage"].append(voltage)
            time.sleep(1)
            for step in range(step_number):
                step_start = time.perf_counter()
                position = bcp303.bcp303_move_stage(
                    step_size=step_size,
                    current_position=position,
                )
                allData[i]["position"].append(position)
                voltage = sm2401.measure_voltage(duration=time_interval / 2, dt=0.01)[
                    "voltage"
                ]
                allData[i]["voltage"].append(voltage)
                # remaining time to wait until the next step
                elapsed = time.perf_counter() - step_start
                remaining = time_interval - elapsed
                if remaining > 0:
                    time.sleep(remaining)
                print(f"process completed: {100 * count / total_steps:.1f}%")
                count += 1
            sm2401_settings = sm2401.getSettings()
            stage_settings["position_z"] = position_z
            settings = {"stage": stage_settings, "sourcemeter": sm2401_settings}
            post_process(
                chip_name=chip_name,
                sample_name=sample_name,
                result=allData[i],
                config=settings,
                repeat=repeat_number,
                position_z=position_z,
                ifshow=False,
                formatted_time=formatted_time,
            )
        # stop the stage and sourcemeter
    except Exception as e:
        print(f"Exception occurred: {e}")
    finally:
        time.sleep(0.5)
        sm2401.close()
        bcp303_z.move_to_origin()
        bcp303_z.channel.StopPolling()
        bcp303.bcp303_stop(ifback=True)
        return allData, settings


if __name__ == "__main__":
    # Define default values for the stage movement
    setting_test = {
        "start_position": 0,
        "step_size": 0,
        "step_number": 1,
        "step_size_z": 1,
        "repeat_number": 1,
        "position_z": 0,
        "time_interval": 4,  # duration = time_interval / 2
    }
    setting = {
        "start_position": 1.5,
        "step_size": 0.005,
        "step_number": 400,
        "step_size_z": 1,
        "repeat_number": 3,
        "position_z": 1,
        "time_interval": 4,
    }
    operation(
        stage_settings=setting_test,
        chip_name="noise_test",
        sample_name="AFM_test",
    )
