import socket
import numpy as np
from pygame.time import Clock
import src.articulate.math as M
from src.net_ONNX import TransPoseNet_np
from hipnuc_module import *
from utils import normalize_and_concat_np

class IMUSet:
    def __init__(self):
        self.sensors = list()
        g = 2**10
        self.a_g = 9.81/g

    def reset(self):
        for sensor in self.sensors:
            sensor.module_data_fifo.queue.clear()

    def create_sensors(self, num_sensors, start):
        path = 'src\CH_Hi229_ori\config.json'
        baud = 115200
        for i in range(num_sensors):
            port = 'COM' + str(start + i)
            sensor = Hipnuc_module(port, baud, path)
            self.sensors.append(sensor)
            print(port, 'Config Done!')
        print('='*80)

    def close_sensors(self):
        for sensor in self.sensors:
            sensor.close()

    def get_data(self, sensor):
        data = sensor.get_module_data(10)

        #{'id': 0, 'acc': [{'X': -175, 'Y': -481, 'Z': 855}], 'quat': [{'W': 0.964, 'X': -0.249, 'Y': 0.09, 'Z': 0.003}]}
        #{'id': 0, 'acc': [{'X': 22, 'Y': -84, 'Z': 994}], 'euler': [{'Pitch': -1.1, 'Roll': -4.89, 'Yaw': 40.1}], 'quat': [{'W': 0.938, 'X': -0.037, 'Y': -0.024, 'Z': 0.343}]}

        id = data['id']

        acc = data['acc'][0].values()
        acc = np.array(list(acc))*self.a_g

        # euler = data['euler'][0].values()
        # euler = np.array(list(euler))

        quat = data['quat'][0].values()
        quat = np.array(list(quat))

        yield id
        yield acc
        # yield euler
        yield quat

    def get_data_frame(self):
        id_list = list()
        acc_list = list()
        # euler_list = list()
        quat_list = list()

        for sensor in self.sensors:
            # id, acc, euler, quat = self.get_data(sensor)
            id, acc, quat = self.get_data(sensor)
            id_list.append(id)
            acc_list.append(acc)
            # euler_list.append(euler)
            quat_list.append(quat)

        inds = np.array(id_list).argsort()

        yield np.array(acc_list)[inds]
        # yield np.array(euler_list)[inds]
        yield np.array(quat_list)[inds]

    def get_mean_measurement_of_n_second(self, num_seconds):
        count = 0
        t_out = time.time() + num_seconds
        Acc = list()
        # Euler = list()
        Quat = list()
        while t_out > time.time():
            try:
                # acc, euler, quat = self.get_data_frame()
                acc, quat = self.get_data_frame()
                Acc.append(acc)
                # Euler.append(euler)
                Quat.append(quat)
                count += 1
                print(count)
            except:
                print("Error")
                self.close_sensors()
                break

        # Acc = np.array(Acc, dtype=np.float32)
        # Euler = np.array(Euler, dtype=np.float32)
        # Quat = np.array(Quat, dtype=np.float32)

        print('='*80)
        print('Total frame:', count)

        return np.array(Acc, dtype=np.float32).mean(axis=0), np.array(Quat, dtype=np.float32).mean(axis=0)

