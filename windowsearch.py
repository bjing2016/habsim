import sys
from simulate_py2 import *
from webutils import *
import elev
import math
import os
import numpy as np
from datetime import datetime, timedelta


spaceshot_locations = {
    ("LostCoast", 40.44, -124.4),
    ("BigSur", 36.305, -121.9),
    ("PointBlanco", 42.84, -124.55),
    ("Tillamook", 45.4, -123.95),
    ("Olympic", 48.3, -124.6)
}


def main(y, m, d, h):
    model_time = datetime(y,m,d,h)

    model_timestamp = model_time.strftime("%Y%m%d%H")

    os.mkdir("/home/bjing/afs-home/WWW/res/spaceshot/" + model_timestamp)

    resultfile = open("/home/bjing/afs-home/WWW/res/spaceshot/" + model_timestamp + "master", "a")

    for name, lat, lon in spaceshot_locations:
        try:
            print(name)
            spaceshot_search(name, model_time, lat, lon, resultfile)
        except IndexError:
            print(name + " failed")
            continue

### Establish global constants ###
lon_offset = 0
points_per_degree = 1
hrs = 6
sourcepath = "../gefs"
mylvls = GEFS

def spaceshot_search(location_name, model_time, slat, slon, resultfile):
    
    asc_rate = 3.7
    timestep_s = 60
    stop_alt = 29000
    max_t_h = 6


    model_timestamp = model_time.strftime("%Y%m%d%H")

    resultfile.write(location_name + "\n")

    for t in range(0, 385, 6):
        launchtime = model_time + timedelta(hours = t)

        sim_timestamp = launchtime.strftime("%Y%m%d%H")

        pathcache = list()

        filename = location_name + model_timestamp + "_" + sim_timestamp

        savepath = "/home/bjing/afs-home/WWW/res/spaceshot/" + model_timestamp
        if os.path.exists(savepath+filename):
            print(filename + "exists, continuing")
            continue


        resultfile.write(sim_timestamp + ": ")

        for n in range(1, 21):
            message = str(t) + "hours,member " + str(n)
            print(message)
            reset()
            set_constants(points_per_degree, lon_offset, hrs, mylvls, sourcepath, model_timestamp + "_", "_" + str(n).zfill(2) + ".npy")
            
            try: 
                rise, fall, coast = simulate(launchtime, slat, slon, asc_rate, timestep_s, stop_alt, 0, max_t_h)
                pathcache.append((rise, fall, coast))
                print("success")
            except (IOError, FileNotFoundError):
                print("fail")
                
        resultfile.write(spaceshot_evaluate(pathcache) + "\n")
    
    resultfile.write("\n")

def spaceshot_evaluate(pathcache):
    pass       

def generate_html(pathcache, filename, model_timestamp, sim_timestamp):
    __, slat, slon, __, __, __ = pathcache[0][0][0]

    path = "/home/bjing/afs-home/WWW/res/spaceshot/" + filename
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