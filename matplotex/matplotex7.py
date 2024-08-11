import matplotlib.pyplot as plt
from matplotlib.text import Text

plt.figure(figsize=(10,4))
plt.figtext(0, 0.9, 'figtext')
plt.suptitle('title figure')
plt.subplot(121)
plt.title('title subplot')
plt.xlabel('xlabel 1')
plt.ylabel('ylabel 1')
plt.text(0.2, 0.2, 'text1')
plt.annotate('annotate', xy=(0.2, 0.4), xytext=(0.6, 0.7),
arrowprops=dict(facecolor='black', shrink=0.05))
plt.subplot(122)
plt.title('title subplote')
plt.xlabel('xlabel 2')
plt.ylabel('ylabel 2')
plt.text(0.5, 0.5, 'text2')

plt.show()