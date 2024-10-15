import numpy as np
import matplotlib.pyplot as plt

# Load your time and voltage data (assuming you have these arrays)
# For demonstration, I'll generate some sample data.
# Replace these with your actual data
time = np.linspace(
    0, 60, 6000
)  # Simulated time data (60 seconds, 100 Hz sampling rate)
voltage = np.sin(0.1 * np.pi * time) + np.random.normal(
    0, 0.001, time.shape
)  # Simulated noisy voltage data

print(voltage)


# Moving average function
def moving_average(data, window_size):
    return np.convolve(data, np.ones(window_size) / window_size, mode="valid")


# Define the window size for the moving average (adjust based on how much smoothing you need)
window_size = 100  # E.g., smooth over 100 data points

# Apply the moving average to the voltage data
voltage_smoothed = moving_average(voltage, window_size)

# Adjust time data to match the length of the smoothed voltage data
time_smoothed = time[: len(voltage_smoothed)]

# Plot the original and smoothed signals
plt.figure(figsize=(10, 6))
plt.plot(time, voltage, label="Original Signal", alpha=0.5)
plt.plot(
    time_smoothed,
    voltage_smoothed,
    label="Smoothed Signal (Moving Average)",
    color="red",
)
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.title("Original and Smoothed Voltage/Time Data")
plt.legend()
plt.grid(True)
plt.show()
