from hipnuc_module import *
import numpy as np
from convert import euler2matrix
import torch
import time

# 12 variable <=> 12*4 = 48 bytes --> 50 bytes
# 50 fps <=> 50 * 50 = 250 bytes/s
# 60 seconds <=> 15kb/minute


g = 2**10
a_g = 9.81/g


def create_sensors(num_sensors, start):
    sensors = list()
    path = 'config.json'
    baud = 115200
    for i in range(num_sensors):
        port = 'COM' + str(start + i)
        sensor = hipnuc_module(port, baud, path)
        sensors.append(sensor)
        print(i, 'config done')
    return sensors


def close_sensors(sensors):
    for sensor in sensors:
        sensor.close()


def get_data(sensor):
    data = sensor.get_module_data()
    acc = data['acc'][0].values()
    acc = np.array(list(acc))*a_g

    euler = data['euler'][0]
    euler = [euler['Pitch'], euler['Roll'], euler['Yaw']]

    yield acc
    yield euler


def get_data_frame(sensors):
    Acc = []
    Euler = []
    for sensor in sensors:
        acc, euler = get_data(sensor)
        Acc.append(acc)
        Euler.append(euler)
    yield np.array(Acc)
    yield np.array(Euler)


count = 0
if __name__ == '__main__':
    Sensors = create_sensors(num_sensors=6, start=20)
    print('='*80)

    Acc = []
    Euler = []

    t_out = time.time() + 20
    while t_out > time.time():
        acc, euler = get_data_frame(Sensors)
        Acc.append(acc)
        Euler.append(euler)
        count += 1
        print(count)

    name = 'data1' + '_'
    Acc = np.array(Acc, dtype=np.float32)
    Accelerations = torch.tensor(Acc)
    torch.save(Accelerations, name + 'acc.pt')
    print('Accelerations:', Accelerations)

    Euler = np.array(Euler, dtype=np.float32)
    Euler = torch.tensor(Euler)
    torch.save(Euler, name + 'euler.pt')
    print('Euler:', Euler)

    print('='*80)
    print('Total frame:', count)
    close_sensors(Sensors)
    exit()


