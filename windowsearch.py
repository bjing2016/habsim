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


destination = "/home/bjing/afs-home/WWW/res/"
#destination = "../"
### How far west does the balloon need to go?
### How long does it need to stay there?
SPACESHOT_DEFAULT_THRESHHOLD = 22 ## km
SPACESHOT_TIME_THRESHHOLD = .5 ## hours 
SPACESHOT_TIMESTEP_S = 60

CYCLOON_TIMESTEP_S = 240

spaceshot_locations = [
    ("PigeonPoint", 37.185, -122.393, WEST, SPACESHOT_DEFAULT_THRESHHOLD),
    ("LostCoast", 40.44, -124.4, WEST, SPACESHOT_DEFAULT_THRESHHOLD),
    ("BigSur", 36.305, -121.9, WEST, SPACESHOT_DEFAULT_THRESHHOLD),
    ("PointBlanco", 42.84, -124.55, WEST, SPACESHOT_DEFAULT_THRESHHOLD),
    ("Tillamook", 45.4, -123.95, WEST, SPACESHOT_DEFAULT_THRESHHOLD),
   # ("Olympic", 48.3, -124.6, WEST, SPACESHOT_DEFAULT_THRESHHOLD),
   # ("SouthTX", 27, -97.38, EAST, SPACESHOT_DEFAULT_THRESHHOLD),
   # ("Georgia", 30.9, -81.41, EAST, SPACESHOT_DEFAULT_THRESHHOLD),
    ("Hollister", 36.8492, -121.432, WEST, SPACESHOT_DEFAULT_THRESHHOLD + 55),
    ("Vandenberg", 34.6, -120.6, WEST, SPACESHOT_DEFAULT_THRESHHOLD),
   # ("Pendleton", 33.4, -117.5, WEST, SPACESHOT_DEFAULT_THRESHHOLD),
   # ("PointReyes", 38, -123, WEST, SPACESHOT_DEFAULT_THRESHHOLD),
   # ("MartinsBeach", 37.3843098, -122.3928558, WEST, SPACESHOT_DEFAULT_THRESHHOLD)
]

floatloon_locations = [
    ("PointReyes", 37.982, -123.067),
    ("BigSur", 36.2988, -121.9035),
    ("ElJarro", 37.0127, -122.222),
    ("AnoNuevo", 37.1046, -122.3249),
    ("PigeonPoint",  37.179, -122.39)

    
]




cycloon_locations = [

    ("PigeonPoint", 37.185, -122.393),
    ("Hollister", 36.8492, -121.432)
]

### Establish global constants ###
lon_offset = 0
points_per_degree = 1
hrs = 6
sourcepath = "../gefs"
mylvls = GEFS

FLOATING_COEFFICIENT = 0.5

EARTH_RADIUS_IN_KM = float(6.371e3) ##km


def main(y, m, d, h):
    model_time = datetime(y,m,d,h)

    model_timestamp = model_time.strftime("%Y%m%d%H")
    
    ### Floatloon

    if not os.path.exists(destination + "floatloon/" + model_timestamp):

        os.mkdir(destination + "floatloon/" + model_timestamp)

    resultfile = open(destination + "floatloon/" + model_timestamp + "master", "w")
    print("Writing to master file " + model_timestamp + "master")
    print("Floatloon")

    for (name, lat, lon) in floatloon_locations:
        floatloon_search(name, model_time, lat, lon, resultfile)
        resultfile.write("\n")
    
    ### Cycloon


    if not os.path.exists(destination + "cycloon/" + model_timestamp):

        os.mkdir(destination + "cycloon/" + model_timestamp)

    resultfile = open(destination + "cycloon/" + model_timestamp + "master", "w")
    print("Writing to master file "  + model_timestamp + "master")
    for name, lat, lon in cycloon_locations:
        try:
            print(name)
            cycloon_search(name, model_time, lat, lon, resultfile)
            resultfile.write("\n")
        except IndexError:
            print(name + " failed")
            continue  



    ### Spaceshot

    if not os.path.exists(destination + "/spaceshot/" + model_timestamp):

        os.mkdir(destination + "spaceshot/" + model_timestamp)

    resultfile = open(destination + "spaceshot/" + model_timestamp + "master", "w")
    print("Writing to master file " + "/home/bjing/afs-home/WWW/res/spaceshot/" + model_timestamp + "master")
    for name, lat, lon, whichcoast, distance in spaceshot_locations:
        try:
            print(name)
            spaceshot_search(name, whichcoast, distance, model_time, lat, lon, resultfile)
            resultfile.write("\n")
        except ValueError:
            print(name + " failed")
            continue

