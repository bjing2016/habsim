import numpy as np
import math

elevfile = '/gefs/worldelev.npy'
data = np.load(elevfile, 'r')
resolution = 120 ## points per degree

def getElevation(lat, lon):
    x = int(round((lon + 180) * resolution) / resolution)
    y = int(round((90 - lat) * resolution) / resolution)
    try: return max(0, data[x,y])
    except: return 0