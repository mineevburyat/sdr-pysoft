import numpy as np
import matplotlib.pyplot as plt
import time

fig, ax = plt.subplots()

x = np.arange(-2*np.pi, 2*np.pi, 0.1)
y = np.cos(x)
 
line, = ax.plot(x, y)
plt.ion()
plt.show()
for delay in np.arange(0, np.pi, 0.1):
    y = np.cos(x+delay)
 
    plt.clf()
    plt.plot(x, y)
    plt.draw()
    plt.gcf().canvas.flush_events()
 
    time.sleep(0.02)