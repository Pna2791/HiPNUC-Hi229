import torch
import numpy as np
from read_data.convert import euler2matrix

id = "18"

euler_path = "../data/dataFrame/data" + id + "_euler.pt"
acc_path   = "../data/dataFrame/data" + id + "_acc.pt"

matrix_path = "../data/dataFrame/data" + id + "_matrix.pt"
acc_glo_path = "../data/dataFrame/data" + id + "_acc_glo.pt"

euler = torch.load(euler_path)
acc = torch.load(acc_path)

matrices = []
acc_globals = []

for frame_eu, frame_acc in zip(euler, acc):
    sensors_euler = []
    sensors_acc = []

    for sensor_eu, sensor_acc in zip(frame_eu, frame_acc):
        pitch, roll, yaw = int(sensor_eu[0]), int(sensor_eu[1]), int(sensor_eu[2])
        matrix = euler2matrix(pitch, roll, yaw)
        sensors_euler.append(matrix)
        sensors_acc.append(matrix.dot(sensor_acc))
    matrices.append(sensors_euler)
    acc_globals.append(sensors_acc)

matrices = np.array(matrices, dtype=np.float32)
acc_globals = np.array(acc_globals, dtype=np.float32)

rots = torch.tensor(matrices)
acc_globals = torch.tensor(acc_globals)
torch.save(rots, matrix_path)
torch.save(acc_globals, acc_glo_path)

print(rots)
