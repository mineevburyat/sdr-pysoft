import serial.tools.list_ports as list_ports
import serial

def get_list_sport():
    return [port.device for port in list(list_ports.comports())]

class Reciver():
    def __init__(self, portname='/dev/ttyUSB0'):
        self.port = serial.Serial(portname, 57600, timeout=2)
        self.current_chan = None
        print('Предупреждение! Установите приемник на канал 0!')
    
    def readlines(self):
        lines = self.port.readlines()
        if lines is None:
            lines = []
        lines = [line.strip().decode('utf-8') for line in lines]
        return lines
                
    def set_channel(self, chan):
        if self.current_chan == chan:
            return True
        if 0 <= chan < 10:
            s = f'0x0{chan}'
            self.port.write(s.encode('utf-8'))
        elif 10 <= chan < 16:
            chan = chan - 10
            s = f'0x1{chan}'
            self.port.write(s.encode('utf-8'))
        else:
            raise ValueError("Канал в диапазоне от 0 до 16!")
        lines = self.readlines()
        if lines is None:
            raise ValueError("Ошибка! Не получен ответ от приемника!")
        if len(lines) == 2:
            if lines[0] == "Ok" and int(lines[1]) == chan:
                self.current_chan = chan
                return True
        elif len(lines) == 1:
            if lines[0] == 'Error':
                return False
        else:
            raise ValueError("Ошибка! Неожиданный ответ!")

if __name__ == "__main__":
    # for port in get_list_sport():
    #     print(f"Порт: {port}")
    recv = Reciver(portname='/dev/ttyUSB0')
    
    while True:
        lines = recv.readlines()
        for line in lines:
            print(line)
        keyboard = input("введите канал приемника: (или q для выхода)")
        if keyboard.isdigit():
            ch = int(keyboard)
        else:
            break
        if recv.set_channel(ch):
            print(f"Установлен канал {recv.current_chan}")
    

