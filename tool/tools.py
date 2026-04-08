import csv
import json
import matplotlib.pyplot as plt
import os
import numpy as np
from datetime import datetime


def save_data_to_csv(data: dict, save_dir: str, suffix=""):
    """
    data:
      {
        "position": [p0, p1, ...],
        "voltage": [[v00, v01, ...], [v10, v11, ...], ...]
      }
    """
    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, f"{suffix}_data.csv")

    positions = data["position"]
    volt_lists = data["voltage"]

    if len(positions) != len(volt_lists):
        raise ValueError(
            f"Length mismatch: position={len(positions)} vs voltage={len(volt_lists)}"
        )

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["pos_index", "position", "sample_index", "voltage"])

        for pos_idx, (pos, vlist) in enumerate(zip(positions, volt_lists)):
            for sample_idx, v in enumerate(vlist):
                writer.writerow([pos_idx, pos, sample_idx, v])

    return path


def avarage_voltage(data: dict, ifsave_csv=True, save_dir="", suffix=""):
    positions = data["position"]
    volt_lists = data["voltage"]

    if len(positions) != len(volt_lists):
        raise ValueError(
            f"Length mismatch: position={len(positions)} vs voltage={len(volt_lists)}"
        )

    avg_voltages = []
    voltage_stds = []
    n_samples = []
    for vlist in volt_lists:
        avg_v = np.mean(vlist)
        avg_voltages.append(avg_v)
        voltage_std = np.std(vlist)
        voltage_stds.append(voltage_std)
        n_samples.append(len(vlist))

    if ifsave_csv:
        os.makedirs(save_dir, exist_ok=True)
        path = os.path.join(save_dir, f"{suffix}_signal_mean.csv")

        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["position", "voltage_mean", "voltage_std", "n_samples"])

            for pos, v_mean, v_std, n in zip(
                positions, avg_voltages, voltage_stds, n_samples
            ):
                writer.writerow([pos, float(v_mean), float(v_std), n])

    return {
        "position": positions,
        "voltage": avg_voltages,
        "voltage_std": voltage_stds,
        "n_samples": n_samples,
    }


def plot_data(data, show=True, file_path=""):
    offset = data["voltage"][0]
    data["voltage"] = [x - offset for x in data["voltage"]]
    data["voltage"] = [x * 1e3 for x in data["voltage"]]
    plt.plot(data["position"], data["voltage"])
    plt.xlabel("Position (um)")
    plt.ylabel("Voltage (mV)")
    plt.title("Voltage vs Position")
    plt.grid(True)
    if file_path:
        plt.savefig(file_path, dpi=300)
    if show:
        plt.show()


def saveSettings(config, save_dir, suffix=""):
    file_path = os.path.join(save_dir, f"{suffix}_config.json")
    with open(file_path, "w") as f:
        json.dump(config, f, indent=4)
    print("Config saved to:", file_path)


def post_process(
    chip_name="",
    sample_name="",
    result=None,
    config=None,
    position_z=None,
    repeat=None,
    ifshow=True,
):

    os.makedirs(f"./result/{chip_name}", exist_ok=True)
    if repeat:
        prefix = f"./result/{chip_name}/{sample_name}"
        os.makedirs(f"{prefix}", exist_ok=True)
        sample_name = f"{sample_name}_z{position_z}"
    else:
        prefix = f"./result/{chip_name}"
    formatted_time = datetime.now().strftime("%Y%m%d%H%M")
    file_path = f"{prefix}/{formatted_time}_{sample_name}"
    os.makedirs(file_path, exist_ok=True)
    suffix = f"{formatted_time}_{chip_name}_{sample_name}"
    saveSettings(config, file_path, suffix=suffix)
    save_data_to_csv(result, file_path, suffix=suffix)
    avg_data = avarage_voltage(
        result, ifsave_csv=True, save_dir=file_path, suffix=suffix
    )
    plot_data(
        avg_data, show=ifshow, file_path=os.path.join(file_path, f"{suffix}_plot.png")
    )
