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
    #{'id': 0, 'acc': [{'X': 22, 'Y': -84, 'Z': 994}], 'euler': [{'Pitch': -1.1, 'Roll': -4.89, 'Yaw': 40.1}], 'quat': [{'W': 0.938, 'X': -0.037, 'Y': -0.024, 'Z': 0.343}]}

    id = data['id']

    yield id
    yield data

def get_data_frame(sensors):
    dict_data = {}
    acc_list = []
    euler_list = []
    quat_list = []
    for sensor in sensors:
        id, data = get_data(sensor)
        dict_data[id] = data
    for i in range(len(sensors)):
        acc = dict_data[i]['acc'][0].values()
        acc = np.array(list(acc))*a_g
        acc_list.append(acc)

        euler = dict_data[i]['euler'][0].values()
        euler = np.array(list(euler))
        euler_list.append(euler)


        euler = dict_data[i]['euler'][0]
        euler = np.array([euler['Pitch'], euler['Roll'], euler['Yaw']])
        euler_list.append(euler)



        quat = dict_data[i]['quat'][0].values()
        quat = np.array(list(quat))
        quat_list.append(quat)

    yield np.array(acc_list)
    yield np.array(euler_list)
    yield np.array(quat_list)


count = 0
if __name__ == '__main__':
    for i in range(10, 0, -1):
        print('\rStand straight in T-pose and be ready. The celebration will begin after %d seconds.' % i, end='')
        time.sleep(1)
    Sensors = create_sensors(num_sensors=6, start=12)
    print('='*80)

    Acc = []
    Euler = []
    Quat = []

    t_out = time.time() + 60
    while t_out > time.time():
        acc, euler, quat = get_data_frame(Sensors)
        Acc.append(acc)
        Euler.append(euler)
        Quat.append(quat)
        count += 1
        print(count)

    name = 'AEQ1/hanhdong_3' + '_'
    Acc = np.array(Acc, dtype=np.float32)
    Accelerations = torch.tensor(Acc)
    torch.save(Accelerations, name + 'acc.pt')
    print('Accelerations:', Accelerations)

    Euler = np.array(Euler, dtype=np.float32)
    Euler = torch.tensor(Euler)
    torch.save(Euler, name + 'euler.pt')
    print('Euler:', Euler)

    Quat = np.array(Quat, dtype=np.float32)
    Quat = torch.tensor(Quat)
    torch.save(Quat, name + 'quat.pt')
    print('Quat:', Quat)

    print('='*80)
    print('Total frame:', count)
    close_sensors(Sensors)
    exit()
