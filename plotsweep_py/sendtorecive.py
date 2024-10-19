import serial
import serial.tools
import serial.tools.list_ports

ports = list(serial.tools.list_ports.comports())
for port in ports:
    print(f"Порт: {port.device}")
    print(f"Описание: {port.description}")
    print(f"Производитель: {port.manufacturer}\n")
    
ser = serial.Serial('/dev/ttyUSB0', 57600, timeout=2)
response = ser.readlines()
if response:
    print(response)
ch = 15
if 0 <= ch < 10:
    s = f'0x0{ch}'
    ser.write(s.encode('utf-8'))
elif 10 <= ch < 16:
    ch = ch - 10
    s = f'0x1{ch}'
    ser.write(s.encode('utf-8'))

lines = ser.readlines()
for line in lines:
    print(line)