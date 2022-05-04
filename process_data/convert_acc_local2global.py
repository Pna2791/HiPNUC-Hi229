import numpy as np
import torch



data_path = "D:/Downloads/TransPose-main/TransPose/data/datassmpl_file et_work/AMASS/"

acc_path = data_path + "vacc.pt"
rot_path = data_path + "vrot.pt"
acc_glo_path = data_path + "vacc_glo.pt"

acc_local = torch.load(acc_path)[0]
rot_matrix = torch.load(rot_path)[0]

acc_global = []

for frame_acc, frame_rot in zip(acc_local, rot_matrix):
    sensors_acc = []
    for sensor_acc, sensor_rot in zip(frame_acc, frame_rot):
        sensor_acc_global = sensor_rot.matmul(sensor_acc)
        sensor_acc_global = np.array(sensor_acc_global)
        sensors_acc.append(sensor_acc_global)
    acc_global.append(sensors_acc)

acc_global = np.array(acc_global, dtype=np.float32)
acc_global = torch.tensor(acc_global)

torch.save(acc_global, acc_glo_path)

print(acc_global)
