import numpy as np 
import math
import elev
from datetime import datetime, timedelta, timezone
import math
import bisect
import time
from windfile import WindFile

# Note: .replace(tzinfo=utc) is needed because we need to call .timestamp

EARTH_RADIUS = float(6.371e6)
DATA_STEP = 6 # hrs

### Cache of datacubes and files. ###
### Filecache is in the form (timestamp, modelnumber). ###
filecache = {}

currgefs = "Unavailable"

mount = True
gefspath = '/gefs/gefs/' if mount else 'gefs/'

def refresh():
    global currgefs
    f = open('/gefs/whichgefs') if mount else open("whichgefs")
    s = f.readline()
    f.close()
    if s != currgefs:
        currgefs = s
        reset()
        return True
    return False

# opens and stores 20 windfiles in filecache
def reset():
    global filecache
    filecache = []
    for i in range(1, 21):
        filecache.append(WindFile(f'{gefspath}{currgefs}_{str(i).zfill(2)}.npz'))

def lin_to_angular_velocities(lat, lon, u, v): 
    dlat = math.degrees(v / EARTH_RADIUS)
    dlon = math.degrees(u / (EARTH_RADIUS * math.cos(math.radians(lat))))
    return dlat, dlon

def simulate(simtime, lat, lon, rate, step, max_duration, alt, model, coefficient=1, elevation=True):
    end = simtime + timedelta(hours=max_duration)
    path = list()

    while True:
        u, v = filecache[model-1].get(lat, lon, alt, simtime)
        path.append((simtime.timestamp(), lat, lon, alt, u, v, 0, 0))
        if simtime >= end or (elevation and elev.getElevation(lat, lon) > alt):
            break
        dlat, dlon = lin_to_angular_velocities(lat, lon, u, v)
        alt = alt + step * rate
        lat = lat + dlat * step * coefficient
        lon = lon + dlon * step * coefficient
        simtime = simtime + timedelta(seconds = step)
    
    return path
