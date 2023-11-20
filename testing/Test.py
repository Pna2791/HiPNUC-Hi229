import serial, torch, time

if __name__ == "__main__":
    ser = serial.Serial("COM6", baudrate=115200, timeout=None)
    t_out = time.time() + 5
    while time.time() < t_out:
        try:
            if ser.in_waiting:
                data = ser.read(ser.in_waiting)
                print(data)
                print(data.decode())
        except Exception as e:
            print(e)
    ser.close()