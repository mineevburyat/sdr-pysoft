from hrfs_read_v4 import RecordCollection, MHZ, kHz

rc = RecordCollection('2.csv')
dt, f_min, f_max, f_step, spectr = rc.get_power_spectr(0)

class Sweep:
    def __init__(self, dt, freq_min, freq_max, freq_step, spectr):
        self.dt = dt
        self.spectr = spectr
        
        if type(spectr) != list:
            raise TypeError("spectr variable is list of power bins")
        len_spectr = len(spectr)
        if len_spectr == 0:
            raise ValueError("spectr is not be empty")
        freq_range = range(int(freq_min), int(freq_max), int(freq_step))
        if len(freq_range) - len_spectr == 0:
            self.freq_range = freq_range
        elif len(freq_range) - len_spectr == 1:
            # warning 
            self.freq_range = range(int(freq_min), int(freq_max - freq_step), int(freq_step))
        else:
            raise ValueError("frequency demention not equevalent power bin dimention") 
        
        
if __name__ == "__main__":
    rc = RecordCollection('2.csv')
    for index in range(len(rc.records_on_sweep)):
        sweep = Sweep(*rc.get_power_spectr(index))
        print(sweep.freq_range)