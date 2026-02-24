import zhinst.core


class ScopeController:
    def __init__(self, daq, device, save_dir=None, ext_scaling=1.0, avg_weight=10):
        self.scope = daq.scopeModule()
        self.device = device
        self.save_dir = save_dir
        self.ext_scaling = ext_scaling
        self.avg_weight = avg_weight

    def configure(self):
        self.scope.set("lastreplace", 1)
        self.scope.subscribe(f"/{self.device}/scopes/0/wave")
        self.scope.set("averager/weight", self.avg_weight)
        self.scope.set("averager/restart", 0)
        self.scope.set("externalscaling", self.ext_scaling)
        self.scope.set("fft/power", 0)
        self.scope.set("mode", 1)
        self.scope.set("fft/spectraldensity", 0)
        self.scope.set("fft/window", 1)
        if self.save_dir:
            self.scope.set("save/directory", self.save_dir)

    def stop(self):
        self.scope.unsubscribe("*")
