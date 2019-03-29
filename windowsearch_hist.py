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



CYCLOON_TIMESTEP_S = 240


cycloon_locations = [
    ("PigeonPoint", 37.185, -122.393),
    ("Hollister", 36.8492, -121.432)
]



floatloon_locations = [
    ("PigeonPoint", 37.185, -122.393),
    ("Hollister", 36.8492, -121.432)
]

### Establish global constants ###
lon_offset = 180
points_per_degree = 2
hrs = 6
sourcepath = "/home/bjing/afs-home/cgi-bin/gfshist"
mylvls = GFSANL



EARTH_RADIUS_IN_KM = float(6.371e3) ##km

def main():
    ### Cycloon

    model_time = datetime(2018,1,1)
    if not os.path.exists("/home/bjing/afs-home/WWW/res/floatloon/2018"):

        os.mkdir("/home/bjing/afs-home/WWW/res/floatloon/2018")

    resultfile = open("/home/bjing/afs-home/WWW/res/floatloon/2018master", "w")
    print("Floatloon")
    floatloon_search("PigeonPoint", model_time, 37.179, -122.39, resultfile)
    resultfile.write("\n")

'''
    if not os.path.exists("/home/bjing/afs-home/WWW/res/cycloon/2018"):

        os.mkdir("/home/bjing/afs-home/WWW/res/cycloon/2018")

    resultfile = open("/home/bjing/afs-home/WWW/res/cycloon/2018master", "w")
    print("Writing to master file")
    for name, lat, lon in cycloon_locations:
        try:
            print(name)
            cycloon_search(name, model_time, lat, lon, resultfile)
            resultfile.write("\n")
        except IndexError:
            print(name + " failed")
            continue
'''


def floatloon_search(location_name, model_time, slat, slon, resultfile):
    
    launch_hour = 7 ###
    max_t_h = 240

    maxtime = datetime(2019,1,1,0)
    resultfile.write(location_name)

    for d in range(364):
        launchtime = model_time + timedelta(days=d, hours=launch_hour)

        sim_timestamp = launchtime.strftime("%Y%m%d%H")
        pathcache = list()
        filename = location_name + sim_timestamp


        resultfile.write("\n" + sim_timestamp + ": ")

        
        max_hours = maxtime - launchtime
        print(maxtime)
        print(launchtime)
        max_hours = max_hours.seconds / 3600 + max_hours.days * 24

        for n in range(1):
            message = str(launchtime) + "hours,member " + str(n)
            print(message)
            reset()
            set_constants(points_per_degree, lon_offset, hrs, mylvls, sourcepath, "", ".npy")
        
            try: 
                rise, fall, coast = simulate(launchtime, slat, slon, 1, CYCLOON_TIMESTEP_S, 0, 1, min(max_t_h,max_hours))
                pathcache.append((rise, fall, coast))
                print("success")
            except (IOError, FileNotFoundError):
                print("fail")
    
        result = cycloon_evaluate(pathcache, max_hours)
        resultfile.write(result)

        print("Evaluating ensemble: " + result)
        
        try:
            generate_html(pathcache, "floatloon", filename, "2018", sim_timestamp, 24, CYCLOON_TIMESTEP_S)
        except IndexError:
            continue
    
    
    resultfile.write("\n")


def cycloon_search(location_name, model_time, slat, slon, resultfile):
    
    sunset = 3 + 24 ## UTC ### 
    launch_hour = 19 ###
    cycloon_rates = [0.5,1.0]
    max_t_h = 240

    maxtime = datetime(2019,1,1,0)
    resultfile.write(location_name)

    cycloon_queue = list()

    for rate in cycloon_rates:
        alt = (sunset - launch_hour) * 3600 * rate ## rising 8 hours
        cycloon_queue.append((rate, alt))
    
    for d in range(364):
        for rate, alt in cycloon_queue:
            print("d = " + str(d))
        
            launchtime = model_time + timedelta(days=d, hours=launch_hour)

            sim_timestamp = launchtime.strftime("%Y%m%d%H")
            pathcache = list()
            filename = location_name + sim_timestamp + "_" + str(rate)


            resultfile.write("\n" + sim_timestamp + ": ")

            
            max_hours = maxtime - launchtime
            print(maxtime)
            print(launchtime)
            max_hours = max_hours.seconds / 3600 + max_hours.days * 24

            for n in range(1):
                message = str(launchtime) + "hours,member " + str(n)
                print(message)
                reset()
                set_constants(points_per_degree, lon_offset, hrs, mylvls, sourcepath, "", ".npy")
            
                try: 
                    rise, fall, coast = simulate(launchtime, slat, slon, rate, CYCLOON_TIMESTEP_S, alt, 2, min(max_t_h,max_hours))
                    pathcache.append((rise, fall, coast))
                    print("success")
                except (IOError, ValueError, FileNotFoundError):
                    print("fail")
            
            try:
                result = cycloon_evaluate(pathcache, max_hours)
                resultfile.write(result)

                print("Evaluating ensemble: " + result)
            
                generate_html(pathcache, "cycloon", filename, "2018", sim_timestamp, 24, CYCLOON_TIMESTEP_S)
            except IndexError:
                print("Error, moving to next")
    
    
    resultfile.write("\n")



def cycloon_evaluate(pathcache, max_hours):
    resultstring = ""

    hours_to_evaluate = [24, 48, 72, 96, 120, 144, 168, 192, 216, 240]
    
    for hour in hours_to_evaluate:
        if hour > max_hours:
            break
        
        num_surviving = 0
        longitudes = []

        for rise, fall, coast in pathcache:
            totalpath = rise+fall+coast
            length = len(totalpath)
            flighthours = length * CYCLOON_TIMESTEP_S / 3600
            if flighthours > hour:
                num_surviving = num_surviving + 1
                longitudes.append(totalpath[int(hour * 3600 / CYCLOON_TIMESTEP_S)][2])
    
        resultstring = resultstring + str(num_surviving) + ","
        
        if (num_surviving == 0):
            resultstring = resultstring + "; "
        else:
            longitude_mean = np.mean(longitudes)
            resultstring = resultstring + str("%.1f" % longitude_mean) + "; "
    
    return resultstring

def generate_html(pathcache, folder, filename, model_timestamp, sim_timestamp, marker_interval, timestep):
    ## As hours --- only works if time_step goes evenly into one hour
    __, slat, slon, __, __, __ = pathcache[0][0][0]

    path = "/home/bjing/afs-home/WWW/res/"+ folder + "/" + model_timestamp + "/" + filename
    f = open(path, "w")

    f.write(part1 + str(slat) + "," + str(slon))
    f.write(part2)

    text_output = "Model time: " + model_timestamp + ", launchtime: " + sim_timestamp + "<br/><br/>"

    
    marker_interval_in_waypoints = marker_interval * 3600 / timestep
    
    for i in range(len(pathcache)):
        pathstring = ""
        rise, fall, coast = pathcache[i]
        
        totalpath = rise + fall + coast
        for j in range(len(totalpath)):
            time, lat, lon, alt, u, v = totalpath[j]
            if (j % marker_interval_in_waypoints == 0 and j != 0) or j == len(totalpath)-1:
                f.write(get_marker_string(lat, lon, str(i+1), str(time)))
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

main()