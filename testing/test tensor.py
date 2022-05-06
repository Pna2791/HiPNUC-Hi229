import torch
import numpy as np

g_mean = 9.607779078213017

# arr = np.zeros((3, 4, 5))
arr = [[1, 2, 3],
       [1, 2, 3]]
arr = np.array(arr)

tensor = torch.tensor(arr)
print(tensor)

# euler = tensor.tolist()
#
#
# print(list(euler))

# for frame in tensor:
#     for sensor in frame:
#         print(int(sensor))

