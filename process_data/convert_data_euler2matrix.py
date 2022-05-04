import torch
import numpy as np
from read_data.convert import euler2matrix

euler_path = "../data/dataFrame/data17_euler.pt"
acc_path   = "../data/dataFrame/data17_acc.pt"

matrix_path = '../data/dataFrame/data17_matrix.pt'
acc_glo_path = "../data/dataFrame/data17_acc_glo.pt"

euler = torch.load(euler_path)
acc = torch.load(acc_path)

matrices = []

for frame_eu, frame_acc in zip(euler, acc):
    sensors = []
    acc_global = []
    for sensor_eu, sensor_acc in zip(frame_eu, frame_acc):
        pitch, roll, yaw = int(sensor_eu[0]), int(sensor_eu[1]), int(sensor_eu[2])
        matrix = euler2matrix(pitch, roll, yaw)
        sensors.append(matrix)
    matrices.append(sensors)

matrices = np.array(matrices, dtype=np.float32)
rots = torch.tensor(matrices)
torch.save(rots, matrix_path)

print(rots)
