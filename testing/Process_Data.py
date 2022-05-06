from hipnuc_module import *
from read_data.convert import euler2matrix, sub_gravity
import time
import numpy as np

g = 2**10
a_g = 9.81/g
g_mean = 9.607779078213017

count = 0
if __name__ == '__main__':

    HI221GW_A = hipnuc_module('COM20', 115200, '../config.json')

    t_end = time.time() + 5
    sum = np.array([0, 0, 0], dtype=np.float32)
    while t_end > time.time():
        count += 1
        data = HI221GW_A.get_module_data()
        euler = list(data['euler'][0].values())
        matrix = euler2matrix(euler)
        # inverse = np.linalg.inv(matrix)
        # print(inverse.dot(matrix))
        # print(matrix)

        acc_local = data['acc'][0].values()
        acc_local = np.array(list(acc_local))*a_g
        # acc_local = np.round(acc_local)
        # print(acc_local)

        # acc_global = matrix.dot(acc_local)
        # print(np.round(acc_global), euler)
        # sum += acc_global
        print(sub_gravity(acc_local, matrix), euler)
    # sum /= count
    # print("MEAN", sum)
    HI221GW_A.close()
    exit()
