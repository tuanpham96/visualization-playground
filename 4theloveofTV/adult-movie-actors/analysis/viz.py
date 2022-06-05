import numpy as np
import matplotlib.pyplot as plt 

tau = 7.8
rho = 1/tau
N = 50000
start_year = 1970
end_year = 2022
T = end_year-start_year

events = np.random.rand(N,T) < rho

def find_on_off(event):
    loc = np.where(event)[0]
    if len(loc) == 0:
        return None
    elif len(loc) == 1:
        return loc[0], loc[0]
    else:
        return loc[0], loc[1] 

loc_events = list(map(find_on_off, events))
loc_events = np.array([L for L in loc_events if L])
loc_events += start_year

isi_events = loc_events[:,1] - loc_events[:,0]

plt.hist(isi_events, bins=50, log=True)
plt.show()

plt.scatter(loc_events[:,0], isi_events, alpha=0.02)
plt.show()
