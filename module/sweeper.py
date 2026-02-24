import time


class SweeperController:
    def __init__(self, daq, device, gridnode="/dev1657/oscs/1/freq"):
        self.device = device
        self.sweeper = daq.sweep()
        self.gridnode = gridnode  # choose oscillator to sweep
        sweeper = daq.sweep()
        sweeper.set("device", device)
        sweeper.set("xmapping", 1)
        sweeper.set("historylength", 100)
        sweeper.set("settling/inaccuracy", 0.00010000)
        sweeper.set("averaging/sample", 1)
        sweeper.set("bandwidth", 1000.00000000)
        sweeper.set("maxbandwidth", 1250000.00000000)
        sweeper.set("omegasuppression", 40.00000000)
        sweeper.set("order", 4)
        sweeper.set(
            "save/directory",
            r"C:\Users\cnmuser\Documents\Zurich Instruments\LabOne\WebServer",
        )
        sweeper.set("averaging/tc", 0.00000000)
        sweeper.set("averaging/time", 0.00000000)
        sweeper.set("bandwidth", 1000.00000000)
        sweeper.set("start", 1000.00000000)
        sweeper.set("stop", 1000000.00000000)
        sweeper.set("omegasuppression", 40.00000000)
        sweeper.set("order", 4)
        sweeper.set("settling/inaccuracy", 0.00010000)

    def configure(
        self,
        start,
        stop,
        samplecount,
        maxbandwidth=10,
        xmapping=0,  # 0: linear, 1: logarithmic
        settling_time=0,
        inaccuracy=0.00001,
        bandwidthcontrol=2,
        bandwidth=10,
        minSamples=10,
        avagering_sample=1,
    ):
        self.sweeper.set("device", self.device)
        self.sweeper.set("gridnode", self.gridnode)
        self.sweeper.set("start", start)
        self.sweeper.set("stop", stop)
        self.sweeper.set("samplecount", samplecount)
        self.sweeper.set("xmapping", xmapping)
        self.sweeper.set("averaging/sample", avagering_sample)

        self.sweeper.set(
            "bandwidthcontrol", bandwidthcontrol
        )  # 0:manual, 1:fixed, 2: auto
        if bandwidthcontrol == 1:
            self.sweeper.set("bandwidth", bandwidth)
            self.sweeper.set("averaging/sample", minSamples)  # mimimum samples

        if bandwidthcontrol == 2:
            self.sweeper.set("maxbandwidth", maxbandwidth)
        self.sweeper.set("settling/time", settling_time)
        self.sweeper.set("settling/inaccuracy", inaccuracy)

        # self.sweeper.set("save/save", 1)
        # self.sweeper.set("save/saveonread", 1)
        # self.sweeper.set("save/directory", save_dir)
        # self.sweeper.set("save/filename", "sweep")
        # self.sweeper.set("save/fileformat", 1)  # 0=matlab,  1 = CSV
        # self.sweeper.set("save/csvseparator", ";")

    def run(self, demods=["0", "1", "2", "3"], timeout=5000000):
        for d in demods:
            self.sweeper.subscribe(f"/{self.device}/demods/{d}/sample")
        self.sweeper.execute()
        start_time = time.time()
        while not self.sweeper.finished():
            time.sleep(0.5)
            progress = self.sweeper.progress()[0]
            print(f"Sweeper progress: {progress * 100:.2f}%")
            if time.time() - start_time > timeout:
                print("Timeout reached before sweep finished.")
                break
        result = self.sweeper.read()
        # print(result)
        self.sweeper.finish()
        self.sweeper.unsubscribe("*")
        print("Sweep finished.")
        return result

    def stop(self):
        self.sweeper.finish()
        self.sweeper.unsubscribe("*")
