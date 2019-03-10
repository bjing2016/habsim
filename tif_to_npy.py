### Run in directory ###


import sys 
import os
from PIL import Image
import numpy as np

files = os.listdir()

for file in files:
    if ".tif" in file:
        im = Image.open(file)
        array = np.array(im)
        name = file[0:-4] + ".npy"
        np.save(name, array)

