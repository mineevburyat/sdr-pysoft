import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


height = 500
width = 1024
fig = plt.figure()


def f():
    line = np.random.randint(1, 100, size=width, dtype=int)
    line[100:112] = 99
    return  line


img = np.zeros((height, width), dtype=int)
img[0] = f()


im = plt.imshow(img, animated=True)


def updatefig(*args):
    global img, im
    img[1:, : ] = img[:-1,:]
    # print(img)
    img[0] = f()
    # print(img[0])
    im.set_array(img)
    return im,

ani = animation.FuncAnimation(fig, updatefig, interval=50, blit=True)
plt.show()