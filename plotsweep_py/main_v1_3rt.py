"""
1 - 1.00
2 - 1.02
3 - 1.04
4 - 1.08
5 - 1.12
6 - 1.16
7 - 1.20
8 - 1.24
9 - 1.28
a - 1.32
b - 1.36
c - 1.40
d - 1.44
e - 1.48
f - 1.52
"""

from hrfs_read_v6rt import SweepCollection, MHZ, kHz
from sweep import Sweep
import numpy as np
import matplotlib.pyplot as plt


if __name__ == "__main__":
    print('start parsing csv')
    rc = SweepCollection(range=(1000,1150), width_bin=250000)
    # rc = SweepCollection(file_csv="6ch.csv")
    print(rc)
    print('parsing ok')
    ts_list, img = rc.get_hotmap()
    
    # TODO Yaxis is time? from up is netime to down is oldtime 
    print(ts_list[-1::-20])
    print([Sweep.get_str_dt(item) for item in ts_list][-1::-20])
    

    X_freq = rc.freq_range()
    Y_td = np.arange(0, -len(ts_list), -1)
    Y_power = np.mean(img, axis=0)
    Y_maxpower = np.max(img, axis=0)
    max_power_index = np.argmax(Y_power)
    max_power = np.max(Y_power)
    freq_max = X_freq[max_power_index]
    Y_avgpower = np.zeros(len(X_freq))
    Y_avgpower[...] = np.mean(Y_power)
    plt.figure()
    # upper graph is avarage power
    plt.subplot(2, 1, 1)
    plt.ylabel('power(dB)')
    plt.title('Spectr frequency')
    plt.text(freq_max, max_power, str(f"{int(freq_max / MHZ)} MHz \n ({round(max_power)} dB)"))
    plt.plot(X_freq, Y_power)
    plt.plot(X_freq, Y_avgpower)
    plt.plot(X_freq, Y_maxpower)
    plt.xlim(rc.freq_min, rc.freq_max)
    plt.grid()
    # lower graph is sonogram
    plt.subplot(2, 1, 2)
    plt.ylabel('td')
    plt.title('Hotmap')
    plt.xlabel('frequency')
    plt.grid()
    plt.pcolormesh(X_freq, Y_td, img[-1::-1,:])
    plt.yticks(Y_td[0::20], [Sweep.get_str_dt(item) for item in ts_list][-1::-20])
    plt.show()
    
    