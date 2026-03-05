import numpy as np

t1 = np.arange(5) * 10 + 0.5
t2 = np.arange(5) * 10 + 0.7
t_all = np.concatenate([t1, t2])
print(t_all)
