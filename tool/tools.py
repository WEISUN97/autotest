import csv
import matplotlib.pyplot as plt
import os
import numpy as np


def is_float(value):
    try:
        float(value)  # Try to convert to float
        return True  # Conversion successful, it's a float
    except ValueError:
        return False  # Conversion failed, it's not a float


# plot as time
def plot_data(
    moku_file_path,
    moku_channels,
    temperatures,
    stagePositions,
    formatted_time,
    step_size,
):
    moku_x_data = []  # List of  x-axis data (order: moku, temperature, stage)
    data_time = []  # List of  x-axis data (order: moku, temperature, stage)
    moku_y_data = [[] for _ in range(len(moku_channels))]  # List of  y-axis data
    # Read the moku CSV file
    with open(moku_file_path, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            try:
                if is_float(row[0]) == True:
                    data_time.append(float(row[0]))
                    moku_x_data.append(
                        float(row[0]) * step_size
                    )  # Convert x data to float
                    for i, col in enumerate(moku_channels):
                        moku_y_data[i].append(
                            float(row[col])
                        )  # Convert y data to float
            except ValueError as e:
                print(f"Skipping row due to conversion error: {row} - {e}")
                continue
    # Create the figure and the first y-axis
    nrows = 2 if stagePositions else 1
    fig, (ax1, ax3) = plt.subplots(
        nrows=nrows, ncols=1, figsize=(10, 8), gridspec_kw={"hspace": 0.5}
    )
    # upper plot
    # Plot moku data on the left y-axis
    for i, y in enumerate(moku_y_data):
        ax1.plot(data_time, y, label=f"Channel {moku_channels[i]}")

    # Set labels for the left y-axis
    ax1.set_xlabel("Time(s)")
    ax1.set_ylabel("Voltage (V)")
    ax1.grid(True)

    # Create the second y-axis for temperature
    ax2 = ax1.twinx()
    ax2.set_ylabel("Temperature (°C)")
    ax2.plot(temperatures[0], temperatures[1], label="Temperature", color="r")

    # Set the title
    ax1.set_title("Signal and Temperature")

    # Combine legends from both axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    # lower plot
    # Set labels for the left y-axis
    if stagePositions:
        ax3.set_xlabel("Position(µm)")
        ax3.set_ylabel("Voltage (V)")
        ax3.grid(True)
        for i, y in enumerate(moku_y_data):
            ax3.plot(moku_x_data, y, label=f"Channel {moku_channels[i]}")
        # Create the second y-axis for stage position
        ax4 = ax3.twinx()
        ax4.set_ylabel(f"Position (µm)")
        for m in range(len(stagePositions[0])):
            stagePositions[0][m] = stagePositions[0][m] * step_size
        ax4.plot(stagePositions[0], stagePositions[1], label="Positions", color="r")

        # Set the title
        ax3.set_title("Signal vs Stage Position")

        # Combine legends from both axes
        lines3, labels3 = ax3.get_legend_handles_labels()
        lines4, labels4 = ax4.get_legend_handles_labels()
        ax3.legend(lines3 + lines4, labels3 + labels4, loc="upper left")

    # Save the plot as a PNG file
    plt.savefig(
        f"./result/{formatted_time}/{formatted_time}_plot.png", dpi=300
    )  # Higher DPI for better quality
    # Show the plot
    plt.show()


# plot forward and backward (repeat time should be 1)
def plot_data_stage(
    moku_file_path,
    moku_channels,
    stagePositions,
    formatted_time,
    step_size,
    MDT693_voltage=0,
    display_plt=True,
):
    moku_x_data = []  # List of  x-axis data (order: moku, temperature, stage)
    moku_y_data = [[] for _ in range(len(moku_channels))]  # List of  y-axis data
    # Read the moku CSV file
    with open(moku_file_path, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            try:
                if is_float(row[0]) == True:
                    a = float(row[0]) * step_size
                    moku_x_data.append(a)  # Convert x data to float
                    for i, col in enumerate(moku_channels):
                        moku_y_data[i].append(
                            float(row[col])
                        )  # Convert y data to float
            except ValueError as e:
                print(f"Skipping row due to conversion error: {row} - {e}")
                continue
    # print(moku_x_data)
    # Create the figure and the first y-axis
    fig, ax1 = plt.subplots(figsize=(10, 8))
    # upper plot
    # Plot moku data on the left y-axis
    for i, y in enumerate(moku_y_data):
        ax1.plot(moku_x_data, y, label=f"Channel {moku_channels[i]}")

    # Set labels for the left y-axis
    ax1.set_xlabel("Position(µm)")
    ax1.set_ylabel("Voltage (V)")
    ax1.grid(True)

    # Create the second y-axis for temperature
    ax2 = ax1.twinx()
    ax2.set_ylabel("Position (µm)")
    for m in range(len(stagePositions[0])):
        stagePositions[0][m] = stagePositions[0][m] * step_size
    ax2.plot(stagePositions[0], stagePositions[1], label="Positions", color="r")

    # Set the title
    ax1.set_title("Signal vs Positions")

    # Combine legends from both axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    # Save the plot as a PNG file
    plt.savefig(
        f"./result/{formatted_time}_{MDT693_voltage}V/{formatted_time}_plot.png",
        dpi=300,
    )  # Higher DPI for better quality
    # Show the plot
    if display_plt:
        plt.show()
        return ax1, moku_x_data, moku_y_data[0]


# plot mutiple data


# Save data to a CSV file
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


def plot_average(ax1, moku_x_data, moku_y_data, window_size):
    # Load your time and voltage data (assuming you have these arrays)
    # For demonstration, I'll generate some sample data.
    # Replace these with your actual data
    time = moku_x_data
    voltage = moku_y_data

    # Moving average function
    def moving_average(data, window_size):
        return np.convolve(data, np.ones(window_size) / window_size, mode="valid")

    # Define the window size for the moving average (adjust based on how much smoothing you need)
    window_size = window_size  # E.g., smooth over 100 data points

    # Apply the moving average to the voltage data
    voltage_smoothed = moving_average(voltage, window_size)

    # Adjust time data to match the length of the smoothed voltage data
    time_smoothed = time[: len(voltage_smoothed)]

    # Plot the original and smoothed signals
    ax1.plot(time_smoothed, voltage_smoothed, label="Channel 1 Average", color="g")
    ax1.legend()
    plt.show()


# Example usage (if this script is run directly, otherwise, import and use in another script)
if __name__ == "__main__":
    ax1, time, voltage = plot_data_stage(
        "./result/2024_10_28_14_25/MokuDataLoggerData_20000101_000257.csv",
        [1, 2],
        [[1, 2, 3], [1, 2, 3]],
        formatted_time="2024_10_28_14_25",
        step_size=0.05,
    )
    # plot_average(
    #     ax1,
    #     time,
    #     voltage,
    #     10000,
    # )
