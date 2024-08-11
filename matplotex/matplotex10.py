import matplotlib.pyplot as plt

from PIL import Image
import requests
from io import BytesIO

response = requests.get('https://www.tutorialspoint.com/matplotlib/images/matplotlib_image.jpg')
if response.ok:
    img = Image.open(BytesIO(response.content))
    print(img)
    plt.imshow(img)
    plt.show()
else:
    print('not file')