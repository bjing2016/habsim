### Run in directory ###


import sys 
import os
from PIL import Image
import numpy as np

files = os.listdir()

for file in files:
    if ".tif" in file:
        name = file[0:-4] + ".npy"
        if os.path.exists(name): continue
        im = Image.open(file)
        array = np.array(im)
        array = np.int16(array)
        print(name)
        np.save(name, array)

