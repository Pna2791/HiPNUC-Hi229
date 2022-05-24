import numpy as np
import torch

pi = np.pi
cos = np.cos
sin = np.sin

asin = np.arcsin
atan2 = np.arctan2

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


def quat2euler(Qb2n):
    q0 = Qb2n[0]
    q1 = Qb2n[1]
    q2 = Qb2n[2]
    q3 = Qb2n[3]

    roll    = atan2(2*(q0*q1 + q2*q3), 1 - 2*q1*q1 - 2*q2*q2)
    pitch   = asin(2*(q0*q2 - q1*q3))
    yaw     = atan2(2*(q0*q3 + q1*q2), 1 - 2*q2*q2 - 2*q3*q3)

    return roll, pitch, yaw


def get_virtual(quat):
    theta = quat2euler(quat)[2]
    theta += pi/2
    virtual = np.array([[0, 1, 0],
                        [1, 0, 0],
                        [0, 0, 1]])

    matrix = np.array([[cos(theta), -sin(theta), 0],
                       [sin(theta), cos(theta), 0],
                       [0, 0, 1]])
    matrix = matrix.dot(virtual)
    return np.linalg.inv(matrix)
