import serial

port = 'COM25'
baud = 115200
Serial = serial.Serial(port, baud, timeout=1)

msg = 'AT+ID' + '\r\n'
msg = msg.encode('utf-8')
print(msg)
Serial.write(msg)
for i in range(5):
    try:
        output = Serial.readline().decode('utf-8')
        print('output', output)
    except:
        print("Error")



Serial.close()