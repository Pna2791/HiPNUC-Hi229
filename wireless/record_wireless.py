from hipnuc_module import Hipnuc_module
import time
import numpy as np
import sys, torch
from datetime import datetime


# sample = {
#     'GWD': [{'': 0}], 'id': [{'': 0}, {'': 1}, {'': 2}, {'': 3}, {'': 4}, {'': 5}],
#     'timestamp': [{'(s)': 0.0}, {'(s)': 0.0}, {'(s)': 0.0}, {'(s)': 0.0}, {'(s)': 0.0}, {'(s)': 0.0}],
#     'acc': [
#         {'X': 0.0, 'Y': 0.024, 'Z': 1.012}
#         {'X': 0.018, 'Y': 0.045, 'Z': 1.02},
#         {'X': 0.014, 'Y': 0.06, 'Z': 1.017},
#         {'X': 0.016, 'Y': -0.008, 'Z': 1.011},
#         {'X': 0.017, 'Y': 0.019, 'Z': 1.008},
#         {'X': 0.038, 'Y': 0.015, 'Z': 0.992}
#     ],
#     'gyr': [{'X': 0.0, 'Y': 0.2, 'Z': 0.0}, {'X': 0.0, 'Y': 0.0, 'Z': 0.0}, {'X': 0.5, 'Y': 0.0, 'Z': -0.1}, {'X': -0.5, 'Y': 0.3, 'Z': 0.4}, {'X': -0.2, 'Y': -0.1, 'Z': 0.0}, {'X': 0.0, 'Y': 0.1, 'Z': 0.0}],
#     'mag': [{'X': -38, 'Y': 13, 'Z': -1}, {'X': -23, 'Y': 10, 'Z': 2}, {'X': -28, 'Y': -1, 'Z': -3}, {'X': -33, 'Y': -2, 'Z': 7}, {'X': -30, 'Y': -3, 'Z': 0}, {'X': -25, 'Y': 12, 'Z': -1}],
#     'euler': [{'Roll': 1.27, 'Pitch': 0.11, 'Yaw': -64.98}, {'Roll': 2.44, 'Pitch': -1.04, 'Yaw': -41.68}, {'Roll': 3.12, 'Pitch': -0.71, 'Yaw': -48.42}, {'Roll': -1.1, 'Pitch': -0.37, 'Yaw': -18.62}, {'Roll': 1.18, 'Pitch': -0.77, 'Yaw': -96.09}, {'Roll': 1.3, 'Pitch': -2.03, 'Yaw': -48.77}],
#     'quat': [
#         {'W': 0.843, 'X': 0.01, 'Y': -0.005, 'Z': -0.537},
#         {'W': 0.934, 'X': 0.017, 'Y': -0.016, 'Z': -0.355},
#         {'W': 0.912, 'X': 0.022, 'Y': -0.017, 'Z': -0.41},
#         {'W': 0.987, 'X': -0.01, 'Y': -0.002, 'Z': -0.162},
#         {'W': 0.669, 'X': 0.002, 'Y': -0.012, 'Z': -0.744},
#         {'W': 0.911, 'X': 0.003, 'Y': -0.021, 'Z': -0.413}
#     ]
# }

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
        acc = np.array(
            [[X['X'], X['Y'], X['Z']] for X in acc],
            dtype=np.float32
        )
        # acc = [np.array([X['X'], X['Y'], X['Z']], dtype=np.float32) for X in acc]

        quat = data['quat']
        quat = np.array(
            [[X['X'], X['Y'], X['Z'], X['W']] for X in quat],
            dtype=np.float32 
        )
        # quat = [np.array([X['X'], X['Y'], X['Z'], X['W']], dtype=np.float32) for X in quat]

        return (id, acc, quat)




def show(mess):
    sys.stdout.write(f"\r{mess}")
    sys.stdout.flush()

def save_file(data, root):
    current_datetime = datetime.now()
    if root:
        timestamp = "root-wireless_2"
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
    
    frames = 180 if root else 180*30
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
