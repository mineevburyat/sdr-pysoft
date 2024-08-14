import csv
from datetime import datetime
from typing import List, Dict, Any, Union


# settings and constants
DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M:%S.%f'
file_path = '3.csv'

MHZ = 1000000
kHz = 1000

"""
 Запись хранит в себе упрощенную строку развертки hackrf_sweep.
 Штамп времени, начальная и конечная частота, список энергетических бинов.
 Шаг, длинна сэмпла должна быть постоянной на всем протяжении разверток,
 поэтому они переносятся на более верхний уровень - в коллекцию записей.
 Заимстовано из https://github.com/greatscottgadgets/plotsweep
"""
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

"""
 Коллекция записей - содержит все записи из csv файла созданным hackrf_sweep.
 Постоянные величины такие как самая старшая и самая младшая частоты, шаг сетки,
 длинна сэмплов и список записей с (штампом времени, поддиапазоном и 
 энергетическими бинами) формируются по ходу чтения файла.
  Заимстовано из https://github.com/greatscottgadgets/plotsweep
"""

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

    def get_sweep(self, start_index, stop_index=-1):
        # формируем развертку по указанным записям, 
        # сохраняем время когда снимали развертку и сохраняем в коллекции разверток
        sweep_records = self.records[start_index : stop_index]
        if sweep_records:
            sum_ts = sum([record.timestamp for record in sweep_records])
            return Sweep(
                datetime.fromtimestamp(sum_ts / len(sweep_records)), 
                sweep_records)
        else:
            raise IndexError('records of sweep is empty')
       

class Sweep:
    def __init__(self, timestamp_sweep, sweep_lines):
        self.timestamp = timestamp_sweep
        self.sweep_lines = sweep_lines

    def __repr__(self):
        return f"Object Sweep: {self.timestamp} lines: {len(self.sweep_lines)}"

class SweepCollections:
    def __init__(self):
        self.sweeps: List[Sweep] = []

    def add_sweep(self, sweep):
        if type(sweep) == Sweep:
            self.sweeps.append(Sweep)

    def __repr__(self):
        return f"Object Sweeps Collections: Count sweeps: {len(self.sweeps)}"



sweeps = SweepCollections()
with open(file_path, 'r') as f:
    reader = csv.reader(f)
    rc = RecordCollection()
    line_count = 0
    for row in reader:
        line = [item.strip() for item in row]
        line_count += 1
        timestamp = Record.parse_datetime(line[0], line[1])
        # помере перебора строк ищем самую маленькую и большую частоты, 
        # шаг сетки, длинна сэмпла - они обычно постоянны на всем 
        # протяжении развертки 
        freq_low = int(line[2])
        rc.find_min_freq(int(line[2]))
        freq_high = int(row[3])
        rc.find_max_freq(int(line[3]))
        freq_step = float(line[4])
        rc.find_step(float(line[4]))
        rc.find_num_sampl(int(line[5]))
        # сохраняем строку как элементарную запись
        samples = [float(x) for x in line[6:]]
        record = Record(timestamp=timestamp, freq_low=freq_low, freq_high=freq_high, samples=samples)
        rc.records.append(record)
        # разбор строки заканчивается, но
        # следует учесть что развертка (sweep) состоит из нескольких строк:  
        # штампвремени, мин и макс частоты, шаг и список мощностей в этом диапазоне.
        # Основной задачей является получить не отдельные записи мощностей, 
        # а всю развертку от минимальной до максимальной частоты
        # и соответсвенно коллекцию таких разверток
        # сигналом для следующей развертки является появление минимальной 
        # частоты в строке.
        if freq_low == rc.freq_min and rc.sweeps == 0 and line_count == 1:
            # пропускаем первую строку и ищем начало следующей развертки
            continue
        if freq_low == rc.freq_min:
            sweep = rc.get_sweep(rc.sweeps * (line_count-1))
            sweeps.add_sweep(sweep)
            # считывание развертки завершилось, начинаем следующую развертку
            line_count = 1
            rc.sweeps += 1
# часть строк в коллекции разверток теряется 
# оставшуюся часть записей считаем за еще одну развертку
rc.sweeps += 1
# и востановливаем из коллекции записей
sweeps.add_sweep(rc.get_sweep(-line_count))

print(rc)
print(sweeps)

# def get_sweepcollection(self):
    #     # формируем развертку по указанным записям, 
    #     # сохраняем время когда снимали развертку 
    #     # и сохраняем в коллекции разверток
    #     sweeps = SweepCollections()
    #     print(sweeps)
    #     for index, total_records in enumerate(self.records_on_sweep):
    #         sweep_records = self.records[index * total_records : (index + 1) * total_records]
    #         if sweep_records:
    #             avg_ts = sum([record.timestamp for record in sweep_records]) / len(sweep_records)
    #             step = self.freq_step
    #             spectr = {}
    #             for record in sweep_records:
    #                 freq_low = record.freq_low
    #                 for index, power_bin in enumerate(record.samples):
    #                     freq = freq_low + step * (index+1)
    #                     spectr[int(freq)] = power_bin
    #         else:
    #             raise IndexError('records of sweep is empty')
    #         dt_str = datetime.fromtimestamp(avg_ts)
    #         sweeps.add_sweep(Sweep(dt_str, spectr))
    #     print(sweeps)
    #     return sweeps