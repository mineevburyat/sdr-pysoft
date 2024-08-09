# This code is a translation from Rust to Python, utilizing standard libraries and data handling.

import csv
from datetime import datetime
from typing import List, Dict, Optional, Any

class RecordCollection:
    def __init__(self):
        self.records: List['Record'] = []
        self.timestamps: Dict[datetime, int] = {}
        self.freq_low: int = float('inf')
        self.freq_high: int = 0
        self.freq_step: float = 0.0

class Record:
    def __init__(self, date: datetime, time: datetime, freq_low: int, freq_high: int, freq_step: float, num_samples: int, samples: List[float]):
        self.date = date
        self.time = time
        self.freq_low = freq_low
        self.freq_high = freq_high
        self.freq_step = freq_step
        self.num_samples = num_samples
        self.samples = samples

def load_records(input_path: str) -> RecordCollection:
    rc = RecordCollection()
    step: Optional[float] = None
    timestamps_set = set()
    
    with open(input_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            try:
                date = datetime.strptime(row[0], "%Y-%m-%d").date()
                time = datetime.strptime(row[1], "%H:%M:%S").time()
                freq_low = int(row[2])
                freq_high = int(row[3])
                freq_step = float(row[4])
                num_samples = int(row[5])
                samples = list(map(float, row[6:]))
                
                record = Record(date, time, freq_low, freq_high, freq_step, num_samples, samples)
                
                rc.freq_low = min(rc.freq_low, record.freq_low)
                rc.freq_high = max(rc.freq_high, record.freq_high)
                
                if step is not None:
                    if abs(step - record.freq_step) > 1e-5:
                        raise ValueError("Frequency step must be constant")
                else:
                    step = record.freq_step
                    
                timestamps_set.add(datetime.combine(record.date, record.time))
                rc.records.append(record)
                
            except Exception as e:
                print(f"Warning: {e}")
                break
    
    rc.freq_step = step if step is not None else 0.0
    
    # Sort the timestamp set & produce a map from timestamp -> row number
    sorted_timestamps = sorted(timestamps_set)
    rc.timestamps = {timestamp: index for index, timestamp in enumerate(sorted_timestamps)}
    
    return rc

if __name__ == "__main__":
    for item in load_records('1.csv'):
        print(item)