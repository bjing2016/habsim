import sys
from simulate_py2 import *
from webutils import *
import elev
import math
import os
import numpy as np
from datetime import datetime, timedelta


EAST = 1
WEST = 0

spaceshot_locations = {
    ("LostCoast", 40.44, -124.4, WEST),
    ("BigSur", 36.305, -121.9, WEST),
    ("PointBlanco", 42.84, -124.55, WEST),
    ("Tillamook", 45.4, -123.95, WEST),
    ("Olympic", 48.3, -124.6, WEST),
    ("SouthTX", 27, -97.38, EAST),
    ("Georgia", 30.9, -81.41, EAST)
    
### Brownsville and Georgia also ###

}

### How far west does the balloon need to go?
### How long does it need to stay there?
SPACESHOT_DISTANCE_THRESHHOLD = 22 ## km
SPACESHOT_TIME_THRESHHOLD = .5 ## hours
SPACESHOT_TIMESTEP_S = 60

EARTH_RADIUS = float(6.371e3) ##km

def main(y, m, d, h):
    model_time = datetime(y,m,d,h)

    model_timestamp = model_time.strftime("%Y%m%d%H")

    if not os.path.exists("/home/bjing/afs-home/WWW/res/spaceshot/" + model_timestamp):

        os.mkdir("/home/bjing/afs-home/WWW/res/spaceshot/" + model_timestamp)

    resultfile = open("/home/bjing/afs-home/WWW/res/spaceshot/" + model_timestamp + "master", "w")
    print("Writing to master file " + "/home/bjing/afs-home/WWW/res/spaceshot/" + model_timestamp + "master")
    for name, lat, lon, coast in spaceshot_locations:
        try:
            print(name)
            spaceshot_search(name, coast, model_time, lat, lon, resultfile)
            resultfile.write("\n")
        except IndexError:
            print(name + " failed")
            continue

### Establish global constants ###
lon_offset = 0
points_per_degree = 1
hrs = 6
sourcepath = "../gefs"
mylvls = GEFS

def spaceshot_search(location_name, coast, model_time, slat, slon, resultfile):
    
    asc_rate = 3.7
    stop_alt = 29000
    max_t_h = 6


    model_timestamp = model_time.strftime("%Y%m%d%H")

    resultfile.write(location_name)

    for t in range(0, 384, 6):
        launchtime = model_time + timedelta(hours = t)

        sim_timestamp = launchtime.strftime("%Y%m%d%H")

        pathcache = list()

        filename = location_name + model_timestamp + "_" + sim_timestamp

        savepath = "/home/bjing/afs-home/WWW/res/spaceshot/" + model_timestamp
        if os.path.exists(savepath+"/"+filename):
            print(filename + "exists, continuing")
            continue

        resultfile.write("\n" + sim_timestamp + ": ")

        for n in range(1, 21):
            message = str(t) + "hours,member " + str(n)
            print(message)
            reset()
            set_constants(points_per_degree, lon_offset, hrs, mylvls, sourcepath, model_timestamp + "_", "_" + str(n).zfill(2) + ".npy")
            
            try: 
                rise, fall, coast = simulate(launchtime, slat, slon, asc_rate, SPACESHOT_TIMESTEP_S, stop_alt, 0, max_t_h)
                pathcache.append((rise, fall, coast))
                print("success")
            except (IOError, FileNotFoundError):
                print("fail")

        
        print("Evaluating ensemble")
        
        result = spaceshot_evaluate(pathcache, coast)

        resultfile.write(result)

        print(result)

        generate_html(pathcache, filename, model_timestamp, sim_timestamp)
    
    resultfile.write("\n")

def spaceshot_evaluate(pathcache, coast):
    __, lat, lon, __, __, ___ = pathcache[0][0][0]


    lon_range = math.degrees(SPACESHOT_DISTANCE_THRESHHOLD / (EARTH_RADIUS * math.cos(math.radians(lat))))

    print("lon range is " + str(lon_range))
    lon_threshhold = 0
    if coast == WEST:
        lon_threshhold = lon-lon_range
    else:
        lon_threshhold = lon + lon_range
    point_number_threshhold = SPACESHOT_TIME_THRESHHOLD * 3600.0 / SPACESHOT_TIMESTEP_S

    print("Lon threshhold, point number threshhold")
    print(lon_threshhold, point_number_threshhold)

    result = 0.0

    for i in range(len(pathcache)):
        result = result + spaceshot_single_evaluate(pathcache[i], lon_threshhold, point_number_threshhold, coast)
    
    return result / len(pathcache)

def spaceshot_single_evaluate(singlepath, lon_threshhold, point_number_threshhold, coast):

    __, path, __ = singlepath

    npoints = 0

    if coast == WEST:
        for point in path:
            __, __, lon, __, __, __ = point
            if (lon % 360) < (lon_threshhold % 360):
                npoints = npoints + 1
    else:
        for point in path:
            __, __, lon, __, __, __ = point
            if (lon % 360) > (lon_threshhold % 360):
                npoints = npoints + 1
    
    
    return min(1, npoints/point_number_threshhold)

def generate_html(pathcache, filename, model_timestamp, sim_timestamp):
    __, slat, slon, __, __, __ = pathcache[0][0][0]

    path = "/home/bjing/afs-home/WWW/res/spaceshot/" + model_timestamp + "/" + filename
    f = open(path, "w")

    f.write(part1 + str(slat) + "," + str(slon))
    f.write(part2)

    text_output = "Model time: " + model_timestamp + ", launchtime: " + sim_timestamp + "<br/><br/>"

    pathstring = ""
    for i in range(len(pathcache)):
        rise, fall, coast = pathcache[i]
        last = None
        if len(coast) > 0:
            last = coast[-1]
        elif len(fall) > 0:
            last = fall[-1]
        else:
            last = rise[-1]

        __, mlat, mlon, __, __, __ = last

        f.write(get_marker_string(mlat, mlon, "",str(i+1)))
    
        totalpath = rise + fall + coast
        for (time, lat, lon, alt, u, v) in totalpath:
            pathstring = pathstring + time.strftime("%H:%M:%S") + "Alt=" + str("%.0f" % alt)+ ",Loc=" + str("%.5f" % lat)+ "," + str("%.5f" % lon)+ \
             ",u=" + str("%.3f" % u)+ ",v=" + str("%.3f" % v)+  "<br>\n"
    
        text_output = text_output + "Model number: " + str (i+1) + "<br/>" + pathstring + "<br/><br/>"

        fall.insert(0, rise[-1])
        coast.insert(0, fall[-1])
        f.write(get_path_string(rise, "#FF0000"))
        f.write(get_path_string(fall, "#008000"))
        f.write(get_path_string(coast, "#000000"))

    f.write(part3short)
    f.write(text_output)
    f.write(part4 + part5)

main(int(sys.argv[1]), int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]))