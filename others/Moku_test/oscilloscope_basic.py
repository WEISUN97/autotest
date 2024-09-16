#
# moku example: Basic Oscilloscope
#
# This script demonstrates how to use the Oscilloscope instrument
# to retrieve a single frame of dual-channel voltage data.
#
# (c) 2021 Liquid Instruments Pty. Ltd.
#
from moku.instruments import Oscilloscope

# Connect to your Moku by its ip address using Oscilloscope('[fe80::7269:79ff:feb0:9e0]')
# or by its serial number using Oscilloscope(serial=000607)
# i = Oscilloscope("[fe80::7269:79ff:feb9:4a22]", force_connect=False)
i = Oscilloscope("[fe80::7269:79ff:feb0:9e0]", force_connect=False)

try:
    # Set the span to from -1ms to 1ms i.e. trigger point centred
    i.set_timebase(-1e-3, 1e-3)

    # Get and print a single frame  of data (time series
    # of voltage per channel)
    data = i.get_data()
    print(data["ch1"], data["ch2"], data["time"])

except Exception as e:
    print(f"Exception occurred: {e}")
finally:
    # Close the connection to the Moku device
    # This ensures network resources are released correctly
    i.relinquish_ownership()
    print("Close the connection")
