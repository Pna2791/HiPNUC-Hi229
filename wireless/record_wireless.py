from hipnuc_module import Hipnuc_module
import time
import numpy as np
import sys, torch
from datetime import datetime

class IMUSet:
    def __init__(self, port='COM6', baud=460800):
        path = 'config_wireless.json'
        self.first = True
        
        self.sensor_wireless = Hipnuc_module(port, baud, path)
        print(port, 'Config Done!')

        print('='*80)


    def clear(self):
        self.sensor_wireless.module_data_fifo.queue.clear()


    def close(self):
        self.sensor_wireless.close()

    def get_module_data(self):
        data = self.sensor_wireless.get_module_data(1)
        if self.first:
            print(data)
            self.first = False
        
        id = data['id']
        id = [x[''] for x in id]

        acc = data['acc']
        acc = [np.array([X['X'], X['Y'], X['Z']], dtype=np.float32) for X in acc]

        quat = data['quat']
        quat = [np.array([X['X'], X['Y'], X['Z'], X['W']], dtype=np.float32) for X in quat]

        return (id, acc, quat)




def show(mess):
    sys.stdout.write(f"\r{mess}")
    sys.stdout.flush()

def save_file(data, root):
    current_datetime = datetime.now()
    if root:
        timestamp = "root-wireless_1"
    else:
        timestamp = current_datetime.strftime("%Y-%m-%d %H-%M")
    name = f"E:/Mocap/Hi229/data/AnhPN/{timestamp}.pt"
    
    if not root:
        file = open("../../Hi229/data/AnhPN/last_wireless.txt", "w")
        file.write(name)
        file.close()

    torch.save(data, name)
    print()
    print("Saved at:", name)


if __name__ == '__main__':
    sensors = IMUSet('COM6')
    print("starting")
    for i in range(-3, 0):
        show(f"Start in {i} seconds")
        time.sleep(1)

    root = True
    # root = False
    print("Recording")
    data_pack = []
    
    frames = 180 if root else 180*20
    sensors.clear()
    for i in range(frames):
        data = sensors.get_module_data()
        data_pack.append(data)
        if i == 0:
            print(data)

        show(f"{i+1} / {frames}")
        if i+1 == 300:
            print()

    save_file(data_pack, root)
    sensors.close()
