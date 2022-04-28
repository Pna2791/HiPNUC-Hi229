import serial
import time


# msg = 'AT+ODR=100'   # FPS
# msg = 'AT+EOUT=1'   # OUTPUT
msg = 'AT+INFO=HSI'    # INFO
# msg = 'AT+MODE=1'.       # 9 axis
# msg = 'AT+SETPTL=90,A0,D0'      # 9 limited

wait_time = 2

baud = 115200
num_sensors = 6
com_start = 20


msg += '\r\n'
msg = msg.encode('utf-8')

for i in range(num_sensors):
    port = 'COM' + str(com_start + i)
    Serial = serial.Serial(port, baud, timeout=1)
    Serial.write(msg)
    t_out = time.time() + wait_time
    print(port)
    while t_out > time.time():
        try:
            output = Serial.readline().decode('utf-8')
            if output:
                print(output, end='\0')

        except:
            print('Error')

    Serial.close()
    print()

