import numpy as np
import torch


z_acc = torch.zeros(300, 6, 3, dtype=torch.float32)
z_rot = torch.zeros(300, 6, 3, 3, dtype=torch.float32)
z_rot[:, :] = torch.tensor([[1, 0, 0],
                            [0, 1, 0],
                            [0, 0, 1.]])


pi = torch.pi
gama = 2*pi
sin = np.sin
cos = np.cos

def ch_rotz(theta):
    return np.array([[cos(theta), -sin(theta), 0],
                     [sin(theta), cos(theta), 0],
                     [0, 0, 1]])

def omega_t(t):
    if t<31:
        return gama*t/60
    return gama - gama*t/60

def alpha_t(t):
    if t<31:
        return gama * t**2 / 7200
    return pi * (t/30 - 0.5 - t**2 / 3600)


# Global

def acc_t(t):
    if t<31:
        return 0.7 * pi
    return -0.7*pi

acc = []
rot = []
for i in range(1, 61):
    alpha = alpha_t(i)
    a = acc_t(i)
    a_x = -sin(alpha) * a
    a_y = -cos(alpha) * a
    acc_global = np.array([a_x, a_y, 0])
    matrix = ch_rotz(-alpha)

    # acc.append(np.linalg.inv(matrix).dot(acc_global))
    acc.append(acc_global)
    rot.append(matrix)

acc = torch.tensor(np.array(acc))
rot = torch.tensor(np.array(rot))

z_acc[60:120, 0, :] = acc
z_rot[60:120, 0, :, :] = rot
z_rot[120:, 0, :, :] = rot[59]


data_path = "../data/dataFrame/clone_"
acc_sub_path = data_path + 'acc_sub.pt'
matrix_path = data_path + 'matrix.pt'

torch.save(z_acc, acc_sub_path)
torch.save(z_rot, matrix_path)

print("DONE")
