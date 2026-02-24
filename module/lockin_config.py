import time


class LockinController:
    def __init__(self, daq, device):
        self.daq = daq
        self.device = device

    def configure_modulation(
        self,
        carrier=1000000,
        sideband_freqs=68000,
        filter_order=8,
        output_amplitude1=0.2,
        output_amplitude2=0.5,
        output_range1=1,
        output_range2=1,
    ):
        # carrier frequency
        self.daq.setDouble("/dev1657/oscs/0/freq", carrier)
        # sideband frequencies
        # self.daq.setDouble("/dev1657/oscs/1/freq", sideband_freqs)

        # low pass filter order
        self.daq.setInt("/dev1657/mods/0/carrier/order", filter_order)
        self.daq.setInt("/dev1657/mods/0/sidebands/0/order", filter_order)
        self.daq.setInt("/dev1657/mods/0/sidebands/1/order", filter_order)

        self.daq.setDouble("/dev1657/demods/0/rate", 1000.00000000)
        # Set output ranges
        range_list = [0.01, 0.1, 1, 10]
        if output_amplitude1 > 10:
            output_amplitude1 = 10
            print("Output amplitude1 exceeds 10V, setting to 10V")
        if output_amplitude2 > 10:
            output_amplitude2 = 10
            print("Output amplitude2 exceeds 10V, setting to 10V")
        for output_range1 in range_list:
            if output_range1 >= output_amplitude1:
                break
        for output_range2 in range_list:
            if output_range2 >= output_amplitude2:
                break
        # drive output
        print(f"Setting output1 range to {output_range1} V")
        print(f"Setting output2 range to {output_range2} V")
        self.daq.setDouble("/dev1657/sigouts/0/range", output_range1)
        time.sleep(1)
        self.daq.setDouble(
            "/dev1657/sigouts/0/amplitudes/6", output_amplitude1 / output_range1
        )
        # print(1 / output_range1 * output_amplitude1)
        # # modulation output
        self.daq.setDouble("/dev1657/sigouts/1/range", output_range2)
        time.sleep(1)
        self.daq.setDouble(
            "/dev1657/sigouts/1/amplitudes/7", output_amplitude2 / output_range2
        )
        time.sleep(1)
