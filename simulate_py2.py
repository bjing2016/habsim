
import numpy as np 
import math
import sys
from webutils import *
import elev
from scipy.stats import norm

EARTH_RADIUS = 6.371e6

total_seconds = 6 * 60 * 60.0
total_mins = 6 * 60.0

levels = [1, 2, 3, 5, 7, 10, 20, 30, 50, 70,\
          100, 150, 200, 250, 300, 350, 400, 450,\
          500, 550, 600, 650, 700, 750, 800, 850,\
          900, 925, 950, 975, 1000]

cache = {}
filecache = {}

path = ""

def get_file(filename):
    global filecache
    if not filename in filecache.keys():
        filecache[filename] = np.load(filename + ".npy")
    return filecache[filename]

def get_or_fetch(timestamp , lat, lon):
    global cache
    if (timestamp, lat, lon) not in cache.keys():
        data = get_file(path + timestamp)
  
        cache[(timestamp, lat, lon)] = data[:,:,lat:lat+2,lon:lon+2]
   
    return cache[(timestamp,lat,lon)]
    
def get_wind(lat_res, lon_res, level_res, time_res):
    lat_i, lat_f = lat_res
    lon_i, lon_f = lon_res
    level_i, level_f = level_res
    timestamp, time_f = time_res
    get_or_fetch(timestamp, lat_i, lon_i)
    get_or_fetch(get_next_timestamp(timestamp), lat_i, lon_i)
    
    data1 = cache[(timestamp, lat_i, lon_i)]
    data2 = cache[(get_next_timestamp(timestamp)), lat_i, lon_i]

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
def get_bounds_and_fractions (lat, lon, alt, timestamp, t_offset_mins):
    
    lat_res, lon_res, pressure_res = None, None, None
    
    pressure = alt_to_hpa(alt)

    for i in range(len(levels)):
        if pressure<=levels[i]:
            fraction = (levels[i]-pressure)/(levels[i]-levels[i-1])
            pressure_res = (i - 1, fraction)
            break;
        pressure_res = i-1, 0
    
    lat = (lat + 90) * 2
    lat = 360 - lat

    lat_res = (int(math.floor(lat)), 1 - lat % 1)

    
    lon = (lon % 360) * 2;
    lon_res = (int(math.floor(lon)), 1 - lon % 1)

    time_f = 1-t_offset_mins/total_mins

    time_res = (timestamp, time_f)
    return lat_res, lon_res, pressure_res, time_res


## Credits to KMarshland ##
def alt_to_hpa(altitude):
    pa_to_hpa = 1.0/100.0
    if altitude < 11000:
        return pa_to_hpa * math.exp(math.log(1.0 - (altitude/44330.7)) / 0.190266) * 101325.0
    else:
        return pa_to_hpa * math.exp(altitude / -6341.73) * 22632.1 / 0.176481

