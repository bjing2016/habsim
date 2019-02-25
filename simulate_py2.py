import numpy as np 
import math
import elev
from datetime import datetime, timedelta
import math
from scipy.stats import norm

EARTH_RADIUS = 6.371e6

levels = [1, 2, 3, 5, 7, 10, 20, 30, 50, 70,\
          100, 150, 200, 250, 300, 350, 400, 450,\
          500, 550, 600, 650, 700, 750, 800, 850,\
          900, 925, 950, 975, 1000]

### Will be populate by get_filecache ###
data_step = None

### Client must directly populate via the method below ###
points_per_degree = None
lon_offset = None

def set_constants(ppd, lo):
    global points_per_degree
    global lon_offset
    points_per_degree = ppd
    lon_offset = lo


### Cache of datacubes and files. ###
### Must be reset for each ensemble member ##

### Filecache is in the form (datetime). ###
filecache = {}

### Cache is in the form (datetime, lower_lat_index, lower_lon_index) ###
datacache = {}

### Extracts datacube from cache ###
def get_or_fetch(timestamp , lat_index, lon_index):
    global datacache
    
    if (timestamp, lat_index, lon_index) not in datacache.keys():
        data = filecache[timestamp]
        datacache[(timestamp, lat_index, lon_index)] = data[:,:,lat_index:lat_index+2,lon_index:lon_index+2]
   
    return datacache[(timestamp,lat_index,lon_index)]

### Returns (u, v) given a DATA BLOCK and relative coordinates WITHIN THAT BLOCK ###
### Handles file and cache import ###

def get_wind(lat_res, lon_res, level_res, time_res):
    lat_i, lat_f = lat_res
    lon_i, lon_f = lon_res
    level_i, level_f = level_res
    timestamp, time_f = time_res
    get_or_fetch(timestamp, lat_i, lon_i)
    get_or_fetch((timestamp + data_step), lat_i, lon_i)
    
    data1 = datacache[(timestamp, lat_i, lon_i)]
    data2 = datacache[(timestamp + data_step), lat_i, lon_i]

    pressure_filter = np.array([level_f, 1-level_f]).reshape(1,2,1,1)
    lat_filter = np.array([lat_f, 1-lat_f]).reshape(1,1,2,1)
    lon_filter = np.array([lon_f, 1-lon_f]).reshape(1,1,1,2)
    
    cube1 = data1[:,level_i:level_i+2]
    cube2 = data2[:,level_i:level_i+2]

    u1 = np.sum(cube1[0] * pressure_filter * lat_filter * lon_filter)
    v1 = np.sum(cube1[1] * pressure_filter * lat_filter * lon_filter)

    u2 = np.sum(cube2[0] * pressure_filter * lat_filter * lon_filter)
    v2 = np.sum(cube2[1] * pressure_filter * lat_filter * lon_filter)

    return u1 * time_f + u2 * (1-time_f), v1 * time_f + v2 * (1-time_f)

## Array format: array[u,v][Pressure][Lat][Lon] ##
## Currently [lat 90 to -90][lon 0 to 395.5]

## Note: this returns bounds as array indices ##
###     return lat_res, lon_res, pressure_res, time_res ###
def get_bounds_and_fractions (lat, lon, alt, base_timestamp, sim_timestamp):
    lat_res, lon_res, pressure_res = None, None, None

    pressure = alt_to_hpa(alt)
    for i in range(len(levels)):
        if pressure<=levels[i]:
            fraction = (levels[i]-pressure)/(levels[i]-levels[i-1])
            pressure_res = (i - 1, fraction)
            break;
        pressure_res = i-1, 0
    
    lat = (lat + 90) * points_per_degree
    lat = 360 - lat
    lat_res = (int(math.floor(lat)), 1 - lat % 1)

    lon = ((lon % 360) - lon_offset) * points_per_degree
    lon_res = (int(math.floor(lon)), 1 - lon % 1)
    offset = sim_timestamp - base_timestamp
    if offset >= data_step:
        base_timestamp = base_timestamp + data_step
        offset = offset - data_step

    time_f = 1-offset.seconds/data_step.seconds

    time_res = (base_timestamp, time_f)

    return lat_res, lon_res, pressure_res, time_res


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

def single_step(basetime, simtime, lat, lon, alt, ascent_rate, step):
    bounds = get_bounds_and_fractions(lat, lon, alt, basetime, simtime)
    
    basetime = bounds[3][0]
    
    u, v = get_wind(*bounds)
    dlat, dlon = lin_to_angular_velocities(lat, lon, u, v)
    
    
    alt = alt + step * ascent_rate
    lat = lat + dlat * step
    lon = lon + dlon * step
    simtime = simtime + timedelta(seconds = step)

    return basetime, simtime, lat, lon, alt

def simulate(basetime, starttime, slat, slon, ascent_rate, step, stop_alt, descent_rate, max_duration):
    

    lat, lon = slat, slon
    alt = elev.getElevation(lat,lon)
    simtime = starttime

    end = starttime + timedelta(hours=max_duration)

    pathcache = (list(), list(), list())
    pathcache[0].append((starttime, lat, lon, alt))
    
    while alt < stop_alt:
        basetime, simtime, lat, lon, alt = single_step(basetime, simtime, lat, lon, alt, ascent_rate, step)
        pathcache[0].append((simtime, lat, lon, alt))

    while simtime < end:
        index = 1
        basetime, simtime, lat, lon, alt = single_step(basetime, simtime, lat, lon, alt, -descent_rate, step)
        pathcache[index].append((simtime, lat, lon, alt))
        groundelev = elev.getElevation(lat, lon)
        if alt < groundelev:
            if groundelev <= 0:
                descent_rate = 0
                index = 2
            else:
                break

    return pathcache

def load_filecache(simtime, duration_hours, step_hours, path, suffix):
    global filecache
    global data_step
    data_step = timedelta(hours = step_hours)
    y, mo, d, h = simtime.year, simtime.month, simtime.day, simtime.hour

    basetime = datetime(y, mo, d,  step_hours * int(h / step_hours))
    endtime = basetime + int(math.ceil(duration_hours / step_hours) + 1) * data_step
    loadtime = basetime
    while loadtime <= endtime:
        if loadtime not in filecache.keys():
            name = loadtime.strftime("%Y%m%d%H")
            filecache[loadtime] = np.load(path + "/" + name + suffix)
            loadtime = loadtime + data_step
    
    return basetime