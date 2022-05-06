from hipnuc_module import *
import numpy as np
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

    #{'id': 0, 'acc': [{'X': -175, 'Y': -481, 'Z': 855}], 'quat': [{'W': 0.964, 'X': -0.249, 'Y': 0.09, 'Z': 0.003}]}

    id = data['id']

    yield id
    yield data

def get_data_frame(sensors):
    dict_data = {}
    acc_list = []
    quat_list = []
    for sensor in sensors:
        id, data = get_data(sensor)
        dict_data[id] = data
    for i in range(len(sensors)):
        acc = dict_data[i]['acc'][0].values()
        acc = np.array(list(acc))*a_g
        acc_list.append(acc)

        quat = dict_data[i]['quat'][0].values()
        quat = np.array(list(quat))
        quat_list.append(quat)

    yield np.array(acc_list)
    yield np.array(quat_list)


count = 0
if __name__ == '__main__':
    Sensors = create_sensors(num_sensors=6, start=20)
    print('='*80)

    Acc = []
    Quat = []

    t_out = time.time() + 10
    while t_out > time.time():
        acc, quat = get_data_frame(Sensors)
        Acc.append(acc)
        Quat.append(quat)
        count += 1
        print(count)

    name = 'Stand' + '_'
    Acc = np.array(Acc, dtype=np.float32)
    Accelerations = torch.tensor(Acc)
    torch.save(Accelerations, name + 'acc.pt')
    print('Accelerations:', Accelerations)

    Quat = np.array(Quat, dtype=np.float32)
    Quat = torch.tensor(Quat)
    torch.save(Quat, name + 'quat.pt')
    print('Quat:', Quat)

    print('='*80)
    print('Total frame:', count)
    close_sensors(Sensors)
    exit()


