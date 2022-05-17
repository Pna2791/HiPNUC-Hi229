import numpy as np
import torch

cos = np.cos
sin = np.sin
g_mean = 9.607779078213017

a_zero = np.array([9.2650782e-03,
                   1.5534239e-02,
                   9.6034727e+00])


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


def euler2matrix(euler, unit='D'):
    if torch.is_tensor(euler):
        euler = euler.tolist()
    pitch, roll, yaw = list(euler)
    if unit == 'D':
        pitch *= np.pi / 180
        roll *= np.pi / 180
        yaw *= np.pi / 180
    return ch_rotz(yaw).dot(ch_roty(roll)).dot(ch_rotx(pitch))


def sub_gravity(acc_local, matrix):
    inverse_matrix = np.linalg.inv(matrix)
    acc_global = matrix.dot(acc_local)
    acc_global -= a_zero
    return acc_local
    return inverse_matrix.dot(acc_global)


def quat2matrix(Qb2n):
    q11 = Qb2n[0]*Qb2n[0]; q12 = Qb2n[0]*Qb2n[1]; q13 = Qb2n[0]*Qb2n[2]; q14 = Qb2n[0]*Qb2n[3]
    q22 = Qb2n[1]*Qb2n[1]; q23 = Qb2n[1]*Qb2n[2]; q24 = Qb2n[1]*Qb2n[3]
    q33 = Qb2n[2]*Qb2n[2]; q34 = Qb2n[2]*Qb2n[3]
    q44 = Qb2n[3]*Qb2n[3]

    matrix = np.array([[ q11+q22-q33-q44,  2*(q23-q14),     2*(q24+q13)],
                       [2*(q23+q14),      q11-q22+q33-q44, 2*(q34-q12)],
                       [2*(q24-q13),      2*(q34+q12),     q11-q22-q33+q44 ]])

    if torch.is_tensor(Qb2n):
        return torch.tensor(matrix, dtype=torch.float32)
    return matrix
