from datetime import datetime
import pyvisa
import time
import matplotlib.pyplot as plt
import csv
import numpy as np

VISA_RESOURCE = "GPIB0::24::INSTR"
TIMEOUT_MS = 5000


class Sourcemeter2401:
    def __init__(self, resource=VISA_RESOURCE, speed_nplc=0.1, v_range=20, v_prot=20):
        rm = pyvisa.ResourceManager()
        self.speed_nplc = speed_nplc
        self.inst = rm.open_resource(resource)

        self.inst.timeout = TIMEOUT_MS
        self.inst.write_termination = "\n"
        self.inst.read_termination = "\n"
        self.inst.send_end = True
        self.inst.query_delay = 0.05

        print("IDN:", self.inst.query("*IDN?").strip())
        self.settings = {
            "init": [
                ":ROUT:TERM FRONT",
                "*RST",
                ":SOUR:FUNC CURR",
                ":SOUR:CURR:MODE FIXED",
                ":SOUR:CURR:RANG MIN",
                ":SOUR:CURR:LEV 0",
                ':SENS:FUNC "VOLT"',
                f":SENS:VOLT:RANG {v_range}",
                f":SENS:VOLT:PROT {v_prot}",
                ":FORM:ELEM VOLT",
                f":SENS:VOLT:NPLC {speed_nplc}",
                ":OUTP ON",
            ],
            "measure": [],
        }
        self.inst.write(":ROUT:TERM FRONT")

        self.inst.write("*RST")
        self.inst.write(":SOUR:FUNC CURR")
        self.inst.write(":SOUR:CURR:MODE FIXED")
        self.inst.write(":SOUR:CURR:RANG MIN")
        self.inst.write(":SOUR:CURR:LEV 0")

        self.inst.write(':SENS:FUNC "VOLT"')
        self.inst.write(":SENS:VOLT:RANG 20")
        self.inst.write(":SENS:VOLT:PROT 20")
        self.inst.write(":FORM:ELEM VOLT")
        # Measurement speed: 0.1 NPLC (power line cycles)
        self.inst.write(f":SENS:VOLT:NPLC {speed_nplc}")
        self.inst.write(":OUTP ON")

        # measurement settings

    def measure_voltage(self, duration=2, dt=0.05):
        results = {"time": [], "voltage": []}

        t0 = time.perf_counter()
        while True:
            v = float(self.inst.query(":MEAS:VOLT?"))
            t = time.perf_counter() - t0
            results["time"].append(t)
            results["voltage"].append(v)
            if t >= duration:
                break
            time.sleep(dt)
        # Measure only once
        # v = float(self.inst.query(":MEAS:VOLT?"))
        # t = time.perf_counter() - t0
        # results["time"].append(t)
        # results["voltage"].append(v)
        self.settings["measure"].append({"duration": duration, "dt": dt})
        return results

    def close(self):
        try:
            self.inst.write(":OUTP OFF")
        finally:
            self.inst.close()
            speed_nplc = {"speed_nplc": self.speed_nplc}
            return speed_nplc

    def getSettings(self):
        return self.settings

    def save_data_csv(self, data, file_path):

        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["time", "voltage"])
            for t, v in zip(data["time"], data["voltage"]):
                writer.writerow([t, v])
        print("Data saved to:", file_path)


if __name__ == "__main__":
    durastion_list = [1, 2, 5, 10, 60, 300]
    try:
        mean_list = {}
        for i in range(len(durastion_list)):
            duration = durastion_list[i]
            mean_list[f"duration_{duration}s"] = []
            for j in range(10):
                speed_nplc = 0.1
                dt = 0
                formatted_time = datetime.now().strftime("%Y%m%d%H%M")
                sm = Sourcemeter2401(speed_nplc=speed_nplc)
                data = sm.measure_voltage(duration=duration, dt=dt)
                volt_lists = data["voltage"]
                mean_voltage = np.mean(volt_lists)
                print(len(data["voltage"]))
                print("Mean Voltage:", mean_voltage)
                # sm.save_data_csv(
                #     data,
                #     f"./Sourcemeter/sourcemeter_data/sm_data_{speed_nplc}_{duration}s_{dt}s_{formatted_time}_mean{mean_voltage:.8f}.csv",
                # )
                mean_list[f"duration_{duration}s"].append(mean_voltage)
        print(mean_list)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        sm.close()

    try:
        duration = 3600
        speed_nplc = 0.1
        dt = 0
        formatted_time = datetime.now().strftime("%Y%m%d%H%M")
        sm = Sourcemeter2401(speed_nplc=speed_nplc)
        data = sm.measure_voltage(duration=duration, dt=dt)
        print(len(data["voltage"]))
        sm.save_data_csv(
            data,
            f"./Sourcemeter/sourcemeter_data/sm_data_{speed_nplc}_{duration}s_{dt}s_{formatted_time}_mean{mean_voltage:.8f}.csv",
        )
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        sm.close()

    # plt.plot(data["time"], data["voltage"])
    # plt.xlabel("Time (s)")
    # plt.ylabel("Voltage (V)")
    # plt.title("Voltage vs Time (Keithley 2401)")
    # plt.grid(True)
    # plt.show()
