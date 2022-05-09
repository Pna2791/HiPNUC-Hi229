import numpy as np
import torch
from read_data.convert import euler2matrix


length = 120

pi = torch.pi
gama = 2*pi
sin = np.sin
cos = np.cos

# Tạo khung data trắng
z_acc = torch.zeros(length, 6, 3, dtype=torch.float32)
z_rot = torch.zeros(length, 6, 3, 3, dtype=torch.float32)
z_rot[:, :] = torch.tensor([[1, 0, 0],
                            [0, 1, 0],
                            [0, 0, 1.]])
euler = [-45, 0, 0]
rot = euler2matrix(euler, unit='D')


rot = torch.tensor(rot)
z_rot[30:, 2] = rot


data_path = "../data/dataFrame/clone_"
acc_sub_path = data_path + 'acc_sub.pt'
matrix_path = data_path + 'matrix.pt'

torch.save(z_acc, acc_sub_path)
torch.save(z_rot, matrix_path)

print("DONE")

