from zhinst.core import ziDAQServer
from module.lockin_config import LockinController
import numpy as np
from module.setting_read import generate_setting, create_allsettings_json
from module.tools import (
    save_sweep_to_csv,
    create_new_folder,
    plot_sweep,
    create_data_json,
)
from module.json_merge import merge_demods_from_files
import time


setting = {
    # Amplitude for driven output
    "bandwidth": 1,  # Bandwidth for sweeper
    "samplecount": 1000,  # Number of result for sweeper
    "demods": ["1", "2", "3"],  # Demodulator channels to use
    "duration": 10,  # Duration of the measurement in seconds
    "wait_time": [
        [0.05],
    ],  # Wait time after setting frequency
}
list1 = []
timestamps = []


class LockinDataLogger:
    def __init__(self, basepath="./results", params={}):
        self.params = params
        self.device = "dev1657"
        self.daq = ziDAQServer("127.0.0.1", 8005, 1)
        lockin = LockinController(self.daq, self.device)
        self.samplecount = params.get("samplecount")
        self.demods = params.get("demods")
        # self.duration = params.get("duration")
        self.wait_time = params.get("wait_time")
        lockin.configure_modulation(
            filter_order=8,
        )
        self.result = {
            self.device: {
                "demods": {
                    d: {"sample": [[{"frequency": [], "r": [], "phase": []}]]}
                    for d in self.demods
                }
            }
        }

    def record_data(self):
        for count in range(self.samplecount):
            demod_data = self.result[self.device]["demods"][d]["sample"][0][0]
            for d in self.demods:
                sample = self.daq.getSample(f"/{self.device}/demods/{d}/sample")
                X = sample["x"][0]
                Y = sample["y"][0]
                R = np.abs(X + 1j * Y)
                Theta = np.arctan2(Y, X)
                demod_data["r"].append(R)
                demod_data["phase"].append(Theta)
            time.sleep(self.wait_time)

    def save_data(self, basepath="./result"):
        suffix = ""
        path, timestamp = create_new_folder(base_path=basepath, suffix=suffix)
        create_data_json(
            result=self.result, path=path, timestamp="alldatas_" + timestamp
        )
        list1.append(f"{timestamp}{suffix}")
        timestamps.append(timestamp)
        create_allsettings_json(path=path, timestamp=timestamp)
        generate_setting(setting=self.params, filename=timestamp, folder=path)
        df = save_sweep_to_csv(
            self.result,
            self.device,
            demod=self.demods,
            suffix=suffix,
            path=path,
            timestamp=timestamp,
        )
        plot_sweep(df, path=path, timestamp=timestamp, demod=["1"])
        return self.daq, self.result

    def datalogger_run(self):
        self.record_data()
        self.save_data()


if __name__ == "__main__":
    foldername = "251120_01"
    basepath, t = create_new_folder(base_path="./result", suffix=foldername)
    setting_one = setting.copy()
    lockin = LockinDataLogger(basepath=basepath, params=setting_one)
    lockin.datalogger_run()

    merged = merge_demods_from_files(
        timestamps,
        list1,
        device_id="dev1657",
        demod_ids=("1", "2", "3"),
        fields=("frequency", "x", "y", "r", "phase"),
        parent_folder=basepath,
        whole_name=list1,
    )
    # generate file name
    data = {"file_name": list1}
    create_data_json(
        result=data, path=basepath, timestamp=f"{foldername}_all_file_names_manual"
    )
    print(list1)
