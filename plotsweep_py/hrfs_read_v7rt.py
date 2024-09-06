import csv
from datetime import datetime
from typing import List
from subprocess import Popen, PIPE
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.gridspec as gridspec


# settings and constants
DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M:%S.%f'

MHZ = 1000000
kHz = 1000
DT_FORMAT = "%d.%m.%Y %H:%M:%S"
MAX_SWEEPS = 100


db_base_ch = [item*MHZ for item in range(960, 1540, 40)]


class Record:
    """
    Запись хранит в себе упрощенную строку развертки hackrf_sweep.
    Штамп времени, начальная и конечная частота, список энергетических бинов.
    Шаг, длинна сэмпла должна быть постоянной на всем протяжении разверток,
    поэтому они переносятся на более верхний уровень - в коллекцию записей.
    Заимстовано из https://github.com/greatscottgadgets/plotsweep
    """
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


class Sweep:
    """
    Развертка. Набор коллекции записей необходимо преобразовать в 
    полноценную развертку - отсортированную по частотам набор бинов мощности 
    с указанием среднего штампа времени снятия развертки. 
    Диапазон частот, шаг и ширина бина являются 
    параметрами более высокой структуры  
    """
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


class SweepCollection:
    """
    Коллекция разверток - содержит все развертки созданным hackrf_sweep.
    Постоянные величины такие как самая старшая и самая младшая частоты, 
    шаг сетки, длинна сэмплов и список записей 
    с (штампом времени и энергетическими бинами) формируются по ходу чтения строк.
    Тут же храниться максимальная история хранения разверток.
    И глубина усреднения мощности при визуализации.
    Заимстовано из https://github.com/greatscottgadgets/plotsweep
    """
    def __init__(self, max_depth_time=MAX_SWEEPS, avg_power_depth=3):
        self.sweeps: List[Sweep] = []
        self.freq_min = None
        self.freq_max = None
        self.freq_step = None
        self.num_sample = None
        self.max_depth_time = max_depth_time
        self.avg_power_depth=avg_power_depth
        
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
        samples = [int(x.split('.')[0]) for x in line[6:]]
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

    def read_sweep_shot(self, range=None, width_bin=1000000):
        if range:
            print("first show! new inicialize")
            start, stop = range
            self.start = start
            self.stop = stop
            self.width_bin = width_bin
            self.sweeps: List[Sweep] = []
            self.freq_min = None
            self.freq_max = None
            self.freq_step = None
            self.num_sample = None

        process = Popen(['hackrf_sweep', f'-f {self.start}:{self.stop}',f'-w {self.width_bin}', '-1'], 
                         stdout=PIPE,
                         stderr=PIPE,
                         text=True)
        records = []
        for row in iter(process.stdout.readline, ''):
            line = [item.strip() for item in row.strip().split(',')]
            if len(line) < 6:
                print("warning!",line)
                continue
            records.append(self._parse_line(line))
        self._get_power_spectr(records)
        for row in iter(process.stderr.readline, ''):
            if row.find('Sweeping') != -1:
                print(row.strip(), " bin counts in spectr:", self.get_bins_in_sweep())
    
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
        """Получить энергетический спектр развертки по записям"""
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
        if self.get_total_sweeps() < self.max_depth_time:
            self.sweeps.append(Sweep(avg_ts, np.array(orded_spectr, dtype=int)))
        else:
            self.sweeps.pop(0)
            self.sweeps.append(Sweep(avg_ts, np.array(orded_spectr, dtype=int)))
            
    
    def freq_range(self):
        return np.arange(self.freq_min + self.freq_step/2, self.freq_max, self.freq_step)
    
    def get_total_sweeps(self):
        return len(self.sweeps)
    
    def get_bins_in_sweep(self, index=-1):
        if self.sweeps:
            sweep = self.sweeps[-1]
            return sweep.get_bins_in_sweep()
        else:
            return 0
    
    def get_min_power(self):
        if self.sweeps:
            return min([np.min(sweep.spectr) for sweep in self.sweeps])
        return -100

    def get_hotmap(self):
        # TODO ValueError could not broadcast input array from shape (704,) into shape (1056,)
        # смотреть формирование развертки - вектора изначальные и вектор новый имеют разную размерность
        ts_list = []
        img = np.full((self.max_depth_time, self.get_bins_in_sweep()), self.get_min_power(), dtype=int)
        for index, sweep in enumerate(self.sweeps):
            img[index] = sweep.spectr
            ts_list.append(sweep.timestamp)
        return ts_list, img
    
    
    def get_avgpower(self, ts_list, img):
        ts_index = len(ts_list) - 1
        if ts_index < self.avg_power_depth:
            power = img[ts_index]
        else:
            power = np.mean(img[ts_index-self.avg_power_depth:ts_index+1:1], axis=0)
        return power

def get_base_supbin(chan):
    chan = chan - 1
    db_12video_chan = [[item*MHZ, (item-20)*MHZ, (item-6)*MHZ, (item+5)*MHZ, (item+19)*MHZ ] for item in range(960, 1540, 40)]
    return db_12video_chan[chan]

def get_base_video_chan(freq):
    for index, base_freq in enumerate([item*MHZ for item in range(960, 1540, 40)]):
        if abs(base_freq - freq) < 2e6:
            return index+1
    return None

