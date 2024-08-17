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

from hrfs_read_v4 import RecordCollection, MHZ, kHz
from sweep import Sweep
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    print('start parsing csv')
    rc = RecordCollection('7ch.csv')
    print('parsing ok')
    count = 0
    count_sweep = len(rc.records_on_sweep)
    ts_list = []
    for index_sweep in range(count_sweep):
        sweep = Sweep(*rc.get_power_spectr(index_sweep))
        if count == 0:
            img = np.array(sweep.spectr)
        else:
            img = np.vstack((img, sweep.spectr))
        ts_list.append(sweep.timestamp)
        count += 1
    
    # TODO Yaxis is time? from up is netime to down is oldtime 
    print(ts_list[0::10])
    print([Sweep.get_str_dt(item) for item in ts_list][-1::-10])
    

    X_freq = sweep.freq_range()
    Y_td = np.arange(len(ts_list))
    Y_power = np.mean(img, axis=0)
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
    plt.xlim(sweep.f_min, sweep.f_max)
    plt.grid()
    # lower graph is sonogram
    plt.subplot(2, 1, 2)
    plt.ylabel('td')
    plt.title('Hotmap')
    plt.xlabel('frequency')
    plt.grid()
    plt.pcolormesh(X_freq, Y_td, img[-1::-1,:])
    plt.yticks(Y_td[0::10], [Sweep.get_str_dt(item) for item in ts_list][0::10])
    plt.show()
    
    