import sys
from simulate_py2 import *
from hist_webutils import *
import elev
import math
import numpy as np
from scipy.stats import norm
from datetime import datetime

path = sys.argv[1]
y = int(sys.argv[2])
mo = int(sys.argv[3])
d = int(sys.argv[4])
h = int(sys.argv[5])
mi = int(sys.argv[6])
t_neighbors = int(sys.argv[7])
t_interval_hours = float(sys.argv[8])
lat = float(sys.argv[9])
lon = float(sys.argv[10])
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
points_per_degree = 2
set_constants(points_per_degree, lon_offset)

data_step_hours = 6

suffix = ".npy"
data_step = timedelta(hours = 6)


text_output = ""

markercache = ""

### Load all the data ###

coretime = datetime(y, mo, d, h, mi)
t_var_step = timedelta(hours = t_interval_hours)
time_set_que = [(coretime + i * t_var_step) for i in range(-t_neighbors, t_neighbors + 1)]
tque_with_basetime = list()

for timestamp in time_set_que:
    try:
        basetime = load_filecache(timestamp, max_t_h, data_step_hours, path, suffix)
        tque_with_basetime.append((basetime, timestamp))
    except (IOError, ValueError):
        text_output = text_output + "Error loading for " + str(timestamp)

### Prepare the run queue ###
run_queue = list()

ascent_queue = [norm.ppf(i/2.0/(ascent_neighbors+1), loc = ascent_rate, scale = ascent_var) for i in range(1,ascent_neighbors*2+2)]
for rate in ascent_queue:
    for timestamp in tque_with_basetime:
        run_queue.append((timestamp, rate))

print(part1 + str(lat) + "," + str(lon))
print(part2)


for item in run_queue:
    (basetime, launchtime), rate = item
    rise, fall, coast = simulate(basetime, launchtime, lat, lon, rate, timestep_s, stop_alt, descent_rate, max_t_h)


    last = None
    if len(coast) > 0:
        last = coast[-1]
    elif len(fall) > 0:
        last = fall[-1]
    else:
        last = rise[-1]

    __, lat, lon, __ = last

    print(get_marker_string(lat, lon, "", str(rate) + "," + str(launchtime)))

    text_output = text_output + "Launch " + str(item[0][1]) + " ascent " + str("%.2f" % ascent_rate) + "<br/><br/>\n"
    
    totalpath = rise + fall + coast
    pathcache = ""
    for (time, lat, lon, alt) in totalpath:
        pathcache = pathcache + time.strftime("%H:%M:%S") + "Alt=" + str("%.0f" % alt)+ ",Loc=" + str("%.5f" % lat)+ "," + str("%.5f" % lon)+"<br>\n"
    
    text_output = text_output + pathcache + "<br/><br/>"

    fall.insert(0, rise[-1])
    coast.insert(0, fall[-1])
    print(get_path_string(rise, "#FF0000"))
    print(get_path_string(fall, "#00FF00"))
    print(get_path_string(coast, "#000000"))




print(part3)
print(text_output)
print(part4)
print(get_setting_string(y, mo, d, h, mi, t_neighbors, t_interval_hours, ascent_rate, ascent_var, ascent_neighbors, stop_alt, descent_rate, max_t_h, timestep_s))
print(part5)