from hipnuc_module import *
from convert import quat2matrix
import numpy as np
import torch
import time


g = 2**10
a_g = 9.81/g

file_name = 'AEQ1/hanhdong_3' + '_'
TPose_time = 5
data_time = 30

D_virtual = np.array([[0, 1, 0],
                      [0, 0, 1],
                      [1, 0, 0]])


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


def T_Pose(sensors):
    count = 0
    
    acc_mean = np.zeros((6, 3))
    quat_mean = np.zeros((6, 4))
    
    t_out = time.time() + TPose_time
    while t_out > time.time():
        remain = round(t_out - time.time())
        print('\rT-pose stop after %d seconds.' % remain, end='')

        acc, quat = get_data_frame(sensors)
        acc_mean += acc
        quat_mean += quat
        count += 1
    acc_mean /= count
    quat_mean /= count

    matrix_T = np.zeros((6, 3, 3))
    acc_T = np.zeros((6, 3))


    get_virtual(D_virtual, quat_mean[4])

    for i, (acc, quat) in enumerate(zip(acc_mean, quat_mean)):
        matrix = quat2matrix(quat)
        acc_T[i] = matrix.dot(acc)

        matrix = D_virtual.dot(matrix)
        matrix_T[i] = torch.linalg.inv(matrix)

    yield acc_T
    yield matrix_T


def read_data(Sensors, acc_T, matrix_T):
    count = 0
    rotation_matrix = []
    acc_virtual = []

    t_out = time.time() + data_time
    while t_out > time.time():
        acc_sensors, quat_sensors = get_data_frame(Sensors)

        acc_frame = np.zeros((6, 3))
        matrix_frame = np.zeros((6, 3, 3))
        for i, (acc, quat) in enumerate(zip(acc_sensors, quat_sensors)):
            matrix = quat2matrix(quat)
            acc_global = matrix.matmul(acc)
            acc_global -= acc_T[i]

            acc_frame[i] = D_virtual.dot(acc_global)
            matrix_frame[i] = D_virtual.dot(matrix).dot(matrix_T[i])

        rotation_matrix.append(matrix_frame)
        acc_virtual.append(acc_frame)

        count += 1
        print(count)


    # Save Data
    acc_virtual = torch.tensor(acc_virtual, dtype=torch.float32)
    torch.save(acc_virtual, file_name + 'acc_vir.pt')

    rotation_matrix = torch.tensor(rotation_matrix, dtype=torch.float32)
    torch.save(rotation_matrix, file_name + 'matrix.pt')

    print('='*80)
    print('Total frame:', count)


if __name__ == '__main__':
    for i in range(10, 0, -1):
        print('\rStand straight in T-pose and be ready. The celebration will begin after %d seconds.' % i, end='')
        time.sleep(1)
    Sensors = create_sensors(num_sensors=6, start=12)
    print('='*80)

    acc_T, matrix_T = T_Pose(Sensors)
    read_data(Sensors, acc_T, matrix_T)

    close_sensors(Sensors)
    exit()
