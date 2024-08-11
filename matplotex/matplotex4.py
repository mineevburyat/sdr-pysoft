import matplotlib.pyplot as plt
from matplotlib.text import Text

line = plt.plot([1,5,2,8,9], label='label legend', color='red')
print(line)
plt.setp(line, linestyle='--')
ylabel = Text(label='ddsfc', color='green')
print(ylabel)
plt.ylabel(ylabel)
plt.xlabel('dgf', labelpad=-30)
plt.title('effggerg', loc='left')
plt.text(1,5,'dgrfth')
plt.legend()
plt.grid()

plt.show()