import csv
from datetime import datetime
from typing import List, Dict, Any, Union


# settings parsing
DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M:%S.%f'
file_path = '3.csv'

MHZ = 1000000
kHz = 1000

class Record:
    def __init__(
        self,
        timestamp: float,
        freq_low: float,
        freq_high: float,
        samples: List[float] = [],
    ):
        self.__timestamp = timestamp
        self.__freq_low = freq_low
        self.__freq_high = freq_high
        self.__samples = samples

    @staticmethod
    def parse_datetime(data: str, time: str) -> float:
        dt = datetime.combine(
            datetime.strptime(data, DATE_FORMAT).date(), 
            datetime.strptime(time, TIME_FORMAT).time())
        return dt.timestamp()

    # @staticmethod
    # def parse_time(s: str) -> datetime.time:
    #     return datetime.time.strptime(s, time_format)

    @property
    def timestamp(self):
        return self.__timestamp
    
    @property
    def freq_low(self):
        return self.__freq_low
    
    @property
    def freq_high(self):
        return self.__freq_high
    
    @property
    def samples(self):
        return self.__samples

    def __repr__(self):
        return f"Object Record: {int(self.freq_low / MHZ)}-{int(self.freq_high / MHZ)} MHz, bins: {len(self.samples)}"

class Sweep:
    def __init__(self, timestamp_sweep, sweep_lines):
        self.timestamp = timestamp_sweep
        self.sweep_lines = sweep_lines

    def __repr__(self):
        # print(self.timestamp)
        # dt = datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')
        return f"Object Sweep: {self.timestamp} lines: {len(self.sweep_lines)}"

class SweepCollections:
    def __init__(self):
        self.sweeps: List[Sweep] = []

    def add_sweep(self, sweep):
        if type(sweep) == Sweep:
            self.sweeps.append(Sweep)

    def __repr__(self):
        return f"Object Sweeps Collections: Count sweeps: {len(self.sweeps)}"

class RecordCollection:
    def __init__(self):
        self.records: List[Record] = []
        self.freq_min = None
        self.freq_max = None
        self.freq_step = None
        self.num_sample = None
        self.sweeps = 0
        
    
    def __str__(self):
        return f"{int(self.freq_min / MHZ)}-{int(self.freq_max / MHZ)} MHz, step {int(self.freq_step / kHz)} kHz, sweeps: {self.sweeps}, records: {len(self.records)}"
    
    def find_min_freq(self, freq):
        if self.freq_min is not None:
            self.freq_min = min(self.freq_min, freq)
        else:
            self.freq_min = freq

    def find_max_freq(self, freq):
        if self.freq_max is not None:
            self.freq_max = max(rc.freq_max, freq)
        else:
            self.freq_max = freq

    def find_step(self, step):
        if self.freq_step is not None:
            if abs(step - self.freq_step) > 1e-5:
                raise ValueError(f"Frequency step must be constant\nfind {step} other {self.freq_step}")
        else:
            self.freq_step = step

    def find_num_sampl(self, num_sample):
        if self.num_sample is not None:
            if num_sample != self.num_sample:
                raise ValueError(f"Number sample mast be constant\nfind {num_sample} other {self.num_sample}")
        else:
            self.num_sample = num_sample

sweeps = SweepCollections()
with open(file_path, 'r') as f:
    reader = csv.reader(f)
    rc = RecordCollection()
    sweep_line_count = 0
    for row in reader:
        line = [item.strip() for item in row]
        timestamp = Record.parse_datetime(line[0], line[1])
        # помере перебора строк ищем самую маленькую частоту
        freq_low = int(line[2])
        rc.find_min_freq(int(line[2]))
        # if rc.freq_min is not None:
        #     rc.freq_min = min(rc.freq_min, freq_low)
        # else:
        #     rc.freq_min = freq_low
        # Ищем самую высокую частоту
        freq_high = int(row[3])
        rc.find_max_freq(int(line[3]))
        # if rc.freq_max is not None:
        #     rc.freq_max = max(rc.freq_max, freq_high)
        # else:
        #     rc.freq_max = freq_high
        # Шаг частоты должен быть постоянным на всем протяжении развёрток
        freq_step = float(line[4])
        rc.find_step(float(line[4]))
        # if rc.freq_step is not None:
        #     if abs(freq_step - rc.freq_step) > 1e-5:
        #             raise ValueError(f"Frequency step must be constant\n{row}")
        # else:
        #     rc.freq_step = freq_step
        rc.find_num_sampl(int(line[5]))
        # сохраняем строку как элементарную запись
        samples = [float(x) for x in line[6:]]
        record = Record(timestamp=timestamp, freq_low=freq_low, freq_high=freq_high, samples=samples)
        rc.records.append(record)
        # следует учесть что развертка (sweep) состоит из нескольких строк:  
        # частотой и мощностью на этой частоте.
        # Основной задачей является получить не отдельные записи мощностей, 
        # а всю развертку от минимальной до максимальной частоты
        # и соответсвенно коллекцию таких разверток
        if freq_low == rc.freq_min:
            if rc.sweeps != 0:
                sweep_records = rc.records[(rc.sweeps - 1) * sweep_line_count : (rc.sweeps * sweep_line_count)]
                sum = 0
                for record in sweep_records:
                    sum += record.timestamp
                sweep = Sweep(datetime.fromtimestamp(sum / len(sweep_records)), sweep_records)
                sweep_line_count = 0
                sweeps.add_sweep(sweep)
            rc.sweeps += 1
        sweep_line_count += 1
        

            

print(rc)
print(sweeps)