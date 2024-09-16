import time

# Start the timer
start_time = time.perf_counter()

# Code to measure
time.sleep(1)  # Example code that takes 1 second

# Stop the timer
end_time = time.perf_counter()

# Calculate elapsed time
elapsed_time = end_time - start_time

print(f"Elapsed time: {elapsed_time} seconds")
