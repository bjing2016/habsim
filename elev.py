import numpy as np
import math

elevfile = '/gefs/worldelev.npy'
data = np.load(elevfile, 'r')
resolution = 120 ## points per degree

def getElevation(lat, lon):
    x = int(round((lon + 180) * resolution))
    y = int(round((90 - lat) * resolution)) - 1
    try: return max(0, data[y, x])
    except: return 0