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
    rc = RecordCollection('8ch.csv')
    print('parsing ok')
    plt.subplot(1, 1, 1)
    plt.title('Power spectr bins')
    plt.xlabel('frequency')
    plt.ylabel('power (dB)')
    # plt.show()
    count = 0
    
    for sweep in range(len(rc.records_on_sweep)):
        count += 1
        dt, f_min, f_max, f_step, spectr = rc.get_power_spectr(0)
        if count == 1:
            avg_spectr = [0 for _ in range(len(spectr))]
        avg_spectr = [(avg_power + power) for avg_power, power in zip(avg_spectr, spectr)]
        # print(dt, int(f_min+f_step/2), int(f_max - f_step/2), int(f_step), len(spectr))
        # x = range(int(f_min), int(f_max - f_step), int(f_step))
    print()
    x = np.arange(f_min+f_step/2, f_max, f_step)
    y = [avg_power / count for avg_power in avg_spectr]
    avg = np.zeros((len(spectr),))
    avg[...] = sum(y) / len(y)
    plt.text(1, 1, dt)
    plt.plot(x, y)
    plt.plot(x,avg)
    plt.grid()
    plt.show()