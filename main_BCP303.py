from BCP303.BCP303 import BPC303
from Sourcemeter.sourcemeter import Sourcemeter2401
from tool.tools import save_data_to_csv, saveSettings, avarage_voltage, plot_data
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


def operation(stage_setting):
    repeat_number = stage_setting["repeat_number"]
    step_size = stage_setting["step_size"]
    step_number = stage_setting["step_number"]
    time_interval = stage_setting["time_interval"]
    result = {"position": [], "voltage": []}
    try:
        # initialize the data logger
        bcp301 = BPC303()
        sm2401 = Sourcemeter2401(speed_nplc=0.1)
        bcp301.move_to_origin()
        position = 0
        for i in range(repeat_number):
            for step in range(step_number):
                step_start = time.perf_counter()
                position = bcp301.bcp303_move_stage(
                    step_size=step_size,
                    current_position=position,
                )
                result["position"].append(position)
                voltage = sm2401.measure_voltage(duration=time_interval / 2, dt=0.01)[
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
        # stop the stage and sourcemeter
    except Exception as e:
        print(f"Exception occurred: {e}")
    finally:
        time.sleep(0.5)
        sm2401.close()
        bcp301.bcp301_stop(ifback=True)
        return result, settings


if __name__ == "__main__":
    # Define default values for the stage movement
    setting = {
        "repeat_number": 1,
        "step_size": 0.1,
        "step_number": 5,
        "time_interval": 2,
    }
    result, config = operation(setting)
    print(result)
    print(config)
    # save the data
    chip_name = "chip1"
    os.makedirs(f"./result/{chip_name}", exist_ok=True)
    sample_name = "beam_test"
    formatted_time = datetime.now().strftime("%Y%m%d%H%M")
    file_path = f"./result/{chip_name}/{formatted_time}_{sample_name}"
    os.makedirs(file_path, exist_ok=True)
    suffix = f"{formatted_time}_{chip_name}_{sample_name}"
    saveSettings(config, file_path, suffix=suffix)
    save_data_to_csv(result, file_path, suffix=suffix)
    avg_data = avarage_voltage(
        result, ifsave_csv=True, save_dir=file_path, suffix=suffix
    )
    plot_data(
        avg_data, show=True, file_path=os.path.join(file_path, f"{suffix}_plot.png")
    )
