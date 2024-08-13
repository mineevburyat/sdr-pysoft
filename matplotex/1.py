import matplotlib.pyplot as plt
import math

def f(x):
    return math.cos(x)

x = range(0,10,1)
y = [f(item) for item in x]
plt.subplot()
plt.grid()
plt.plot(x, y)
plt.show()