import torch


acc = torch.load("D:/Downloads/TransPose-main/TransPose/data/datassmpl_file et_work/AMASS/vacc.pt")[0]
acc = acc[1:-1, 5]
acc = torch.round(acc)
print(acc)
