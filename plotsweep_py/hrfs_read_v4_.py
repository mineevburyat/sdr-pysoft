import csv
from datetime import datetime
from typing import List, Dict, Any, Union


# settings and constants
DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M:%S.%f'

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
    def __init__(self, file_csv=None):
        self.records: List[Record] = []
        self.freq_min = None
        self.freq_max = None
        self.freq_step = None
        self.num_sample = None
        self.records_on_sweep = []
        if file_csv:
            self.read_sweep_csv(file_csv)
        
    @staticmethod
    def parse_datetime(data: str, time: str) -> float:
        dt = datetime.combine(
            datetime.strptime(data, DATE_FORMAT).date(), 
            datetime.strptime(time, TIME_FORMAT).time())
        return dt.timestamp()

    def __str__(self):
        if self.records:
            freq_min = int(self.freq_min / MHZ)
            freq_max = int(self.freq_max / MHZ)
            step = int(self.freq_step / kHz)
            total_sweeps = len(self.records_on_sweep)
            records_in_sweep = self.records_on_sweep[0]
            last_records = self.records_on_sweep[-1]
            return f"{freq_min}-{freq_max} MHz, step {step} kHz, total sweeps: {total_sweeps}, records on sweep: {records_in_sweep}, record on last sweep: {last_records}"
        else:
            return "Empty Records Collection"
    
    def __repr__(self) -> str:
        total_sweeps = len(self.records_on_sweep)
        return f"Object RecordCollection (total sweeps {total_sweeps})"
    
    def find_min_freq(self, freq):
        if self.freq_min is not None:
            self.freq_min = min(self.freq_min, freq)
        else:
            self.freq_min = freq

    def find_max_freq(self, freq):
        if self.freq_max is not None:
            self.freq_max = max(self.freq_max, freq)
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

    def read_sweep_csv(self, file_name):
        with open(file_name, 'r') as f:
            reader = csv.reader(f)
            line_count = 0
            sweep = 0
            for row in reader:
                line = [item.strip() for item in row]
                line_count += 1
                timestamp = self.parse_datetime(line[0], line[1])
                # помере перебора строк ищем самую маленькую и большую частоты, 
                # шаг сетки, длинна сэмпла - обычно постоянны на всем 
                # протяжении разверток 
                freq_low = int(line[2])
                freq_high = int(row[3])
                self.find_step(float(line[4]))
                self.find_num_sampl(int(line[5]))
                self.find_min_freq(freq_low)
                self.find_max_freq(freq_high)
                # сохраняем строку как элементарную запись
                samples = [float(x) for x in line[6:]]
                record = Record(timestamp=timestamp, 
                                freq_low=freq_low, 
                                freq_high=freq_high, 
                                samples=samples)
                self.records.append(record)
                
                # разбор строки завершен, но необходимо разделить отдельные развертки
                # сигналом начало новой развертки появление самой минимальной частоты
                if freq_low == self.freq_min and sweep == 0 and line_count == 1:
                    # пропускаем первую строку и ищем начало следующей развертки
                    continue
                if freq_low == self.freq_min:
                    # считывание развертки завершилось, 
                    # сохраняем количество записей в развертке и
                    # начинаем следующую развертку
                    self.records_on_sweep.append(line_count - 1)
                    line_count = 1
                    sweep += 1
        # часть строк в коллекции разверток теряется 
        # оставшуюся часть записей считаем за еще одну развертку
        self.records_on_sweep.append(line_count)
    
    
    def get_power_spectr(self, index):
        """Получить энергетический спектр развертки по индексу"""
        records_on_sweep = self.records_on_sweep[index]
        sweep_records = self.records[index * records_on_sweep : (index + 1) * records_on_sweep]
        if sweep_records:
            avg_ts = sum([record.timestamp for record in sweep_records]) / len(sweep_records)
            step = self.freq_step
            spectr = {}
            for record in sweep_records:
                freq_low = record.freq_low
                for i, power_bin in enumerate(record.samples):
                    freq = freq_low + step * (i+1)
                    spectr[int(freq)] = power_bin
        else:
            raise IndexError(f'records of sweep is empty on {index}, records in this sweep {self.records_on_sweep[index]}')
        
        orded_spectr = [power for freq, power in sorted(spectr.items())]
        return (avg_ts, self.freq_min, self.freq_max, self.freq_step, orded_spectr)


if __name__ == '__main__':
    rc = RecordCollection('2.csv')
    print(rc)
    ts, f_min, f_max, f_step, spectr = rc.get_power_spectr(0)
    dt_str = datetime.fromtimestamp(ts)
    print(dt_str, f_min / MHZ, f_max / MHZ, round(f_step / kHz, 1), len(spectr))