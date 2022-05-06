from hipnuc_module import *
import time
import numpy as np

g = 2**10
a_g = 9.81/g

count = 0
if __name__ == '__main__':

    HI221GW_A = hipnuc_module('COM20', 115200, './config.json')

    t_end = time.time() + 20
    while t_end > time.time():
        count += 1
        # data = HI221GW_A.get_module_data()['euler']
        data = HI221GW_A.get_module_data()
        # data = list(data)
        # acc = np.array(data)*a_g

        print(data)

        print(count)
    HI221GW_A.close()
    exit()
