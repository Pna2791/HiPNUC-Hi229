import torch
import numpy as np
from read_data.convert import euler2matrix, sub_gravity

data_path = "../data/dataFrame/data18_"


acc_path = data_path + "acc.pt"
euler_path = data_path + "euler.pt"

rot_path = data_path + "matrix.pt"
acc_sub_path = data_path + "acc_sub.pt"

acc_local = torch.load(acc_path)
euler = torch.load(euler_path)


acc_sub_frames = []
matrix_frames = []

for frame_acc, frame_euler in zip(acc_local, euler):
    acc_sub_sensors = []
    matrix_sensors = []
    amass_root = np.array([[1, 0, 0],
                           [0, 0, 1],
                           [0, -1, 0.]])

    for acc, euler in zip(frame_acc, frame_euler):
        acc = np.array(acc)
        matrix = euler2matrix(euler)
        sub_acc = sub_gravity(acc, matrix)

        acc_sub_sensors.append(amass_root.dot(sub_acc))
        matrix_sensors.append(amass_root.dot(matrix))

    acc_sub_frames.append(acc_sub_sensors)
    matrix_frames.append(matrix_sensors)

acc_sub_frames = np.array(acc_sub_frames)
matrix_frames = np.array(matrix_frames)

sub_acc = torch.tensor(acc_sub_frames, dtype=torch.float32)
matrices = torch.tensor(matrix_frames, dtype=torch.float32)

torch.save(sub_acc, acc_sub_path)
torch.save(matrices, rot_path)

print("DONE")
