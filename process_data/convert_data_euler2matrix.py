import torch
import numpy as np
from read_data.convert import euler2matrix

euler_path = "../data/dataFrame/data18_euler.pt"
matrix_path = '../data/dataFrame/data18_matrix.pt'

euler = torch.load(euler_path)


matrices = []

for frame in euler:
    sensors = []
    for sensor in frame:
        pitch, roll, yaw = int(sensor[0]), int(sensor[1]), int(sensor[2])
        matrix = euler2matrix(pitch, roll, yaw)
        sensors.append(matrix)
    matrices.append(sensors)

matrices = np.array(matrices, dtype=np.float32)
rots = torch.tensor(matrices)
torch.save(rots, matrix_path)

print(rots)
