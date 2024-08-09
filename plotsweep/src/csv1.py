# This code translates Rust source code to Python. It handles CSV file reading and parsing, and manages records collection.

import csv
from datetime import datetime
from collections import defaultdict

class Record:
    def __init__(self, freq_low, freq_high, freq_step, date, time):
        self.freq_low = freq_low
        self.freq_high = freq_high
        self.freq_step = freq_step
        self.date = date
        self.time = time

class RecordCollection:
    def __init__(self):
        self.freq_low = float('inf')
        self.freq_high = float('-inf')
        self.freq_step = None
        self.records = []
        self.timestamps = {}

def load_records(input_path):
    with open(input_path, mode='r', newline='') as input_file:
        rdr = csv.reader(input_file)
        rc = RecordCollection()

        # Loop through all lines & parse records
        # also keep track of frequency range & unique timestamps to determine final image size
        step = None
        timestamps = set()
        for row in rdr:
            try:
                record = Record(float(row[0]), float(row[1]), float(row[2]), row[3], row[4]) # Adjust indices based on CSV structure
                rc.freq_low = min(rc.freq_low, record.freq_low)
                rc.freq_high = max(rc.freq_high, record.freq_high)
                if step is not None:
                    if abs(step - record.freq_step) > 1e-5:
                        raise ValueError("Frequency step must be constant")
                else:
                    step = record.freq_step
                timestamps.add(datetime.combine(record.date, record.time))
                rc.records.append(record)
            except Exception as e:
                print(f"Warning: {e}")
                break

        rc.freq_step = step

        # Sort the timestamp set & produce a map from timestamp -> row number
        sorted_timestamps = sorted(timestamps)
        rc.timestamps = {timestamp: i for i, timestamp in enumerate(sorted_timestamps)}

        return rc
    
if __name__ == "__main__":
    print(load_records('1.csv'))