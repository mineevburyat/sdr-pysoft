import csv
from datetime import datetime
from typing import List, Dict, Any, Union
from subprocess import Popen, PIPE, DEVNULL, STDOUT, run
import numpy as np
import matplotlib.pyplot as plt
import time
from matplotlib.animation import FuncAnimation


# settings and constants
DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M:%S.%f'

MHZ = 1000000
kHz = 1000
DT_FORMAT = "%d.%m.%Y %H:%M:%S"
MAX_SWEEPS = 100


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
 Развертка. Набор коллекции записей преобразуем в полноценную развертку - 
 отсортированную по частотам набор бинов мощности с указанием среднего времени 
 снятия развертки. Диапазон частот, шаг и ширина бина является 
 параметром более высокой структуры  
"""
class Sweep:
    def __init__(self, timestamp, spectr):
        if type(spectr) != np.ndarray:
            raise TypeError("Sweep convertion: spectr variable mast been numpy array of power bins")
        counts_in_spectr = len(spectr)
        if counts_in_spectr == 0:
            raise ValueError("spectr is not be empty")
        
        self.timestamp = timestamp
        self.spectr = np.array(spectr)
        

    def get_bins_in_sweep(self):
        return len(self.spectr)
    
    def min_power(self):
        return np.min(self.spectr)
    
    def max_power(self):
        return np.max(self.spectr)
    
    def get_str_dt(self):
        return datetime.fromtimestamp(self.timestamp).strftime(DT_FORMAT)
    
    def __repr__(self):
        return f"{self.get_str_dt()}: {len(self.spectr)}"

"""
Коллекция разверток - содержит все развертки созданным hackrf_sweep.
 Постоянные величины такие как самая старшая и самая младшая частоты, шаг сетки,
 длинна сэмплов и список записей с (штампом времени, поддиапазоном и 
 энергетическими бинами) формируются по ходу чтения файла.
  Заимстовано из https://github.com/greatscottgadgets/plotsweep
