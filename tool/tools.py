import csv
import json
from turtle import pd
import matplotlib.pyplot as plt
import os
import numpy as np
from datetime import datetime
import pandas as pd


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


def plot_data_origin(data, index=0, show=False, file_path=""):
    plt.figure()
    if index != None:
        offset = np.mean(data["voltage"][0 : index + 1])
    else:
        offset = data["voltage"][0]
    data["voltage"] = [x - offset for x in data["voltage"]]
    data["voltage"] = [x for x in data["voltage"]]
    plt.plot(data["position"], data["voltage"])
    plt.xlabel("Position (um)")
    plt.ylabel("Voltage (mV)")
    plt.title("Voltage vs Position")
    plt.grid(True)
    if file_path:
        plt.savefig(file_path, dpi=300)
    if show:
        plt.show()
    else:
        plt.close()


import numpy as np


def find_last_zero_before_valid(
    x, y, zero_tol=0.3, valid_thresh=1.0, sustain=2, baseline_n=2
):
    """
    zero_tol : float
        Tolerance for defining a near-zero point, i.e. abs(y) <= zero_tol.
    valid_thresh : float
        Threshold for defining valid data, i.e. y >= valid_thresh.
    sustain : int
        Number of consecutive points required to confirm valid data starts.

    Returns
    -------
    idx : int or None
        Index of the last zero point before valid data starts.
    x0 : float or None
        x value of that point.
    y0 : float or None
        y value of that point.
    """
    x = np.asarray(x)
    y = np.asarray(y)
    baseline = np.mean(y[:baseline_n])
    n = len(y)
    if len(x) != n:
        raise ValueError("x and y must have the same length")

    # Find the first sustained valid region
    start_valid = None
    for i in range(n - sustain + 1):
        if np.all(y[i : i + sustain] >= valid_thresh + baseline):
            start_valid = i
            break

    if start_valid is None:
        return None, None, None

    # Search backward for the last near-zero point before valid region
    for j in range(start_valid - 1, -1, -1):
        if abs(y[j]) <= zero_tol + baseline:
            print(f"Found zero point at index {j}, position={x[j]}, voltage={y[j]}")
            return j, x[j], y[j]

    return None, None, None


def plot_data_sample(
    data, index=0, show=True, file_path="", sensitivity=580, stiffness=8.8 * 1e-6
):
    # sensitivity: mV/um, stiffness: N/um, so force = stiffness * position_sample, voltage: mV
    plt.figure()
    if index != None:
        # offset = np.mean(data["voltage"][0 : index + 1])
        offset = data["voltage"][index]
    else:
        offset = data["voltage"][0]
    data["voltage"] = [x - offset for x in data["voltage"]]
    # x_AFM: displacement of AFM tip
    position_AFM = [x / sensitivity for x in data["voltage"]]
    pos_offset = data["position"][index]
    data["position"] = [x - pos_offset for x in data["position"]]
    # x_sample = x_stage - x_AFM
    data["position_sample"] = [x - y for x, y in zip(data["position"], position_AFM)]
    data["force_sample"] = [x * stiffness * 1e3 for x in position_AFM]  # convert to mN
    plt.plot(data["position_sample"][index:], data["force_sample"][index:])
    plt.xlabel("Displacement (um)")
    plt.ylabel("Force (mN)")
    plt.title("Force vs Displacement")
    plt.grid(True)
    if file_path:
        plt.savefig(file_path, dpi=300)
    if show:
        plt.show()
    else:
        plt.close()


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
    ifshow=False,
    show_signal=False,
    formatted_time="",
):
    os.makedirs(f"./result/{chip_name}", exist_ok=True)
    if repeat > 1:
        prefix = f"./result/{chip_name}/{formatted_time}_{sample_name}"
        os.makedirs(f"{prefix}", exist_ok=True)
        sample_name = f"{sample_name}_z{position_z}"
    else:
        ifshow = True
        prefix = f"./result/{chip_name}"
    file_path = f"{prefix}/{formatted_time}_{sample_name}"
    os.makedirs(file_path, exist_ok=True)
    suffix = f"{formatted_time}_{chip_name}_{sample_name}"
    saveSettings(config, file_path, suffix=suffix)
    path = save_data_to_csv(result, file_path, suffix=suffix)
    avg_data = avarage_voltage(
        result, ifsave_csv=True, save_dir=file_path, suffix=suffix
    )
    avg_data["voltage"] = [x * 1e3 for x in avg_data["voltage"]]  # convert to mV
    index = find_last_zero_before_valid(
        avg_data["position"],
        avg_data["voltage"],
        zero_tol=0.5,
        valid_thresh=1.0,
        sustain=3,
        baseline_n=2,
    )[0]
    data1 = avg_data.copy()
    if ifshow:
        show_signal = False
    plot_data_origin(
        data1,
        index=index,
        show=show_signal,
        file_path=os.path.join(file_path, f"{suffix}_origin_plot.png"),
    )
    plot_data_sample(
        avg_data,
        index=index,
        show=ifshow,
        file_path=os.path.join(file_path, f"{suffix}_sample_plot.png"),
    )


# Save data to a CSV file
def save_temperature_to_csv(file_path, data, titles=["Time", "Value(°C)"]):
    if not data or not data[0]:
        raise ValueError("Data is empty, nothing to save")  # No data to save,
    try:
        # Transpose the data so that each inner list represents a column
        transposed_data = list(zip(*data))

        # Open the file in write mode
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)

            # Write the header if provided
            if titles:
                writer.writerow(titles)

            # Write each row of transposed data
            for row in transposed_data:
                writer.writerow(row)

        print(f"Data successfully saved to {file_path}")

    except Exception as e:
        print(f"An error occurred while saving data: {e}")