def freq_in_base_channels_bin(freq, channel):
    sub_bin = get_base_supbin(channel)
    for f_bin in sub_bin:
        if abs(f_bin - freq) < 2e6:
            return True
    return False
    

def find_video_chans(freq_list):
    channels = []
    for freq in freq_list:
        channel = get_base_video_chan(freq)
        if channel:
            channels.append(channel)
    if channels:
        print("info! there is a possibility of a video channel", channels)
        probres = {}
        for channel in channels:
            probres[channel] = 0
            for freq in freq_list:
                if freq_in_base_channels_bin(freq, channel):
                    probres[channel] += 1
            result = {}
            print("info! may be is channels:", probres)
            for ch, wight in probres.items():
                if 2 <= wight <= 5:
                    result[ch] = wight
            return sorted(result.items(), key=lambda item: item[1])

    else:
        return []        

def get_index_freq(freq_vector, freq):
    print

if __name__ == '__main__':
    # сворачиваем диапазон на 40МГц гистограммы
    # где столбец выше - там и вещание
    # обязательно выдерживать диапазон от 940 до 1540
    # котрый разбивается на 16 поддиапазонов
    freq_range = (940, 1540)
    step = 500000
    # Получаем начальные данные первой развертки
    rc = SweepCollection()
    rc.read_sweep_shot(range=freq_range, width_bin=step)
    ts_list, img = rc.get_hotmap()
    Y_power = img[0]
    X_freq = rc.freq_range()
    max_power = np.max(img,axis=0)
    avg_max = np.average(max_power)

    Floor = np.full((rc.get_bins_in_sweep(),), avg_max, dtype=int)
    # print(Floor)
    # Формируем сетку с графиками
    fig = plt.figure(figsize=(16, 8),facecolor='white')
    
    gs = gridspec.GridSpec(2, 1)
    ax_u = plt.subplot(gs[0,0])
    ax_u.set_axis_off
    ax_u.set_ylim(rc.get_min_power() - 10, 0)
    ax_u.set_title('Power')
    ax_u.set_ylabel('Power (dB)', fontsize=16)
    ax_u.set_xlim(X_freq[0], X_freq[-1])
    # ax_u.set_xticks(fontsize=10)
    line, = ax_u.plot(X_freq, Y_power)
    ln_floor, = ax_u.plot(X_freq, Floor)
    max_markers = 10
    markers, = ax_u.plot([], [], marker="D", ls='', color="red" )
    ax_d = plt.subplot(gs[1,0])
    quad = ax_d.pcolormesh(X_freq,range(0,-rc.max_depth_time,-1), img, shading='gouraud', )
    ax_d.set_xlabel('frequency', fontsize=16)
    ax_d.set_ylabel('time', fontsize=16)
    ax_d.set_yticks([])
    # quad = ax_d.pcolormesh(img)
    f_count = 0
    def n_largest_indices_sorted(arr, n):
        indices = np.argpartition(arr, -n)[-n:]
        return indices[np.argsort(-arr[indices])]
    
    
        
    def update(phasa):
        try:
            rc.read_sweep_shot()
            ts_list, img = rc.get_hotmap()
        except IndexError as e:
            print("warning!", e)
        except ValueError as e:
            print("warning!", e)
        else:
            Y_power = rc.get_avgpower(ts_list, img)
            # поиск максимальной огибающей и максималносредней
            max_power = np.max(img, axis=0)
            avg_max = np.average(max_power)
            Floor = np.full((rc.get_bins_in_sweep(),), avg_max, dtype=int)
            # поиск частот с пиками
            max_indexes = n_largest_indices_sorted(Y_power, 20)
            max_indexes = max_indexes.tolist()
            
            for i, x in enumerate(max_indexes):
                for y in max_indexes[i+1:]:
                    if abs(x-y) <= 4:
                        max_indexes.remove(y)
            max_freq_find = [X_freq[index] for index in max_indexes]
            # print([int(np.average(Y_power[index * 83: (index+1) * 84]) - avg_max) for index in range(16)])
            ln_floor.set_data(X_freq, Floor)
            line.set_data(X_freq, Y_power)
            quad.set_array(img.ravel())            
            vchans = [chan[0] for chan in find_video_chans(max_freq_find)]
            global f_count
            if vchans:
                f_count += 1
                if f_count > 3:
                    f_count = 3
            else:
                if f_count > 0:
                    f_count -= 1
            print(vchans, f_count)
            if vchans and f_count > 2:
                print("Warning!! Fing channels:", vchans)
                # ax_u.set_title(f"Power: find video chan - {str(vchans)}")
                vfreq = []
                for vchan in vchans:
                    vfreq.extend(get_base_supbin(vchan))
                find_indexes = []
                for freq in vfreq:
                    nearest_val = X_freq.flat[np.abs(X_freq - freq).argmin()]
                    find_indexes.append(np.where(X_freq == nearest_val)[0][0])
                markers.set_data([X_freq[index] for index in find_indexes], [Y_power[index] for index in find_indexes]) 
            else:
                markers.set_data([], [])
                

        finally:
            return [line, ln_floor, quad, markers]
                
        
            
    animation = FuncAnimation(fig, func=update, interval=1000,
                              blit=True, repeat=False, ) 
    gs.tight_layout(fig)
    plt.show()
    