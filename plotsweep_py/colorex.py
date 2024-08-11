import matplotlib.pyplot as plt
import numpy as np


x = np.linspace(0, 10, 50)
# print(x, len(x))
y = x**2
y2 = x
plt.title('Линейная зависимость y = x') # заголовок
plt.xlabel('x') # ось абсцисс
plt.ylabel('f(x)') # ось ординат
plt.grid() # включение отображение сетки
plt.plot(x, y, 'r--') # построение графика
plt.plot(x, y2)
plt.show()