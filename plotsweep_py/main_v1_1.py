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
    rc = RecordCollection('test.csv')
    print('parsing ok')
    # plt.show()
    count = 0
    count_sweep = len(rc.records_on_sweep)
    ts_list = np.zeros(count_sweep)
    for index_sweep in range(count_sweep):
        sweep = Sweep(*rc.get_power_spectr(index_sweep))
        if count == 0:
            img = np.array(sweep.spectr)
        else:
            img = np.vstack((img, sweep.spectr))
        ts_list[count] = sweep.timestamp
        count += 1
    print()
    
    
    
    plt.subplot(1, 1, 1)
    plt.title('Hotmap')
    plt.xlabel('frequency')
    plt.ylabel('td')
    
    # plt.xlim(sweep.f_min, sweep.f_max)
    # print(f_min, f_max)
    # plt.xticks(np.arange(f_min + f_step/2, f_max, f_step * 50))
    plt.grid()
    
    # plt.yticks()
    plt.pcolormesh(img[-1::-1,:], vmin=sweep.min_power(), vmax=sweep.max_power())
    
    plt.colorbar()
    plt.show()
    
    