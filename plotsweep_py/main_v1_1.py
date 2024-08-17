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
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    print('start parsing csv')
    rc = RecordCollection('test.csv')
    print('parsing ok')
    # plt.show()
    count = 0
    
    
    for sweep in range(len(rc.records_on_sweep)):
        count += 1
        dt, f_min, f_max, f_step, spectr = rc.get_power_spectr(0)
        if count == 1:
            img = np.array(spectr)
        else:
            img = np.vstack((img, spectr))
        
    print()
    
    
    
    plt.subplot(1, 1, 1)
    plt.title('Hotmap')
    plt.xlabel('frequency')
    plt.ylabel('td')
    plt.pcolormesh(img)
    plt.colorbar()
    # plt.xlim(f_min + f_step/2, f_max)
    # plt.xticks(np.arange(f_min + f_step/2, f_max, f_step * 100))
    # plt.yticks()
    plt.show()
    
    