# Here's the translated Python code:

import datetime
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.dates import DateFormatter
import colorcet as cc

class DrawSettings:
    def __init__(self, colormap, power_min, power_max, hide_axes):
        self.colormap = colormap
        self.power_min = power_min
        self.power_max = power_max
        self.hide_axes = hide_axes

def colormaps():
    return {
        "fire": cc.cm_n.fire,
        "grey": cc.cm_n.gray,
        "inferno": cc.cm_n.kbc,
        "plasma": cc.cm_n.gouldian
    }

def build_lut(colormap):
    return [colormap(i / 65535) for i in range(65536)]

def draw_image(record_collection, output_path, settings):
    rc = record_collection
    width = int((rc.freq_high - rc.freq_low) / rc.freq_step) + 1
    height = len(rc.timestamps)
    print(rc.freq_high, rc.freq_low, rc.freq_step, width, height)
    vertical_margin = 10

    if settings.hide_axes:
        padding = (0, 0)
    else:
        padding = (150, 50 + vertical_margin)

    fig, ax = plt.subplots(figsize=((width+padding[0]*2)/100, (height+padding[1]*2)/100), dpi=100)
    ts_min = min(rc.timestamps.keys())
    ts_max = max(rc.timestamps.keys())
    
    if not settings.hide_axes:
        ax.set_ylim(ts_max, ts_min)  # Reversed y-axis
        ax.set_xlim(rc.freq_low, rc.freq_high)
        ax.set_xlabel("Frequency (MHz)")
        ax.xaxis.set_major_formatter(lambda x, pos: f"{x/1e6:.0f}")
        ax.yaxis.set_major_formatter(DateFormatter("%Y-%m-%d %H:%M:%S"))
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    else:
        ax.axis('off')

    lut = build_lut(settings.colormap)
    # print(len(settings.colormap))
    # print(lut)
    range_val = settings.power_max - settings.power_min
    scale = (len(lut) - 1) / range_val
    # print(scale)
    img = np.zeros((height, width, 3))
    print(rc.timestamps)
    for record in rc.records:
        # print(record)
        x = int(((record.freq_low - rc.freq_low) / rc.freq_step) + 0.5)
        # print(x)
        y = rc.timestamps[datetime.datetime.combine(record.date, record.time)]
        # print(record.samples)
        for i, sample in enumerate(record.samples):
            # print(i, sample)
            scaled_pixel = (sample - settings.power_min) * scale
            index = int(np.clip(scaled_pixel, 0, len(lut) - 1))
            img[y, x + i] = lut[index][:3]  # Exclude alpha channel
    # print(img, len(img[0]))
    ax.imshow(img, extent=[rc.freq_low, rc.freq_high, ts_max, ts_min], aspect='auto')

    plt.tight_layout()
    plt.savefig(output_path, dpi=100, bbox_inches='tight')
    plt.close()

# Note: The RecordCollection class and other supporting classes/functions are not provided in the original code,
# so they are not included in this translation. You may need to implement them separately.


# This Python code provides an equivalent functionality to the Rust code you provided. Here are some notes on the translation:

# 1. We use `matplotlib` for plotting instead of `plotters`.
# 2. The `colorous` library is replaced with `colorcet`, which provides similar color maps.
# 3. The `DrawSettings` class is implemented as a simple Python class.
# 4. The `colormaps` function returns a dictionary of color maps from `colorcet`.
# 5. The `build_lut` function creates a lookup table for colors.
# 6. The `draw_image` function is the main function that creates the plot. It uses `matplotlib` to create a figure and axis, then plots the data as an image.
# 7. Error handling is not explicitly implemented in this translation. You may want to add try-except blocks as needed.
# 8. The `RecordCollection` class and its properties (like `freq_high`, `freq_low`, etc.) are assumed to exist. You'll need to implement this class separately.

# Remember to install the required libraries (`matplotlib`, `numpy`, `colorcet`) before running this code.

