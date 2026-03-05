from zhinst.core import ziDAQServer
import sys
import os
import matplotlib.pyplot as plt
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
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
    "duration": 5,  # Duration of the measurement in seconds
    "wait_time": [
        [0.05],
    ],  # Wait time after setting frequency
}
list1 = []
timestamps = []


class LockinScope:
    def __init__(self, basepath="./results", params={}):
        self.params = params
        self.device = "dev1657"
        self.daq = ziDAQServer("127.0.0.1", 8005, 1)
        self.daq.set("/dev1657/scopes/0/enable", 1)
        self.scope = self.daq.scopeModule()
        lockin = LockinController(self.daq, self.device)
        self.samplecount = params.get("samplecount")
        self.demods = params.get("demods")
        self.duration = params.get("duration")
        # self.wait_time = params.get("wait_time")
        # lockin.configure_modulation(
        #     filter_order=8,
        # )
        self.daq.set("/dev1657/scopes/0/time", 15)  # samplerate=6.4k
        # self.daq.setInt(f"/{self.device}/scopes/0/length", 6400 * self.duration)

    def scope_on(self):
        self.daq.set("/dev1657/scopes/0/enable", 1)
        # self.daq.set("/dev1657/scopes/0/time", 10)
        self.scope.subscribe(f"/{self.device}/scopes/0/wave")
        self.scope.execute()
        t0 = time.time()
        while time.time() - t0 < self.duration:
            time.sleep(0.1)

    def scope_off(self):
        self.daq.set("/dev1657/scopes/0/enable", 0)
        self.scope.finish()
        self.scope.unsubscribe("*")

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

    def scope_run(self):
        self.scope_on()

        clockbase = self.daq.getInt(f"/{self.device}/clockbase")
        t_list, v_list = [], []

        t_start = time.time()
        while time.time() - t_start < self.duration:
            res = self.scope.read(True)
            print(res)
            dev = res.get("/dev1657/scopes/0/wave")
            if not dev:
                continue
            for rec_list in dev:
                rec = rec_list[0]
                v = rec["wave"][0]
                dt = rec["dt"]
                t0 = rec["timestamp"] / float(clockbase)
                t = t0 + np.arange(v.size) * dt

                t_list.append(t)
                v_list.append(v)

            time.sleep(0.02)

        self.scope_off()

        if not t_list:
            return {"time": [], "signal": []}

        t_all = np.concatenate(t_list)
        v_all = np.concatenate(v_list)

        # 排序 + 归零
        idx = np.argsort(t_all)
        t_all = t_all[idx] - t_all[idx][0]
        v_all = v_all[idx]

        return {"time": t_all.tolist(), "signal": v_all.tolist()}

    # def scope_run(self):
    #     self.scope_on()
    #     all_records = self.scope.read()[self.device]["scopes"]["0"]["wave"]
    #     self.scope_off()
    #     t_counter = 0
    #     t_all = np.array([])
    #     signal_all = np.array([])
    #     print(len(all_records))
    #     for data in all_records:
    #         rec = data[0]
    #         signal = rec["wave"][0]
    #         dt = rec["dt"]
    #         t = np.arange(signal.size) * dt + t_counter
    #         t_counter += signal.size * dt
    #         print(t_counter)
    #         t_all = np.concatenate([t_all, t])
    #         signal_all = np.concatenate([signal_all, signal])
    #     result = {"time": t_all.tolist(), "signal": signal_all.tolist()}
    #     return result

    # self.scope_on()

    # clockbase = self.daq.getInt(f"/{self.device}/clockbase")
    # t_list = []
    # v_list = []

    # t_start = time.time()
    # while time.time() - t_start < self.duration:
    #     res = self.scope.read(True)  # True: 读完清空缓存，避免重复

    #     dev = res.get(self.device, {})
    #     scopes = dev.get("scopes", {})
    #     s0 = scopes.get("0", {})
    #     waves = s0.get("wave", [])

    #     # waves 结构一般是：[[rec],[rec],...]
    #     for rec_list in waves:
    #         for rec in rec_list:
    #             v = rec["wave"][0]  # 通道0
    #             dt = rec["dt"]
    #             t0 = rec["timestamp"] / float(clockbase)
    #             t = t0 + np.arange(v.size) * dt

    #             t_list.append(t)
    #             v_list.append(v)

    #     time.sleep(0.02)  # 小睡一下，减轻CPU占用（可调）

    # self.scope_off()

    # if not t_list:
    #     return {"time": [], "signal": []}

    # t_all = np.concatenate(t_list)
    # v_all = np.concatenate(v_list)

    # # 按时间排序 + 去重（防止偶尔顺序乱/重复点）
    # idx = np.argsort(t_all)
    # t_all = t_all[idx]
    # v_all = v_all[idx]

    # # 从0开始
    # t_all = t_all - t_all[0]

    # return {"time": t_all.tolist(), "signal": v_all.tolist()}


if __name__ == "__main__":
    foldername = "251120_01"
    # basepath, t = create_new_folder(base_path="./result", suffix=foldername)
    setting_one = setting.copy()
    scope = LockinScope(basepath="", params=setting_one)
    result = scope.scope_run()
    # print(result)
    # print(result)
    plt.figure(figsize=(8, 4))
    plt.plot(result["time"], result["signal"])
    plt.xlabel("Time (s)")
    plt.ylabel("Voltage (V)")
    plt.title("Scope Signal")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # merged = merge_demods_from_files(
    #     timestamps,
    #     list1,
    #     device_id="dev1657",
    #     demod_ids=("1", "2", "3"),
    #     fields=("frequency", "x", "y", "r", "phase"),
    #     parent_folder=basepath,
    #     whole_name=list1,
    # )
    # generate file name
    # data = {"file_name": list1}
    # create_data_json(
    #     result=data, path=basepath, timestamp=f"{foldername}_all_file_names_manual"
    # )
    # print(list1)
