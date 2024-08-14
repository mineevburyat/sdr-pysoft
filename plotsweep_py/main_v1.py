from hrfs_read_v4 import RecordCollection, MHZ, kHz
import matplotlib.pyplot as plt

if __name__ == "__main__":
    print('start parsing csv')
    rc = RecordCollection('3.csv')
    print('parsing ok')
    plt.subplot(1, 1, 1)
    plt.title('Power spectr bins')
    plt.xlabel('frequency')
    plt.ylabel('power (dB)')
    # plt.show()
    for sweep in range(len(rc.records_on_sweep)):
        dt, f_min, f_max, f_step, spectr = rc.get_power_spectr(0)
        plt.text(1, 1, dt)
        print(dt, int(f_min), int(f_max - f_step), int(f_step), len(spectr))
        x = range(int(f_min), int(f_max - f_step), int(f_step))
        y = spectr
        plt.plot(x, y)
    plt.show()