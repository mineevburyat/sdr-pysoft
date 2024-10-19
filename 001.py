class MyNum:
    def __init__(self, n):
        self.n = n

    def __iadd__(self, other):
        print(type(other))
        if type(other) == int:
            self.n = self.n + other
        elif type(other) == None:
            pass
        else:
            self.n = self.n + other.get_val()
        return self
        
      
    def get_val(self):
        return self.n

    def __str__(self):
        return f"{self.n}"

a = MyNum(3)
b = MyNum(4)
a += 2
b += a
print(a, b)