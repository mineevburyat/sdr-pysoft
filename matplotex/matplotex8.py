import matplotlib.pyplot as plt
import numpy as np
np.random.seed(123)
vals = np.zeros((800, 1024))
plt.imshow(vals)

plt.colorbar()
plt.show()