from zhinst.core import ziDAQServer
import numpy as np
import time

DEVICE = "dev1657"
PATH = f"/{DEVICE}/sigins/0/sample"

daq = ziDAQServer("127.0.0.1", 8005, 1)
clockbase = daq.getInt(f"/{DEVICE}/clockbase")
print(daq.getInt("/dev1657/scopes/0/time"))
print(daq.getInt("/dev1657/scopes/0/length"))
