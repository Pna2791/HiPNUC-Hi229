from hipnuc_module import Hipnuc_module
import time
import numpy as np
import sys, torch
from datetime import datetime

class IMUSet:
    def __init__(self, port='COM6', baud=460800):
        path = 'config_wireless.json'
        
        self.sensor_wireless = Hipnuc_module(port, baud, path)
        print(port, 'Config Done!')

        print('='*80)


    def clear(self):
        self.sensor_wireless.module_data_fifo.queue.clear()


    def close(self):
        self.sensor_wireless.close()

    def get_module_data(self):
        data = self.sensor_wireless.get_module_data(1)
        
        id = data['id']
        id = [x[''] for x in id]

        acc = data['acc']
        acc = [np.array([X['X'], X['Y'], X['Z']], dtype=np.float32) for X in acc]

        quat = data['quat']
        quat = [np.array([X['W'], X['X'], X['Y'], X['Z']], dtype=np.float32) for X in quat]

        return (id, acc, quat)




def show(mess):
    sys.stdout.write(f"\r{mess}")
    sys.stdout.flush()

def save_file(data):
    current_datetime = datetime.now()
    timestamp = current_datetime.strftime("%Y-%m-%d %H-%M")
    # timestamp = "root-wireless"
    name = f"../data/AnhPN/{timestamp}.pt"

    torch.save(data, name)
    print()
    print("Saved at:", name)

def extract_data(data):
    acc = data['acc'][0]
    acc = np.array([acc['X'], acc['Y'], acc['Z']], dtype=np.float32)
    quat = data['quat'][0]
    quat = np.array([quat['W'],  quat['X'],  quat['Y'],  quat['Z']], dtype=np.float32)
    return acc, quat


if __name__ == '__main__':
    sensors = IMUSet('COM6')
    print("starting")
    for i in range(-3, 0):
        show(f"Start in {i} seconds")
        time.sleep(1)

    print("Recording")
    data_pack = []
    frames = 900
    sensors.clear()
    for i in range(frames):
        data = sensors.get_module_data()
        data_pack.append(data)
        if i == 0:
            print(data)

        show(f"{i+1} / {frames}")
        if i+1 == 300:
            print()

    save_file(data_pack)
    sensors.close()
