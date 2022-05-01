import torch
import numpy as np


arr = np.zeros((3, 4, 5))
tensor = torch.tensor(arr)

for frame in tensor:
    for sensor in frame:
        print(int(sensor))

