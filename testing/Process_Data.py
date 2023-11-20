from hipnuc_module import hipnuc_module
import time
import numpy as np

g = 2**10
a_g = 9.81/g
g_mean = 9.607779078213017

count = 0
if __name__ == '__main__':

    HI221GW_A = hipnuc_module('COM6', 115200, '../config.json')

    t_end = time.time() + 5
    while t_end > time.time():
        count += 1
        data = HI221GW_A.get_module_data()
        print(data)
    HI221GW_A.close()
    exit()
