import matplotlib.pyplot as plt
import numpy as np


# Линейная зависимость
x = np.linspace(0, 10, 50)
y1 = x
# Квадратичная зависимость
y2 = [i**2 for i in x]

plt.figure(figsize=(15, 10))
plt.subplot(1, 1, 1)
plt.plot(x, y1) # построение графика
plt.title('Зависимости: y1 = x, y2 = x^2') # заголовок
plt.ylabel('y1', fontsize=20) # ось ординат
plt.grid(True) # включение отображение сетки
plt.subplot(3, 1, 2)
plt.plot(x, y2) # построение графика
plt.xlabel('x', fontsize=6) # ось абсцисс
plt.ylabel('y2', fontsize=12) # ось ординат
plt.grid(True) # включение отображение сетки
plt.show()