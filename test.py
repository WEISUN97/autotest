import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


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
    data["force_sample"] = [
        x * stiffness * 1e3 for x in data["position_sample"]
    ]  # convert to mN
    print(f"position_sample: {data['position_sample'][index:index+5]}")
    print(f"force_sample: {data['force_sample'][index:index+5]}")
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


# ===== Read data from CSV =====
csv_file = "/Users/bubble/Desktop/Project/Buckling/autotest/result/V1_R_W_2_Right/202604291741_test_1_left/202604291741_test_1_left_z-0.00205999938962981/202604291741_V1_R_W_2_Right_test_1_left_z-0.00205999938962981_signal_mean.csv"  # replace with your file name
df = pd.read_csv(csv_file)

print("CSV headers:", df.columns.tolist())

x = df["position"].to_numpy()
y = df["voltage_mean"].to_numpy()
# print(y*1000)
# ===== Run detection =====
idx, x0, y0 = find_last_zero_before_valid(
    x, y * 1000, zero_tol=0.5, valid_thresh=1.0, sustain=2, baseline_n=2
)

print("Result:", idx, x0, y0)

# ===== Plot data sample =====
data = {
    "position": df["position"].to_numpy(),
    "voltage": df["voltage_mean"].to_numpy(),
}
plot_data_sample(data, index=idx, show=True, file_path="")
