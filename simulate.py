import numpy as np 
import math
import elev
from datetime import datetime, timedelta, timezone
import math
import bisect
import time

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

### Cache of datacubes and files. ###
### Filecache is in the form (currgefs, modelnumber). ###
filecache = {}

levels = GEFS
suffix = ".npy"
currgefs = "Unavailable"

def refresh():
    f = open("whichgefs")
    s = f.readline()
    f.close()
    if s != currgefs:
        reset()
        currgefs = s

def reset():
    global filecache
    filecache = {}

def get_basetime(simtime):
    return datetime(simtime.year, simtime.month, simtime.day, int(math.floor(simtime.hour / 6) * 6)).replace(tzinfo=timezone.utc)

def get_file(timestamp, model):
    if (timestamp, model) not in filecache.keys():
        name = timestamp.strftime("%Y%m%d%H")
        filecache[(timestamp, model)] = np.load("gefs/" + currgefs + "_" + name + "_" + str(model).zfill(2) + suffix, "r")
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

    pressure_filter = np.array([level_f, 1-level_f]).reshape(1,2,1,1)
    lat_filter = np.array([lat_f, 1-lat_f]).reshape(1,1,2,1)
    lon_filter = np.array([lon_f, 1-lon_f]).reshape(1,1,1,2)
    
    cube1 = data1[:,level_i:level_i+2,lat_i:lat_i+2, lon_i:lon_i+2]
    cube2 = data2[:,level_i:level_i+2,lat_i:lat_i+2, lon_i:lon_i+2]

    u1 = np.sum(cube1[0] * pressure_filter * lat_filter * lon_filter)
    v1 = np.sum(cube1[1] * pressure_filter * lat_filter * lon_filter)

    u2 = np.sum(cube2[0] * pressure_filter * lat_filter * lon_filter)
    v2 = np.sum(cube2[1] * pressure_filter * lat_filter * lon_filter)

    return u1 * time_f + u2 * (1-time_f), v1 * time_f + v2 * (1-time_f)

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
        return pa_to_hpa * math.exp(math.log(1.0 - (altitude/44330.7)) / 0.190266) * 101325.0
    else:
        return pa_to_hpa * math.exp(altitude / -6341.73) * 22632.1 / 0.176481

def lin_to_angular_velocities(lat, lon, u, v): 
    dlat = math.degrees(v / EARTH_RADIUS)
    dlon = math.degrees(u / (EARTH_RADIUS * math.cos(math.radians(lat))))
    return dlat, dlon

def get_wind(simtime, lat, lon, alt, model):
    bounds = get_bounds_and_fractions(lat, lon, alt, simtime)  
    u, v = get_wind_helper(*bounds, model)
    return u, v

def simulate(simtime, lat, lon, rate, step, max_duration, alt, model, coefficient=1, elevation=True):
    
    end = simtime + timedelta(hours=max_duration)
    path = list()
    while True:
        u, v = get_wind(simtime, lat, lon, alt, model)
        path.append((simtime.timestamp(), lat, lon, alt, u, v))
        
        if simtime >= end or (elevation and elev.getElevation(lat, lon) > alt):
            break
        dlat, dlon = lin_to_angular_velocities(lat, lon, u, v)
        alt = alt + step * rate
        lat = lat + dlat * step * coefficient
        lon = lon + dlon * step * coefficient
        simtime = simtime + timedelta(seconds = step)
    
    return path