import datetime
from collections import defaultdict, OrderedDict
from typing import List, Dict, Any, Union

class Record:
    def __init__(
        self,
        date: datetime.date = None,
        time: datetime.time = None,
        freq_low: int = None,
        freq_high: int = None,
        freq_step: float = None,
        num_samples: int = None,
        samples: List[float] = [],
    ):
        self.date: datetime.date = date
        self.time: datetime.time = time
        self.freq_low: int = freq_low
        self.freq_high: int = freq_high
        self.freq_step: float = freq_step
        self.num_samples = num_samples
        self.samples = samples

    @staticmethod
    def parse_date(s: str) -> datetime.datetime:
        return datetime.datetime.strptime(s, "%Y-%m-%d")

    @staticmethod
    def parse_time(s: str) -> datetime.time:
        return datetime.time.strptime(s, "%H:%M:%S%.f")

class RecordCollection:
    def __init__(self):
        self.records: List[Record] = []
        self.timestamps: Dict[datetime.datetime, int] = defaultdict(int)
        self.freq_low: int = 0
        self.freq_high: int = 0
        self.freq_step: float = 1.0

    def add_record(self, record: Record):
        """Добавить запись в коллекцию."""
        if not isinstance(record, Record):
            raise TypeError("Неверная запись")
        self.records.append(record)

        timestamp = datetime.datetime.combine(
            record.date,
            record.time,
        )
        self.timestamps[timestamp] += 1

        # Проверка диапазона частот
        if self.freq_low is None or record.freq_low < self.freq_low:
            self.freq_low = record.freq_low
        if record.freq_high > self.freq_high:
            self.freq_high = record.freq_high

        self.update_frequencies()

    def update_frequencies(self):
        """Обновить частоты."""
        self.freq_step = (self.freq_high - self.freq_low) / (len(self.records) - 1)

    @staticmethod
    def load_records(input_path: str) -> "RecordCollection":
        with open(input_path, "r") as file:
            reader = csv.reader(file, delimiter=",")
            rc = RecordCollection()
            for row in reader:
                if not row:
                    continue
                date = datetime.strptime(row[0], "%Y-%m-%d")
                time = datetime.strptime(row[1], "%H:%M:%S%.f")
                freq_low = int(row[2])
                freq_high = int(row[3])
                freq_step = float(row[4])
                num_samples = int(row[5])
                samples = [float(x) for x in row[6:]]
                record = Record(date=date, time=time, freq_low=freq_low, freq_high=freq_high, freq_step=freq_step, num_samples=num_samples, samples=samples)
                rc.add_record(record)
            return rc

    def add_record(self, record: Record):
        """Добавить запись в коллекцию."""
        if not isinstance(record, Record):
            raise TypeError("Неверная запись")
        self.records.append(record)

        timestamp = datetime.combine(
            record.date,
            record.time,
        )
        self.timestamps[timestamp] += 1

        # Проверка диапазона частот
        if self.freq_low is None or record.freq_low < self.freq_low:
            self.freq_low = record.freq_low
        if record.freq_high > self

         if self.freq_low is None or record.freq_low < self.freq_low:
            self.freq_low = record.freq_low

