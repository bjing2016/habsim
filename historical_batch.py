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
suffix = ".npy"
data_step = timedelta(hours = 6)

### Load all the data ###

coretime = datetime(y, mo, d, h, mi)
t_var_step = timedelta(hours = t_interval_hours)
time_set_que = [(coretime + i * t_var_step) for i in range(-t_neighbors, t_neighbors + 1)]

for timestamp in time_set_que:
    try:
        load_filecache(timestamp, max_t_h, 6, path, suffix)
    except (IOError, ValueError):
        text = text + "Error loading for " + str(timestamp)

### Prepare the run queue ###
run_queue = list()

ascent_queue = [norm.ppf(i/2.0/(ascent_neighbors+1), loc = ascent_rate, scale = ascent_var) for i in range(1,ascent_neighbors*2+2)]
for rate in ascent_queue:
    for timestamp in time_set_que:
        run_queue.append((timestamp, rate))




print

    '''
    biginfocache = "Timestamp=" + str(argv[2]) + "<br/>" + \
        "Offset=" + str(argv[3]) + "<br/>" + \
            "Time neighbors=" + str(argv[4]) + "<br/>" + \
                "Time interval=" + str(argv[5]) + "<br/>" + \
                    "Lat=" + str(argv[6]) + "<br/>" + \
                        "Lon=" + str(argv[7]) + "<br/>" + \
                            "Ascent rate=" + str(argv[8]) + "<br/>" + \
                            "Ascent rate neighbors=" + str(argv[9]) + "<br/>" + \
                            "Ascent variation=" + str(argv[10]) + "<br/>" + \
                            "Timestep=" + str(argv[11]) + "<br/>" + \
                                "Stop altitude=" + str(argv[12]) + "<br/>"
    
    '''
   
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
    result = result + bigpathcache + part3 + biginfocache + part4 + get_setting_string(sys.argv) + part5
    print(result)
    
main()





"""
infocache = ''' <br/><br/>
    
    Timestamp=''' + str(timestamp) + ", offset=" + str(t_offset_mins) + ", ascent rate=" + str("%.2f" % ascent_rate) + ''' <br/> 
    Time='''+ str(time) + "," + str(lat) + "," + str(lon) + ",alt=" + str(alt) + "<br/>\n"
"""