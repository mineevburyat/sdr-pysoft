from subprocess import Popen, PIPE, DEVNULL, STDOUT
from time import sleep, mktime, strptime
from datetime import datetime
import numpy as np
from frange import FreqRange, FreqRanges
from hrfs_read_v4 import Record, RecordCollection


freq_range = FreqRanges((125, 150),
                       (420, 450),
                       (800, 900),
                       (990, 1400),
                       (2300, 2500)
)

# product
process = Popen(['hackrf_sweep', '-w 500000', '-a 1'], stdout=PIPE)
# debug
# out = Popen(['hackrf_sweep', '-f 200:6000', '-1'], stdout=PIPE)


run_str = ['|', '/', '-', '\\']
indx = 0
print('start hackrf_sweep.....')

SNR = 20 # dB превышение уровня шума
scan_analiz = {} # 
history = {}
count_freq = 0
count_find = 0
min_power = 0
max_power = -100

DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M:%S.%f'

def parse_datetime(data: str, time: str) -> float:
        dt = datetime.combine(
            datetime.strptime(data, DATE_FORMAT).date(), 
            datetime.strptime(time, TIME_FORMAT).time())
        return dt.timestamp()

def find_step(step):
        if freq_step is not None:
            if abs(step - freq_step) > 1e-5:
                raise ValueError(f"Frequency step must be constant\nfind {step} other {self.freq_step}")
        else:
            freq_step = step

try:
    while process.poll() is None:
        print(f'\r{run_str[indx]} {count_find} ({count_freq})', end='')
        line = process.stdout.readline().strip().split(b', ')
        if len(line) > 6:
            timestamp = parse_datetime(line[0], line[1])
            ch_count = len(line) - 6
            powers = np.array([float(item) for item in line[6:]])
            avg = powers.mean()
            min_power = min(min_power, np.min(powers))
            max_power = max(max_power, np.max(powers))

    with open(file_name, 'r') as f:
            reader = csv.reader(f)
            line_count = 0
            sweep = 0
            for row in reader:
                line = [item.strip() for item in row]
                line_count += 1
                
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
    


    
        print(f'\r{run_str[indx]} {count_find} ({count_freq})', end='')
        line = process.stdout.readline().strip().split(b', ')
        if len(line) > 6:
            ch_count = len(line) - 6
            powers = np.array([float(item) for item in line[6:]])
            avg = powers.mean()
            min_power = min(min_power, np.min(powers))
            max_power = max(max_power, np.max(powers))
            for index, power in enumerate(powers):
                freq = float(line[2]) + float(line[4]) * index
                if freq_range.inranges(freq * 1e6):
                    if power > avg + SNR:
                        old_power = scan_analiz.get(freq)
                        if old_power and power > old_power:
                            scan_analiz[freq] = power
                        else:
                            scan_analiz[freq] = power
                            count_freq += 1
                        count_find += 1
        
        indx = (indx + 1) % len(run_str)
        if scan_analiz:
            for freq, power in dict(sorted(scan_analiz.items())):
                print(f"{freq} - {power}")
except KeyboardInterrupt:
    sleep(1)
    print('\nstop hackrf.')
    
for freq, power in scan_analiz.items():
    print(freq/1e6, 'Mhz : ', power, 'dB')

# for freq, t_line in history.items():
#     print(freq/1e6, 'Mhz: ')
#     for stamp in t_line:
#         t_value = datetime.fromtimestamp(stamp[0])
#         print('\t', t_value.strftime("%Y-%m-%d %H:%M:%S"), ': ', stamp[1])
