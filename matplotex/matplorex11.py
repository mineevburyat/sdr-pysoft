import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

fig = plt.figure()


def get_sample():
    return np.random.randint(0, 99, size=1024 )

index = 0
x = get_sample()
img = np.zeros((500,1024))
img[index] = x
im = plt.imshow(img, animated=True)


def updatefig(*args):
    global x, img, index
    # print(img[1:,:])
    img[1:, :] = img[:-1, :]
    img[0] = get_sample()
    im.set_array(img)
    return im,

ani = animation.FuncAnimation(fig, updatefig, interval=50, blit=True)
plt.show()