def cycloon_search(location_name, model_time, slat, slon, resultfile):
    
    sunset = 3 + 24 ## UTC ### 
    launch_hour = 19 ###
    cycloon_rates = [0.5,1.0]
    max_t_h = 144

    model_timestamp = model_time.strftime("%Y%m%d%H")
    maxtime = model_time + timedelta(hours = 375)
    resultfile.write(location_name)

    cycloon_queue = list()

    for rate in cycloon_rates:
        alt = (sunset - launch_hour) * 3600 * rate ## rising 8 hours
        cycloon_queue.append((rate, alt))
    
    for d in range(15):
        for rate, alt in cycloon_queue:
            launchtime = model_time + timedelta(days=d, hours=launch_hour)

            sim_timestamp = launchtime.strftime("%Y%m%d%H")
            pathcache = list()
            filename = location_name + model_timestamp + "_" + sim_timestamp + "_" + str(rate);


            resultfile.write("\n" + sim_timestamp + ": ")

            
            max_hours = maxtime - launchtime
            print(launchtime)
            max_hours = max_hours.seconds / 3600 + max_hours.days * 24

            for n in range(1, 21):
                message = str(launchtime) + "hours,member " + str(n)
                print(message)
                reset()
                set_constants(points_per_degree, lon_offset, hrs, mylvls, sourcepath, model_timestamp + "_", "_" + str(n).zfill(2) + ".npy")
            
                try: 
                    rise, fall, coast = simulate(launchtime, slat, slon, rate, CYCLOON_TIMESTEP_S, alt, 2, min(max_t_h,max_hours), coefficient=FLOATING_COEFFICIENT)
                    pathcache.append((rise, fall, coast))
                    print("success")
                except (IOError, FileNotFoundError):
                    print("fail")

        
            result = cycloon_evaluate(pathcache, max_hours)
            resultfile.write(result)

            print("Evaluating ensemble: " + result)
            
            generate_html(pathcache, "cycloon", filename, model_timestamp, sim_timestamp, 24, CYCLOON_TIMESTEP_S)
    
    
    resultfile.write("\n")



def floatloon_search(location_name, model_time, slat, slon, resultfile):
    
    launch_hours = [0,3,6,9,12,15,18,21] ###
    max_t_h = 144

    model_timestamp = model_time.strftime("%Y%m%d%H")
    maxtime = model_time + timedelta(hours = 375)
    resultfile.write(location_name)

    for d in range(2, 3): #15
        for launch_hour in launch_hours:
            launchtime = model_time + timedelta(days=d, hours=launch_hour)

            sim_timestamp = launchtime.strftime("%Y%m%d%H")
            pathcache = list()
            filename = location_name + model_timestamp + "_" + sim_timestamp


            resultfile.write("\n" + sim_timestamp + ": ")

            
            max_hours = maxtime - launchtime
            print(maxtime)
            print(launchtime)
            max_hours = max_hours.seconds / 3600 + max_hours.days * 24

            for n in range(1, 21):
                message = str(launchtime) + "hours,member " + str(n)
                print(message)
                reset()
                set_constants(points_per_degree, lon_offset, hrs, mylvls, sourcepath, model_timestamp + "_", "_" + str(n).zfill(2) + ".npy")
            
                try: 
                    rise, fall, coast = simulate(launchtime, slat, slon, 1, CYCLOON_TIMESTEP_S, 0, 1, min(max_t_h,max_hours), coefficient=FLOATING_COEFFICIENT)
                    pathcache.append((rise, fall, coast))
                    print("success")
                except (IOError, FileNotFoundError):
                    print("fail")
        
            result = cycloon_evaluate(pathcache, max_hours)
            resultfile.write(result)

            print("Evaluating ensemble: " + result)
            
            try:
                generate_html(pathcache, "floatloon", filename, model_timestamp, sim_timestamp, 24, CYCLOON_TIMESTEP_S)
            except IndexError:
                continue
            
        
        resultfile.write("\n")


def cycloon_evaluate(pathcache, max_hours):
    resultstring = ""

    hours_to_evaluate = [24, 48, 72, 96, 120, 144]
    
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

def spaceshot_search(location_name, whichcoast, distance, model_time, slat, slon, resultfile):
    
    asc_rate = 3.7
    stop_alt = 29000
    max_t_h = 6

    model_timestamp = model_time.strftime("%Y%m%d%H")

    resultfile.write(location_name)

    for t in range(0, 384, 24):
        launchtime = model_time + timedelta(hours = t)
        sim_timestamp = launchtime.strftime("%Y%m%d%H")
        pathcache = list()
        filename = location_name + model_timestamp + "_" + sim_timestamp
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
                print("faillll")

        try:
            result = spaceshot_evaluate(pathcache, whichcoast, distance)
            resultfile.write(str(result))
            print("Proability: " + str(result))
            generate_html(pathcache, "spaceshot", filename, model_timestamp, sim_timestamp, 6, SPACESHOT_TIMESTEP_S)
        except (IndexError):
            print("Failed")
    
    resultfile.write("\n")

def spaceshot_evaluate(pathcache, whichcoast, distance):
    __, lat, lon, __, __, ___ = pathcache[0][0][0]

    lon_range = math.degrees(distance / (EARTH_RADIUS_IN_KM * math.cos(math.radians(lat))))

    lon_threshhold = 0
    if whichcoast == WEST:
        lon_threshhold = lon-lon_range
    else:
        lon_threshhold = lon + lon_range
    point_number_threshhold = SPACESHOT_TIME_THRESHHOLD * 3600.0 / SPACESHOT_TIMESTEP_S

    result = 0.0

    for i in range(len(pathcache)):
        result = result + spaceshot_single_evaluate(pathcache[i], lon_threshhold, point_number_threshhold, whichcoast)
    
    return result / len(pathcache)

def spaceshot_single_evaluate(singlepath, lon_threshhold, point_number_threshhold, whichcoast):

    __, path, __ = singlepath

    npoints = 0

    if whichcoast == WEST:
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

def generate_html(pathcache, folder, filename, model_timestamp, sim_timestamp, marker_interval, timestep):
    ## As hours --- only works if time_step goes evenly into one hour
    __, slat, slon, __, __, __ = pathcache[0][0][0]

    path = destination+ folder + "/" + model_timestamp + "/" + filename + ".html"
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

main(int(sys.argv[1]), int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]))