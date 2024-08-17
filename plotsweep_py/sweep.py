from hrfs_read_v4 import RecordCollection, MHZ, kHz
import numpy as np
from datetime import datetime

DT_FORMAT = "%d.%m.%Y %H:%M:%S"

class Sweep:
    def __init__(self, timestamp, freq_min, freq_max, bin_width, spectr):
        if type(spectr) != list:
            raise TypeError("spectr variable mast been list of power bins")
        counts_in_spectr = len(spectr)
        if counts_in_spectr == 0:
            raise ValueError("spectr is not be empty")
        
        self.timestamp = timestamp
        self.spectr = np.array(spectr)
        self.f_min = freq_min
        self.f_max = freq_max
        self.f_step = bin_width
        # последние развертки обычно содержат не весь диапазон, 
        # необходимо дополнить минимальной мощностью оставшийся диапазон 
        # для сохранения размерности
        if self.get_bins_in_range != counts_in_spectr:
            holder = np.zeros(self.get_bins_in_range() - counts_in_spectr)
            holder[...] = self.min_power()
            self.spectr = np.hstack((self.spectr, holder))

    def freq_range(self):
        return np.arange(self.f_min + self.f_step/2, self.f_max, self.f_step)
    
    def get_bins_in_range(self):
        return len(self.freq_range())
    
    def min_power(self):
        return np.min(self.spectr)
    
    def max_power(self):
        return np.max(self.spectr)
    
    @staticmethod
    def get_str_dt(timestamp):
        return datetime.fromtimestamp(timestamp).strftime(DT_FORMAT)
        
    

class SweepCollections:
    def __init__(self ):
        pass



if __name__ == "__main__":
    files = ['2.csv', '3.csv', '4.csv', '5.csv', '6.csv', '7.csv', '8.csv',]
    for file in files:
        rc = RecordCollection(file)
        for index in range(len(rc.records_on_sweep)):
            sweep = Sweep(*rc.get_power_spectr(index))
            # print(sweep.freq_range)
            # print(sweep.spectr)
            if sweep.get_bins_in_range() == len(sweep.spectr):
                print(sweep.get_str_dt(sweep.timestamp))
                continue
            else:
                raise ValueError("dimensions not equvalent")