def get_next_timestamp(timestamp):
    
    timestamp = int(timestamp)
    
    h2 = h1 = timestamp % 100
    d2 = d1 = (timestamp // 100) % 100
    m2 = m1 = (timestamp // 100**2) % 100
    y2 = y1 = (timestamp // 100**3)

    h2 = (h1 + 6) % 24
    if h2 < h1:
        d2 = d1 + 1
        if y1 == 2016:
            threshhold = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        else:
            threshhold = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        d2 = d2 % threshhold[m1 - 1]
        if d2 < d1:
            m2 = (m1 + 1) % 12
            if m2 < m1:
                y2 = y1 + 1
    return str(y2) + str(m2).zfill(2) + str(d2).zfill(2) + str(h2).zfill(2)


def get_prev_timestamp(timestamp):
    
    timestamp = int(timestamp)
    
    h2 = h1 = timestamp % 100
    d2 = d1 = (timestamp // 100) % 100
    m2 = m1 = (timestamp // 100**2) % 100
    y2 = y1 = (timestamp // 100**3)

    h2 = (h1 - 6) % 24
    if h2 > h1:
        d2 = d1 - 1
        if y1 == 2016:
            threshhold = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        else:
            threshhold = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        d2 = d2 % threshhold[m1 - 2]
        if d2 > d1:
            m2 = (m1 - 1) % 12
            if m2 > m1:
                y2 = y1 - 1
    return str(y2) + str(m2).zfill(2) + str(d2).zfill(2) + str(h2).zfill(2)


def lin_to_angular_velocities(lat, lon, u, v): 
    dlat = math.degrees(v / EARTH_RADIUS)
    dlon = math.degrees(u / (EARTH_RADIUS * math.cos(math.radians(lat))))
    return dlat, dlon

def simulate(timestamp, t_offset_mins, slat, slon, ascent_rate, timestep_s, stop_alt):
    
    lat, lon = slat, slon
    alt = elev.getElevation(lat,lon)
    time = 0
    pathcache = list()
    pathcache.append([lat, lon])
    infocache = ''' <br/><br/>
    
    Timestamp=''' + str(timestamp) + ", offset=" + str(t_offset_mins) + ", ascent rate=" + str("%.2f" % ascent_rate) + ''' <br/> 
    Time='''+ str(time) + "," + str(lat) + "," + str(lon) + ",alt=" + str(alt) + "<br/>\n"

    while alt < stop_alt:

        if (t_offset_mins > total_mins):
            t_offset_mins = t_offset_mins - total_mins
            timestamp = get_next_timestamp(timestamp)

        bounds = get_bounds_and_fractions(lat, lon, alt,timestamp, t_offset_mins)
        u, v = get_wind(*bounds)
        dlat, dlon = lin_to_angular_velocities(lat, lon, u, v)
  
        alt = alt + timestep_s * ascent_rate
        lat = lat + dlat * timestep_s
        lon = lon + dlon * timestep_s
        time = time + timestep_s
        t_offset_mins = t_offset_mins + timestep_s / 60.0

        pathcache.append([lat, lon])
        infocache = infocache + "Time="+ str(time) + "," + str("%.4f" % lat) + "," + str("%.4f" % lon) + ",alt=" + str("%.2f" %alt) + "<br/>\n"
    
    return pathcache, infocache, lat, lon
    

def get_run_set(timestamp, t_offset_mins, t_neighbors, t_interval, ascent_rate, ascent_rate_neighbors, ascent_rate_var):
    result = list()
 #   ascent_queue = [i/2/(ascent_rate_neighbors+1) for i in range(1,ascent_rate_neighbors*2+2)]
    time_set_que = [rectify_timestamp(timestamp, t_offset_mins - (t_neighbors * t_interval)*60 + t_interval*60*i) for i in range(2*t_neighbors + 1)]
    ascent_queue = [norm.ppf(i/2.0/(ascent_rate_neighbors+1), loc = ascent_rate, scale = ascent_rate_var) for i in range(1,ascent_rate_neighbors*2+2)]
    #print(ascent_rate_neighbors)
    #for i in range(1,ascent_rate_neighbors*2+2):
    #    print(i)
    #    print(i/2.0/(ascent_rate_neighbors+1))
    #    print(norm.ppf(i/2.0/(ascent_rate_neighbors+1), loc = ascent_rate, scale = ascent_rate_var))
    for rate in ascent_queue:
        for time in time_set_que:
            result.append((time, rate))
    return result

def rectify_timestamp(timestamp, t_offset_mins):
    while t_offset_mins < 0:
        timestamp = get_prev_timestamp(timestamp)
        t_offset_mins = t_offset_mins + total_mins
    while t_offset_mins > total_mins:
        timestamp = get_next_timestamp(timestamp)
        t_offset_mins = t_offset_mins - total_mins
    
    return timestamp, t_offset_mins

def main():
    global path, timestamp
    argv = sys.argv
    path = sys.argv[1]
    timestamp = sys.argv[2]
    bigpathcache = ""
    biginfocache = "Timestamp=" + str(argv[2]) + "<br/>" + \
        "Timestamp=" + str(argv[3]) + "<br/>" + \
            "Time neighbors=" + str(argv[4]) + "<br/>" + \
                "Time interval=" + str(argv[5]) + "<br/>" + \
                    "Lat=" + str(argv[6]) + "<br/>" + \
                        "Lon=" + str(argv[7]) + "<br/>" + \
                            "Ascent rate=" + str(argv[8]) + "<br/>" + \
                            "Ascent rate neighbors=" + str(argv[9]) + "<br/>" + \
                            "Ascent variation=" + str(argv[10]) + "<br/>" + \
                            "Timestep=" + str(argv[11]) + "<br/>" + \
                                "Stop altitude=" + str(argv[12]) + "<br/>"
    
    
   
    run_queue = get_run_set(timestamp, float(argv[3]), int(argv[4]), float(argv[5]), float(argv[8]), int(argv[9]), float(argv[10]))
    
    for item in run_queue:
        try:
            if item[1] < 0:
                pass
            pathcache, infocache, final_lat, final_lon = simulate(item[0][0], item[0][1], float(sys.argv[6]), float(sys.argv[7]), item[1], \
                float(sys.argv[11]), float(argv[12]))
            bigpathcache = bigpathcache + get_path_string(pathcache) + get_marker_string(final_lat, final_lon,"", str(item))
            biginfocache = biginfocache + infocache
        except (IOError, ValueError):
            biginfocache = biginfocache + "<br/>Error:" + str(item) + "<br/>"
    result = part1 + str(sys.argv[6]) + "," + str(sys.argv[7]) + part2
    result = result + bigpathcache + part3 + biginfocache + part4
    print(result)
    
main()


## Usage: simulate.py path timestamp t_offset t_neighbors, t_interval, lat, lon, ascent_rate, ascent_rate_neighbors, ascent_var, timestep_s, stop_alt
 #           0           1       2       3           4           5       6   7       8               9                    10         11          12