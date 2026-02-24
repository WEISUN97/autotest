import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
import json
from module.setting_read import purify
import csv


def create_new_folder(base_path: str = "./results", suffix: str = "") -> str:
    timestamp = datetime.now().strftime("%y%m%d%H%M")
    if base_path == "./results":
        folder_name = suffix
    else:
        folder_name = f"{timestamp}{suffix}"
    new_folder_path = os.path.join(base_path, folder_name)

    os.makedirs(new_folder_path, exist_ok=False)
    return new_folder_path, timestamp


def save_sweep_to_csv(result, device, demod=["1"], suffix="", path="", timestamp=""):
    combined_df = None
    try:
        for d in demod:
            sample_data = result[device]["demods"][d]["sample"][0][0]
            freq = sample_data["frequency"]
            amplitude = sample_data["r"]
            phase = sample_data["phase"]

            df = pd.DataFrame(
                {
                    "Frequency_Hz": freq,
                    f"Amplitude_d{d}": amplitude,
                    f"Phase_rad_d{d}": phase,
                }
            )

            if combined_df is None:
                combined_df = df
            else:
                # Merge on Frequency
                combined_df = pd.merge(combined_df, df, on="Frequency_Hz")

            print(f"Saved demod {d} data.")

        # If plotting is enabled, plot the sweep data
        #     save_path_plot = f"./results/figure/sweepplot_{timestamp}{suffix}.png"
        #     plot_sweep(combined_df, save_path=save_path_plot)
    except KeyError as e:
        print(f"Demodulator {demod} not found in result. Error: {e}")

    if combined_df is not None:
        file_name = f"sweep_{timestamp}{suffix}.csv"
        save_path = f"{path}/{file_name}"
        combined_df.to_csv(save_path, index=False)
        print(f"All data saved to {save_path}")
        return combined_df
    else:
        print("No data saved.")
        return None


def plot_sweep(df, demod=["1", "3"], path="", timestamp=""):
    title = "Sweep Result"
    file_name = f"sweep_{timestamp}.png"
    save_path = f"{path}/{file_name}"
    if not path:
        timestamp = datetime.now().strftime("%y%m%d%H%M")
        file_name = f"sweep_{timestamp}.png"
        save_path = f"./results/{file_name}"
    amp_cols = [
        col for col in df.columns if "Amplitude" in col and any(d in col for d in demod)
    ]
    # print(f"Plotting columns: {amp_cols}")
    # print(df)

    plt.figure(figsize=(10, 6))
    print(amp_cols)
    for col in amp_cols:
        print(col)
        plt.plot(df["Frequency_Hz"], df[col], label=col)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude (V)")
    plt.title(title)
    legend_labels = [f"Demod {int(d)+1}" for d in demod]
    plt.legend(legend_labels)
    plt.grid(True)
    plt.tight_layout()

    if path:
        plt.savefig(save_path, dpi=300)
        print(f"Plot saved to: {save_path}")
    else:
        plt.show()


def plot_from_csv(
    csv_paths, column_indices=None, save_path="", show_plot=True, title=""
):
    plt.figure(figsize=(10, 6))

    for csv_path in csv_paths:
        if not os.path.exists(csv_path):
            print(f"File not found: {csv_path}")
            continue

        df = pd.read_csv(csv_path)

        if "Frequency_Hz" not in df.columns:
            print(f"Frequency_Hz not found in: {csv_path}")
            continue

        columns = df.columns.tolist()
        filename = os.path.splitext(os.path.basename(csv_path))[0]

        if column_indices is None:
            plot_columns = [col for col in columns if col != "Frequency_Hz"]
        else:
            plot_columns = []
            for idx in column_indices:
                if idx < 0 or idx >= len(columns):
                    print(f" Invalid index {idx} in: {csv_path}")
                    continue
                if columns[idx] != "Frequency_Hz":
                    plot_columns.append(columns[idx])

        for col in plot_columns:
            label = f"{filename}_{col}"
            plt.plot(df["Frequency_Hz"], df[col], label=label)

    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Value")
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300)
        print(f"Saved overlay plot: {save_path}")
    if show_plot:
        plt.show()


def create_data_json(result={}, path="", timestamp=""):
    pure_json_path = os.path.join(path, f"{timestamp}.json")
    with open(pure_json_path, "w", encoding="utf-8") as f:
        json.dump(purify(result), f, indent=2, ensure_ascii=False)
    return 0


def save_data_to_csv(file_path, data, titles=["Time", "Value(°C)"]):
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


def voltage_name_generator(voltages: list[float]) -> list[str]:
    names = []
    for v in voltages:
        if v >= 1:
            names.append(f"{v:.0f}V")
        elif v >= 1e-3:
            names.append(f"{v*1e3:.0f}mV")
        else:
            names.append(f"{v*1e6:.0f}uV")
    return names
