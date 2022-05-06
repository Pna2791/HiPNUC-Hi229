import serial
import time


msg = 'AT+TRG'
msg += '\r\n'
msg = msg.encode('utf-8')

port = 'COM20'
baud = 115200

Serial = serial.Serial(port, baud)

t_start = time.time()
Serial.write(msg)

echo = Serial.readline()
print(time.time() - t_start)
print(echo.__len__())
# print(echo.decode('utf-8'))
