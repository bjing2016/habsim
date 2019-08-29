import numpy as np 
import math
import elev
from datetime import datetime, timedelta, timezone
import math
import bisect
import time

# Note: .replace(tzinfo=utc) is needed because we need to call .timestamp

EARTH_RADIUS = float(6.371e6)
DATA_STEP = 6 # hrs

GFSANL = [1, 2, 3, 5, 7, 10, 20, 30, 50, 70,\
          100, 150, 200, 250, 300, 350, 400, 450,\
          500, 550, 600, 650, 700, 750, 800, 850,\
          900, 925, 950, 975, 1000]

GEFS = [10, 20, 30, 50, 70,\
          100, 150, 200, 250, 300, 350, 400, 450,\
          500, 550, 600, 650, 700, 750, 800, 850,\
          900, 925, 950, 975, 1000]

GEFS_ALT = [30782, 26386, 23815, 20576, 18442, \
            16180, 13608, 11784, 10363, 9164, 8117, 7186, 6344, \
            5575, 4865, 4206, 3591, 3012, 2466, 1949, 1457, \
            989, 762, 540, 323, 111]

GEFS_ALT_DIFFS = [-4396, -2571, -3239, -2134, -2262, -2572, -1824, -1421, -1199, \
       -1047,  -931,  -842,  -769,  -710,  -659,  -615,  -579,  -546, \
        -517,  -492,  -468,  -227,  -222,  -217,  -212]

### Cache of datacubes and files. ###
### Filecache is in the form (currgefs, modelnumber). ###
filecache = {}

levels = GEFS
suffix = ".npy"
currgefs = "Unavailable"

mount = True
gefspath = '/gefs/gefs/' if mount else 'gefs/'

def refresh():
    global currgefs
    f = open('/gefs/whichgefs') if mount else open("whichgefs")
    s = f.readline()
    f.close()
    if s != currgefs:
        reset()
        currgefs = s
        return True
    return False

def reset():
    global filecache
    filecache = {}

def get_basetime(simtime):
    return datetime(simtime.year, simtime.month, simtime.day, int(math.floor(simtime.hour / 6) * 6)).replace(tzinfo=timezone.utc)

def get_file(timestamp, model):
    if (timestamp, model) not in filecache.keys():
        name = timestamp.strftime("%Y%m%d%H")
        filecache[(timestamp, model)] = np.load(gefspath + currgefs + "_" + name + "_" + str(model).zfill(2) + suffix, "r")
        print('Loading', timestamp, model)
    return filecache[(timestamp,model)]

### Returns (u, v) given a DATA BLOCK and relative coordinates WITHIN THAT BLOCK ###
### Handles file and cache import ###

def get_wind_helper(lat_res, lon_res, level_res, time_res, model):
    lat_i, lat_f = lat_res
    lon_i, lon_f = lon_res
    level_i, level_f = level_res
    timestamp, time_f = time_res
    
    data1 = get_file(timestamp, model)
    data2 = get_file(timestamp + timedelta(hours=6), model)

    #pressure_filter = np.array([level_f, 1-level_f]).reshape(1,2,1,1)
    pressure_filter = np.array([level_f, 1-level_f]).reshape(1,2)
    lat_filter = np.array([lat_f, 1-lat_f]).reshape(1,1,2,1)
    lon_filter = np.array([lon_f, 1-lon_f]).reshape(1,1,1,2)
    
    cube1 = data1[:,level_i:level_i+2,lat_i:lat_i+2, lon_i:lon_i+2]
    cube2 = data2[:,level_i:level_i+2,lat_i:lat_i+2, lon_i:lon_i+2]

    line1 = np.sum(cube1 * lat_filter * lon_filter, axis=(2,3))
    line2 = np.sum(cube2 * lat_filter * lon_filter, axis=(2,3))

    line_t = line1 * time_f + line2 * (1-time_f)
    du, dv = np.diff(line_t, axis=1).flatten()
    dh = GEFS_ALT_DIFFS[level_i]

    u, v = (line_t * pressure_filter).sum(axis=1).flatten()

    return u, v, du/dh, dv/dh
    '''
    u1 = np.sum(cube1[0] * pressure_filter * lat_filter * lon_filter)
    v1 = np.sum(cube1[1] * pressure_filter * lat_filter * lon_filter)

    u2 = np.sum(cube2[0] * pressure_filter * lat_filter * lon_filter)
    v2 = np.sum(cube2[1] * pressure_filter * lat_filter * lon_filter)

    return u1 * time_f + u2 * (1-time_f), v1 * time_f + v2 * (1-time_f)
    '''
