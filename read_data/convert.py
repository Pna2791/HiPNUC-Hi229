import numpy as np

cos = np.cos
sin = np.sin


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


def euler2matrix(pitch, roll, yaw):
    return ch_rotx(pitch).dot(ch_roty(roll)).dot(ch_rotz(yaw))



