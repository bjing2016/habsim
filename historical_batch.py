import sys
from simulate_py2 import *
from webutils import *
import elev
import math
import numpy as np
from scipy.stats import norm
from datetime import datetime

mypath = sys.argv[1]
y = int(sys.argv[2])
mo = int(sys.argv[3])
d = int(sys.argv[4])
h = int(sys.argv[5])
mi = int(sys.argv[6])
t_neighbors = int(sys.argv[7])
t_interval_hours = float(sys.argv[8])
slat = float(sys.argv[9])
slon = float(sys.argv[10])
ascent_rate = abs(float(sys.argv[11]))
ascent_neighbors = int(sys.argv[12])
ascent_var = float(sys.argv[13])
timestep_s = abs(float(sys.argv[14]))
stop_alt = float(sys.argv[15])
descent_rate = abs(float(sys.argv[16]))
max_t_h = float(sys.argv[17])

## Usage: simulate.py path y mo d h mi t_neighbors, t_interval, lat, lon, ascent_rate, ascent_neighbors, ascent_var, timestep_s, stop_alt, descent_rate, max_t_h
 #           0         1   2  3 4 5  6    7           8           9   10,     11                12              13          14          15     16          17

### Establish global constants ###
lon_offset = 180
lat_start = 90
points_per_degree = 2
hrs = 6
mylvls = GFSANL
suffix = ".npy"

set_constants(points_per_degree, lon_offset, lat_start, hrs, mylvls, mypath, "", suffix)

### data_step_hours = 6

###data_step = timedelta(hours = 6)


text_output = ""

markercache = ""

### Load all the data ###

coretime = datetime(y, mo, d, h, mi)
t_var_step = timedelta(hours = t_interval_hours)
time_set_que = [(coretime + i * t_var_step) for i in range(-t_neighbors, t_neighbors + 1)]

## for timestamp in time_set_que:
##    try:
##       basetime = load_filecache(timestamp, max_t_h, data_step_hours, path, suffix)
##      tque_with_basetime.append((basetime, timestamp))
##   except (IOError, ValueError):
##        text_output = text_output + "Error loading for " + str(timestamp)

### Prepare the run queue ###
run_queue = list()

ascent_queue = [norm.ppf(i/2.0/(ascent_neighbors+1), loc = ascent_rate, scale = ascent_var) for i in range(1,ascent_neighbors*2+2)]
for rate in ascent_queue:
    for timestamp in time_set_que:
        run_queue.append((timestamp, rate))

print(part1 + str(slat) + "," + str(slon))
print(part2)


for item in run_queue:
    launchtime, rate = item
    rise, fall, coast = simulate(launchtime, slat, slon, rate, timestep_s, stop_alt, descent_rate, max_t_h)
    
    last = None
    if len(coast) > 0:
        last = coast[-1]
    elif len(fall) > 0:
        last = fall[-1]
    else:
        last = rise[-1]

    __, mlat, mlon, __, __, __ = last

    print(get_marker_string(mlat, mlon, "", str(rate) + "," + str(launchtime)))

    text_output = text_output + "Launch " + str(launchtime) + " ascent " + str("%.2f" % ascent_rate) + "<br/><br/>\n"
    
    totalpath = rise + fall + coast
    pathcache = ""
    for (time, lat, lon, alt, u, v) in totalpath:
        pathcache = pathcache + time.strftime("%H:%M:%S") + "Alt=" + str("%.0f" % alt)+ ",Loc=" + str("%.5f" % lat)+ "," + str("%.5f" % lon)+ \
             ",u=" + str("%.3f" % u)+ ",v=" + str("%.3f" % v)+  "<br>\n"
    
    text_output = text_output + pathcache + "<br/><br/>"

    fall.insert(0, rise[-1])
    coast.insert(0, fall[-1])
    print(get_path_string(rise, "#FF0000"))
    print(get_path_string(fall, "#008000"))
    print(get_path_string(coast, "#000000"))




print(part3)
print(text_output)
print(part4)
print(get_setting_string(slat, slon, y, mo, d, h, mi, t_neighbors, t_interval_hours, ascent_rate, ascent_var, ascent_neighbors, stop_alt, descent_rate, max_t_h, timestep_s))
print(part5)