## Array format: array[u,v][Pressure][Lat][Lon] ##
## Currently [lat 90 to -90][lon 0 to 359]

## Note: this returns bounds as array indices ##
###     return lat_res, lon_res, pressure_res, time_res ###
def get_bounds_and_fractions (lat, lon, alt, sim_timestamp):
    lat_res, lon_res, pressure_res = None, None, None
        
    lat = 90 - lat
    lat_res = (int(math.floor(lat)), 1 - lat % 1)

    lon = lon % 360
    lon_res = (int(math.floor(lon)), 1 - lon % 1)
    
    base_timestamp = get_basetime(sim_timestamp)
    offset = sim_timestamp - base_timestamp
    time_f = 1-float(offset.seconds)/(3600*6)
    time_res = (base_timestamp, time_f)
    
    pressure_res = get_pressure_bound(alt)
    return lat_res, lon_res, pressure_res, time_res

def get_pressure_bound(alt):
    pressure = alt_to_hpa(alt)
    pressure_i = bisect.bisect_left(levels, pressure)
    if pressure_i == len(levels):
        return pressure_i-2, 0
    if pressure_i == 0:
        return 0, 1
    return pressure_i - 1, (levels[pressure_i]-pressure)/float(levels[pressure_i] - levels[pressure_i-1])

## Credits to KMarshland ##
def alt_to_hpa(altitude):
    pa_to_hpa = 1.0/100.0
    if altitude < 11000:
        return pa_to_hpa * (1-altitude/44330.7)**5.2558 * 101325
    else:
        return pa_to_hpa * math.exp(altitude / -6341.73) * 128241

def hpa_to_alt(p):
    if p >  226.325:
        return 44330.7 * (1 - (p / 1013.25) ** 0.190266)
    else:
        return -6341.73 * (math.log(p) - 7.1565)

def lin_to_angular_velocities(lat, lon, u, v): 
    dlat = math.degrees(v / EARTH_RADIUS)
    dlon = math.degrees(u / (EARTH_RADIUS * math.cos(math.radians(lat))))
    return dlat, dlon

def get_wind(simtime, lat, lon, alt, model):
    bounds = get_bounds_and_fractions(lat, lon, alt, simtime)  
    u, v, du, dv = get_wind_helper(*bounds, model)
    return u, v, du, dv

def simulate(simtime, lat, lon, rate, step, max_duration, alt, model, coefficient=1, elevation=True):
    
    end = simtime + timedelta(hours=max_duration)
    path = list()
    while True:
        u, v, du, dv = get_wind(simtime, lat, lon, alt, model)
        path.append((simtime.timestamp(), lat, lon, alt, u, v, du, dv))
        if simtime >= end or (elevation and elev.getElevation(lat, lon) > alt):
            break
        dlat, dlon = lin_to_angular_velocities(lat, lon, u, v)
        alt = alt + step * rate
        lat = lat + dlat * step * coefficient
        lon = lon + dlon * step * coefficient
        simtime = simtime + timedelta(seconds = step)
    
    return path

import time
def refreshdaemon():
    while True:
        print('Refresh daemon waking.')
        if refresh(): print('Cache reset by daemon.')
        currdatetime = get_basetime(datetime.strptime(currgefs, "%Y%m%d%H"))
        startdatetime = currdatetime - timedelta(hours = 384)
        enddatetime = currdatetime + timedelta(hours = 384)
        while startdatetime <= enddatetime:
            try: get_file(timestamp, model)
            except: pass
            startdatetime += timedelta(hours=6)
        print('Refresh daemon sleeping.')
        time.sleep(60)

from threading import Thread
Thread(target = refreshdaemon).start()