if __name__ == '__main__':
    imu_set = IMUSet()
    imu_set.create_sensors(num_sensors=6, start=12)

    input('\tFinish.\nWear all imus correctly and press any key.')
    for i in range(10, 0, -1):
        print('\rStand straight in T-pose and be ready. The celebration will begin after %d seconds.' % i, end='')
        time.sleep(1)
    print('\rStand straight in T-pose. Keep the pose for 3 seconds ...', end='')

    acc_glo_mean_np, quat_mean_np = imu_set.get_mean_measurement_of_n_second(num_seconds=3)

    D_virtual_np = np.array([[0, 1, 0],
                             [0, 0, 1],
                             [1, 0, 0]], dtype=np.float32)

    def quat2matrix_np(Qb2n):
        q11 = Qb2n[0]*Qb2n[0]; q12 = Qb2n[0]*Qb2n[1]; q13 = Qb2n[0]*Qb2n[2]; q14 = Qb2n[0]*Qb2n[3]
        q22 = Qb2n[1]*Qb2n[1]; q23 = Qb2n[1]*Qb2n[2]; q24 = Qb2n[1]*Qb2n[3]
        q33 = Qb2n[2]*Qb2n[2]; q34 = Qb2n[2]*Qb2n[3]
        q44 = Qb2n[3]*Qb2n[3]
        Cb2n = np.array([[q11+q22-q33-q44,  2*(q23-q14),     2*(q24+q13)],
                         [2*(q23+q14),      q11-q22+q33-q44, 2*(q34-q12)],
                         [2*(q24-q13),      2*(q34+q12),     q11-q22-q33+q44]])
        return Cb2n

    matrix_T_np = np.zeros((6, 3, 3), dtype=np.float32)
    acc_T_np = np.zeros((6, 3), dtype=np.float32)

    for i, (acc, quat) in enumerate(zip(acc_glo_mean_np, quat_mean_np)):
        matrix = quat2matrix_np(quat)
        acc_T_np[i] = np.matmul(matrix, acc)
        matrix = np.matmul(D_virtual_np, matrix)
        matrix_T_np[i] = np.linalg.inv(matrix)

    # imu start reading
    print('\tFinish.\nStart estimating poses. Press q to quit, r to record motion, s to stop recording.')

    net = TransPoseNet_np()
    # # send Unity
    # server_for_unity = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server_for_unity.bind(('127.0.0.1', 8888))
    # server_for_unity.listen(1)
    # print('Server start. Waiting for unity3d to connect.')
    # conn, addr = server_for_unity.accept()

    clock = Clock()

    # count = 0
    # while True:
    #     clock.tick(60)
    #     try:
    #         acc_sensors, quat_sensors = imu_set.get_data_frame()
    #         count += 1
    #         print(count)
    #     except:
    #         print("Error")
    #         imu_set.close_sensors()
    #         break
    #
    #     rotation_matrices_np = np.zeros((6, 3, 3), dtype=np.float32)
    #     acc_virtual_np = np.zeros((6, 3), dtype=np.float32)
    #
    #     for i, (acc, quat) in enumerate(zip(acc_sensors, quat_sensors)):
    #         matrix = quat2matrix_np(quat)
    #         acc_global_np = np.matmul(matrix, acc)
    #         acc_global_np -= acc_T_np[i]
    #
    #         acc_virtual_np[i] = np.matmul(D_virtual_np, acc_global_np)
    #         rotation_matrices_np[i] = np.matmul(np.matmul(D_virtual_np, matrix), matrix_T_np[i])
    #
    #     data_nn_np = normalize_and_concat_np(acc_virtual_np, rotation_matrices_np)
    #     pose, tran = net.forward_online_np(data_nn_np)
    #     pose = M.rotation_matrix_to_axis_angle_np(pose.reshape(1, 216)).reshape(72)
    #
    #     # send pose
    #     s = ','.join(['%g' % v for v in pose]) + '#' + \
    #         ','.join(['%g' % v for v in tran]) + '$'
    #     conn.send(s.encode('utf8'))
    #
    #     print('\r', 'Sensor FPS:', clock.get_fps(), end='')

    # Poses = []
    # Trans = []
    accs = np.array([])
    quats = np.array([])

    t_out = time.time() + 30
    count = 0
    while t_out > time.time():
        clock.tick(60)
        try:
            acc_sensors, quat_sensors = imu_set.get_data_frame()
            count += 1
            print(count)
        except:
            print("Error")
            imu_set.close_sensors()
            break

        rotation_matrices_np = np.zeros((6, 3, 3), dtype=np.float32)
        acc_virtual_np = np.zeros((6, 3), dtype=np.float32)

        for i, (acc, quat) in enumerate(zip(acc_sensors, quat_sensors)):
            matrix = quat2matrix_np(quat)
            acc_global_np = np.matmul(matrix, acc)
            acc_global_np -= acc_T_np[i]

            acc_virtual_np[i] = np.matmul(D_virtual_np, acc_global_np)
            rotation_matrices_np[i] = np.matmul(np.matmul(D_virtual_np, matrix), matrix_T_np[i])
        #
        # data_nn_np = normalize_and_concat_np(acc_virtual_np, rotation_matrices_np)
        # pose, tran = net.forward_online_np(data_nn_np)
        # # pose = M.rotation_matrix_to_axis_angle_np(pose.reshape(1, 216)).reshape(72)

        # Poses.append(pose)
        # acc.append(acc_sensors)
        accs = np.append(accs, acc_virtual_np).reshape(-1, 6, 3)
        # Trans.append(tran)
        # quat.append(quat_sensors)
        quats = np.append(quats, rotation_matrices_np).reshape(-1, 6, 3, 3)
        # send pose
        # s = ','.join(['%g' % v for v in pose]) + '#' + \
        #     ','.join(['%g' % v for v in tran]) + '$'
        # conn.send(s.encode('utf8'))

        print('\r', 'Sensor FPS:', clock.get_fps(), end='')

    # Poses = np.array(Poses, dtype=np.float32)
    # np.save('Poses.npy', Poses)
    #
    # Trans = np.array(Trans, dtype=np.float32)
    # np.save('Trans.npy', Trans)

    # acc = np.array(acc, dtype=np.float32)
    # np.save('acc.npy', acc)
    #
    # quat = np.array(quat, dtype=np.float32)
    # np.save('quat.npy', quat)

    accs = np.array(accs, dtype=np.float32)
    np.save('acc_virtual_np.npy', accs)

    quats = np.array(quats, dtype=np.float32)
    np.save('rotation_matrices_np.npy', quats)
