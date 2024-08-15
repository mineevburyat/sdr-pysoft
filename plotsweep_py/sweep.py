from hrfs_read_v4 import RecordCollection, MHZ, kHz
import numpy as np

NOISE_LEVEL = -100

class Sweep:
    def __init__(self, dt, freq_min, freq_max, bin_width, spectr):
        if type(spectr) != list:
            raise TypeError("spectr variable mast been list of power bins")
        len_spectr = len(spectr)
        if len_spectr == 0:
            raise ValueError("spectr is not be empty")
        
        self.dt = dt
        self.spectr = np.array(spectr)
        self.freq_range = np.arange(freq_min + bin_width/2, freq_max, bin_width)
        # print(len(self.freq_range), len_spectr)
        # последние развертки содержут не весь диапазон, необходимо 
        # дополнить noise level оставшийся диапазон
        if len(self.freq_range) != len_spectr:
            holder = np.zeros(len(self.freq_range) - len_spectr)
            holder[...] = NOISE_LEVEL
            self.spectr = np.hstack((self.spectr, holder))
            # print(self.spectr)

    
        
if __name__ == "__main__":
    files = ['2.csv', '3.csv', '4.csv', '5.csv', '6.csv', '7.csv', '8.csv',]
    for file in files:
        rc = RecordCollection(file)
        for index in range(len(rc.records_on_sweep)):
            sweep = Sweep(*rc.get_power_spectr(index))
            # print(sweep.freq_range)
            # print(sweep.spectr)
            if len(sweep.freq_range) == len(sweep.spectr):
                continue
            else:
                raise ValueError("dimensions not equvalent")