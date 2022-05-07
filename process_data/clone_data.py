import numpy as np
import torch

length = 120


# Tạo khung data trắng
z_acc = torch.zeros(length, 6, 3, dtype=torch.float32)
z_rot = torch.zeros(length, 6, 3, 3, dtype=torch.float32)
z_rot[:, :] = torch.tensor([[1, 0, 0],
                            [0, 1, 0],
                            [0, 0, 1.]])


pi = torch.pi
gama = 2*pi
sin = np.sin
cos = np.cos


def ch_rotx(theta):
    return np.array([[1, 0, 0],
                     [0, cos(theta), -sin(theta)],
                     [0, sin(theta), cos(theta)]])


def ch_roty(theta):
    return np.array([[cos(theta), 0, sin(theta)],
                     [0, 1, 0],
                     [-sin(theta), 0, cos(theta)]])


def ch_rotz(theta):
    return np.array([[cos(theta), -sin(theta), 0],
                     [sin(theta), cos(theta), 0],
                     [0, 0, 1]])


def euler2matrix(euler):
    if torch.is_tensor(euler):
        euler = euler.tolist()
    pitch, roll, yaw = list(euler)
    return ch_rotz(yaw).dot(ch_roty(roll)).dot(ch_rotx(pitch))


# các công thức tính theo thời gian
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
        return 0.8 * pi
    return -0.8*pi


# Tạo ra các dữ liệu ảo
acc = []
rot = []
for i in range(1, 61):
    alpha = -alpha_t(i)
    a = -acc_t(i)
    a_x = -sin(alpha) * a
    a_y = cos(alpha) * a

    # điền các số liệu cho gia tốc và euler
    acc_global = np.array([0, a, 0])
    euler = [0, 0, -pi/2]
    matrix = euler2matrix(euler)
    # print(alpha*180/pi)

    # Chuyển gia tốc sang local hoặc lưu global
    # acc.append(np.linalg.inv(matrix).dot(acc_global))
    acc.append(acc_global)
    rot.append(matrix)

acc = torch.tensor(np.array(acc))
rot = torch.tensor(np.array(rot))

# thêm các giá trị vừa tạo vào frame 30 - 90
start_frame = 30
# z_acc[start_frame:start_frame+60, 0, :] = acc
z_rot[start_frame:start_frame+60, 0, :, :] = rot
z_rot[start_frame+60:, 0, :, :] = rot[59]


data_path = "../data/dataFrame/clone_"
acc_sub_path = data_path + 'acc_sub.pt'
matrix_path = data_path + 'matrix.pt'

torch.save(z_acc, acc_sub_path)
torch.save(z_rot, matrix_path)

print("DONE")

