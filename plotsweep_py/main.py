import sys
import argparse
from csv2 import load_records  # Assuming csv.py is renamed to csv_module.py
from draw import colormaps, DrawSettings, draw_image  # Assuming draw.py is renamed to draw_module.py

def plot(args):
    input_path = args.INPUT
    output_path = args.OUTPUT
    power_min = float(args.power_min)
    power_max = float(args.power_max)
    colormap = args.colormap

    rc = load_records(input_path)
    print(rc.freq_step)
    maps = colormaps()
    # print(maps)
    settings = DrawSettings(
        colormap=maps[colormap],
        power_min=power_min,
        power_max=power_max,
        hide_axes=args.hide_axes
    )
    draw_image(rc, output_path, settings)

def main():
    parser = argparse.ArgumentParser(description="A tool to plot spectrogram images using hackrf_sweep, soapy_power, or rtl_power output.")
    parser.add_argument("INPUT", help="Input file path")
    parser.add_argument("OUTPUT", help="Output file path")
    parser.add_argument("--colormap", choices=list(colormaps().keys()), default="fire", help="Colormap to use")
    parser.add_argument("--hide-axes", action='store_true', help="Hide axes")
    parser.add_argument("--power-min", type=float, default=-120, help="Minimum power value")
    parser.add_argument("--power-max", type=float, default=-10, help="Maximum power value")

    args = parser.parse_args()
    
    # try:
    #     plot(args)
    # except Exception as err:
    #     print(f"error: {err}")
    #     sys.exit(1)
    
    plot(args)

if __name__ == "__main__":
    # print(colormaps())
    main()

