from hipnuc_module import *
import time
import numpy as np

g = 2**10
a_g = 9.81/g


cos = np.cos
sin = np.sin


def ch_rotx(theta):
    return np.array([[1, 0, 0],
                     [0, cos(theta), -sin(theta)],
                     [0, sin(theta), cos(theta)]])


def ch_roty(theta):
    return np.array([[cos(theta), 0, sin(theta)],
                     [0, 1, 0],
                     [-sin(theta), 0, cos(theta)]])


def ch_rotz(theta):
    return np.array([[cos(theta), -sin(theta), 0],
                     [sin(theta), cos(theta), 0],
                     [0, 0, 1]])


def euler2matrix(euler, unit='D'):
    pitch, roll, yaw = list(euler)
    if unit == 'D':
        pitch *= np.pi / 180
        roll *= np.pi / 180
        yaw *= np.pi / 180

    matrix = ch_rotz(yaw).dot(ch_roty(roll)).dot(ch_rotx(pitch))
    return matrix


count = 0
if __name__ == '__main__':

    HI221GW_A = hipnuc_module('COM20', 115200, '../config.json')

    t_end = time.time() + 20
    while t_end > time.time():
        count += 1
        data = HI221GW_A.get_module_data()

        acc = data['acc'][0].values()
        acc = np.array(list(acc))*a_g

        euler = data['euler'][0]
        euler = [euler['Pitch'], euler['Roll'], euler['Yaw']]

        matrix = euler2matrix(euler)
        matrix = np.linalg.inv(matrix)
        print(matrix.dot(acc))

        print(count)
    HI221GW_A.close()
    exit()
