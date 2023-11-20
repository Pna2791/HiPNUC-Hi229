from hipnuc_module import *
import time
import numpy as np
import sys, torch
from datetime import datetime

g = 2**10
a_g = 9.81/g
print("a_g:", a_g)

def show(mess):
    sys.stdout.write(f"\r{mess}")
    sys.stdout.flush()

def save_file(data):
    current_datetime = datetime.now()
    timestamp = current_datetime.strftime("%Y-%m-%d %H-%M")
    timestamp = "root"
    name = f"../Hi229/data/AnhPN/{timestamp}.pt"

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
    HI221GW_A = hipnuc_module('COM5', 115200, './config.json')
    print("starting")
    # for i in range(-3, 0):
    #     show(f"Start in {i} seconds")
    #     time.sleep(1)

    print("Recording")
    data_pack = []
    frames = 180
    HI221GW_A.module_data_fifo.queue.clear()
    for i in range(frames):
        data = HI221GW_A.get_module_data()
        acc, quat = extract_data(data)
        data_pack.append((acc, quat))

        show(f"{i+1} / {frames}")
        if i == 240:
            print()

    save_file(data_pack)
    HI221GW_A.close()