"""
class SweepCollection:
    def __init__(self, file_csv=None, range=None, width_bin=1000000):
        self.sweeps: List[Sweep] = []
        self.freq_min = None
        self.freq_max = None
        self.freq_step = None
        self.num_sample = None
        
        if file_csv:
            self.read_sweep_csv(file_csv)
        elif range and type(range) == tuple:
            self.read_sweep_realtime(range, width_bin)
        else:
            print("warning! sweepcollection is empty")
    
    def __str__(self):
        if self.sweeps:
            freq_min = int(self.freq_min / MHZ)
            freq_max = int(self.freq_max / MHZ)
            step = int(self.freq_step / kHz)
            total_sweeps = self.get_total_sweeps()
            bins_in_sweep = self.get_bins_in_sweep()
            return f"{freq_min}-{freq_max} MHz, step {step} kHz, total sweeps: {total_sweeps}, bins on sweep: {bins_in_sweep}"
        else:
            return "Empty Sweeps Collection"

    @staticmethod
    def parse_datetime(data: str, time: str) -> float:
        dt = datetime.combine(
            datetime.strptime(data, DATE_FORMAT).date(), 
            datetime.strptime(time, TIME_FORMAT).time())
        return dt.timestamp()
    
    @staticmethod
    def get_str_dt(timestamp):
        return datetime.fromtimestamp(timestamp).strftime(DT_FORMAT)
    
    def _parse_line(self, line):
        timestamp = self.parse_datetime(line[0], line[1])
        freq_low = int(line[2])
        freq_high = int(line[3])
        self.find_step(float(line[4]))
        self.find_num_sampl(int(line[5]))
        self.find_min_freq(freq_low)
        self.find_max_freq(freq_high)
        # сохраняем строку как элементарную запись
        samples = [float(x) for x in line[6:]]
        return Record(timestamp=timestamp, 
                        freq_low=freq_low, 
                        freq_high=freq_high, 
                        samples=samples)
        


    def read_sweep_csv(self, file_name):
        with open(file_name, 'r') as f:
            reader = csv.reader(f)
            records = []
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
                freq_high = int(line[3])
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
                records.append(record)
                
                # разбор строки завершен, но необходимо разделить отдельные развертки
                # сигналом начало новой развертки появление самой минимальной частоты
                if freq_low == self.freq_min and sweep == 0 and line_count == 1:
                    # пропускаем первую строку и ищем начало следующей развертки
                    continue
                if freq_low == self.freq_min:
                    # считывание развертки завершилось, 
                    # сохраняем количество записей в развертке и
                    # начинаем следующую развертку
                    # TODO последние развертки обычно содержат не весь диапазон, 
                    # необходимо дополнить минимальной мощностью оставшийся диапазон 
                    # для сохранения размерности
                    # if self.get_bins_in_sweep != counts_in_spectr:
                    #     holder = np.zeros(self.get_bins_in_range() - counts_in_spectr)
                    #     holder[...] = self.min_power()
                    #     self.spectr = np.hstack((self.spectr, holder))
                    self._get_power_spectr(records)
                    records = [records[-1]]
                    line_count = 1
                    sweep += 1
        # часть строк в коллекции разверток теряется 
        # оставшуюся часть записей считаем за еще одну развертку
        # self.records_on_sweep.append(line_count)
    
    def read_sweep_realtime(self, range, width_bin):
        start = range[0]
        stop = range[1]
        process = Popen(['hackrf_sweep', f'-f {start}:{stop}',f'-w {width_bin}', '-1'], stdout=PIPE)
        records = []
        line_count = 0
        
        while process.poll() is None:
            # print(f'\r{run_str[indx]} {count_find} ({count_freq})', end='')
            row = process.stdout.readline().strip().split(b', ')
            line = [str(item)[2:-1] for item in row]
            line_count += 1
            if len(line) < 6:
                continue
            # print(line)
            # ch_count = len(line) - 6
            timestamp = self.parse_datetime(line[0], line[1])
            freq_low = int(line[2])
            freq_high = int(line[3])
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
            records.append(record)
        self._get_power_spectr(records)

    def read_sweep_shot(self, range, width_bin=1000000):
        start, stop = range
        process = Popen(['hackrf_sweep', f'-f {start}:{stop}',f'-w {width_bin}', '-1'], 
                         stdout=PIPE,
                         text=True)
        records = []
        for row in iter(process.stdout.readline, ''):
            line = [item.strip() for item in row.strip().split(',')]
            if len(line) < 6:
                continue
            records.append(self._parse_line(line))
        self._get_power_spectr(records)
    
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

    def _get_power_spectr(self, records: List[Record]):
        """Получить энергитический спектр развертки по записям"""
        if records:
            avg_ts = sum([record.timestamp for record in records]) / len(records)
            step = self.freq_step
            spectr = {}
            for record in records:
                freq_low = record.freq_low
                for i, power_bin in enumerate(record.samples):
                    freq = freq_low + step * (i+1)
                    spectr[int(freq)] = power_bin
        else:
            raise IndexError('records of sweep is empty')
        
        orded_spectr = [power for freq, power in sorted(spectr.items())]
        if self.get_total_sweeps() < MAX_SWEEPS:
            self.sweeps.append(Sweep(avg_ts, np.array(orded_spectr)))
        else:
            self.sweeps.append(Sweep(avg_ts, np.array(orded_spectr)))
            self.sweeps.pop(0)
    
    def freq_range(self):
        return np.arange(self.freq_min + self.freq_step/2, self.freq_max, self.freq_step)
    
    def get_total_sweeps(self):
        return len(self.sweeps)
    
    def get_bins_in_sweep(self):
        if self.sweeps:
            sweep = self.sweeps[0]
            return sweep.get_bins_in_sweep()
        else:
            return 0
    
    def get_min_power(self):
        return min([np.min(sweep.spectr) for sweep in self.sweeps])

    def get_hotmap(self):
        count = 0
        ts_list = []
        # img = np.zeros((self.get_bins_in_sweep, MAX_RECORDS), dtype=float)
        # img[:] = self.get_min_power()
        for sweep in self.sweeps:
            if count == 0:
                img = np.array(sweep.spectr)
            else:
                img = np.vstack((img, sweep.spectr))
            ts_list.append(sweep.timestamp)
            count += 1
        return ts_list, img
    
    

if __name__ == '__main__':
    rc = SweepCollection()
    rc.read_sweep_shot(range=(980,1400), width_bin=250000)
    X_freq = rc.freq_range()
    ts_list, img = rc.get_hotmap()
    Y_power = img
    # find max power
    # Y_maxpower = np.max(img, axis=0)
    # max_power_index = np.argmax(Y_power)
    # max_power = np.max(Y_power)
    # freq_max = X_freq[max_power_index]
    # find average power line
    Y_avgpower = np.zeros(len(X_freq))
    Y_avgpower[...] = np.mean(Y_power)
    
    fig, ax = plt.subplots()
    line, = ax.plot(X_freq, Y_power)
    # line_avg, = ax.plot(X_freq, Y_avgpower)
    
    

    def init(line):
        ax.set_xlim(X_freq)
        ax.set_ylim(rc.get_min_power, 0)
        line.set_data(X_freq, Y_power)
        return line
    
    def update(phasa, line):
        rc.read_sweep_shot(range=(980,1400), width_bin=250000)
        ts_list, img = rc.get_hotmap()
        X_freq = rc.freq_range()
        # Y_td = np.arange(0, -len(ts_list), -1)
        print(img.shape)
        # row, col = img.shape
        if len(img.shape) == 1:
            Y_power = img
        else:
            row, col = img.shape
            if row <= 5:
                Y_power = np.mean(img, axis=0)
            else:
                Y_power = np.mean(img[-1:-5:-1], axis=0)
        line.set_data(X_freq, Y_power)
        return [line]
            
    animation = FuncAnimation(fig, func=update, interval=1000,
                              blit=True, repeat=False, fargs=(line, ),) 
    plt.show()
    