import numpy as np 

class Frange:
    @staticmethod
    def validate_step(value):
        if value is None:
            return 1.0
        if value == 0:
            raise ValueError('step value not been zero')
        
    @staticmethod
    def validate_start_and_end(start, stop):
        if start < stop:
            return start, stop
        else:
            raise ValueError('start value mast been less then stop')
        
    def __init__(self, *args):
        match len(args):
            case 3:
                self.step = args[2]
                self.start, self.stop = args[0], args[1]
            case 2:
                self.start, self.stop = args[0], args[1]
                self.step = 1.0
            case 1:
                self.step = 1.0
                self.start = 0.0
                self.stop = float(args[0])
            case _:
                raise TypeError(f"range expected 1, 2 or 3 argument, got {len(args)}")

    def get_value(self):
        self._tmp = self.start + self.step / 2
        while self._tmp <= self.stop - self.step / 2:
            yield self._tmp
            self._tmp +=  self.step

if __name__ == '__main__':
    fr = Frange(30000000.0, 70000000.0, 1000000.0)
    count = 0
    for f in fr.get_value():
        print(f)
        count += 1
    print(count)
    print(np.arange(30000000 + 500000, 70000000, 1000000))