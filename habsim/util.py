import requests
import json
import math
import urllib
import os
from datetime import datetime, timezone

ROOT_URL = "http://habsim.org"
EARTH_RADIUS = 6371.0

def checkElev(launchsite):
    '''
    Returns true if the launch site is above ground. Only works in areas which have elevation data.
    '''
    return launchsite.elev >= getElev(launchsite.coords)

def getElev(coords):
    '''
    Fetches ground elevation from the server. Pass in a tuple (lat, lon)
    '''
    lat, lon = coords
    elev = requests.get(ROOT_URL + f"/elev?lat={lat}&lon={lon}").text
    return float(elev)

def whichgefs():
    '''
    Returns GEFS run timestamp
    '''
    return requests.get(url=ROOT_URL+"/which").text
    
def checkServer():
    '''
    Checks server status. This should be called before accessing the API.
    '''
    which = whichgefs()
    if which == "Unavailable":        
        print("Server live. Wind data temporarily unavailable.")
        return False
    else:
        print("Server live with GEFS run " + which)
        status = requests.get(ROOT_URL+"/status").text
        if status != "Ready":
            print(status)
        return True

def predict(timestamp, lat, lon, alt, drift_coeff, model, rate, dur, step):
    '''
    You should not need to call this method. Use the Prediction class instead.
    '''
    URL = ROOT_URL+'/singlepredict?&timestamp={}&lat={}&lon={}&alt={}&coeff={}&dur={}&step={}&model={}&rate={}'\
        .format(timestamp, lat, lon, alt, drift_coeff, dur, step, model, rate)
    return json.load(urllib.request.urlopen(URL))

def angular_to_lin_distance(lat1, lat2, lon1, lon2): 
    '''
    Returns distance between two points in km based on Euclian approximation.
    '''
    v = math.radians(lat2 - lat1) * EARTH_RADIUS
    u = math.radians(lon2 - lon1) * EARTH_RADIUS * math.cos(math.radians(lat1))
    return u, v

def closestPoint(traj, target, interval=1, division=0.75):

    '''
    Implements a modified binary search algorithm to find the closest point between a trajectory
    and a target. First, points are taken from the trajectory at a user-defined interval. Then the search range
    is [start, end]. If start is closer, the new range is [start, start + division * (end-start)], and vice versa.
    The search continues until a single point is reached.

    Returns the point, distance, and bearing
    '''

    traj = traj[::interval]
    if len(traj) == 1:
        return traj[0], haversine(*traj[0][1:3], *target.location(traj[0][0])), bearing(*traj[0][1:3], *target.location(traj[0][0]))
    slat, slon = traj[0][1:3]
    elat, elon = traj[-1][1:3]
    stlat, stlon = target.location(traj[0][0])
    etlat, etlon = target.location(traj[-1][0])

    start_dist = haversine(slat, slon, stlat, stlon)
    end_dist = haversine(elat, elon, etlat, etlon)

    if start_dist < end_dist:
        end = math.floor(len(traj) * division)
        return closestPoint(traj[:end], target, division=division)
    else:
        start = math.ceil(len(traj) * (1-division))
        return closestPoint(traj[start:], target, division=division)

def haversine(lat1, lon1, lat2, lon2):
    '''
    Returns great circle distance between two points.
    '''
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2-lat1
    dlon = lon2-lon1

    a = math.sin(dlat/2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return EARTH_RADIUS * c
    '''
    var φ1 = lat1.toRadians();
    var φ2 = lat2.toRadians(); 
    var Δφ = (lat2-lat1).toRadians();
    var Δλ = (lon2-lon1).toRadians();

    var a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
        Math.cos(φ1) * Math.cos(φ2) *
        Math.sin(Δλ/2) * Math.sin(Δλ/2);
    var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

    var d = R * c;
    https://www.movable-type.co.uk/scripts/latlong.html
    '''

def bearing(lat1, lon1, lat2, lon2):
    '''
    Returns compass bearing from point 1 to point 2.
    '''
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2-lon1

    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)

    return math.degrees(math.atan2(y, x))

    '''
    var y = Math.sin(λ2-λ1) * Math.cos(φ2);
    var x = Math.cos(φ1)*Math.sin(φ2) -
        Math.sin(φ1)*Math.cos(φ2)*Math.cos(λ2-λ1);
    var brng = Math.atan2(y, x).toDegrees();
    '''

def optimize_step(pred, target, alpha, decreasing_weights=False):
    '''
    Optimizes a trajectory to become closer to a target. Alpha is the gradient descent step size.
    The gradient is multipled by the absolute distance to make convergence more likely.
    If decreasing_weights is True, points earlier in the trajectory are moved more.
    However, the scale for alpha is different, so be careful when toggling the flag.
    '''
    closest, distance, bearing = closestPoint(pred.trajectory, target)
    vectoru = distance * math.sin(math.radians(bearing))
    vectorv = distance * math.cos(math.radians(bearing))

    prof = pred.profile
    steps_per_interval = int(prof.interval * 3600 / pred.step)
    for i in range(1, len(prof)):
        du, dv = pred.trajectory[i * steps_per_interval][-2:]
        prof[i] += alpha * (vectoru * du + vectorv * dv) * ((len(prof) - i) if decreasing_weights else 1)
    
    return closest, distance, bearing

gefs_layers = [30782, 26386, 23815, 20576, 18442, \
            16180, 13608, 11784, 10363, 9164, 8117, 7186, 6344, \
            5575, 4865, 4206, 3591, 3012, 2466, 1949, 1457, \
            989, 762, 540, 323, 111]

def average_wind(time, lat, lon, alt):
    '''
    Pass in a datetime object, lat, lon, alt.
    Averages wind from all 20 model runs by computing the average vector magnitude,
    then the average vector direction by summing all vectors.
    '''
    time = time.timestamp()
    time = datetime.utcfromtimestamp(time)
    URL = ROOT_URL+'/windensemble?&yr={}&mo={}&day={}&hr={}&mn={}&lat={}&lon={}&alt={}'\
        .format(time.year, time.month, time.day, time.hour, time.minute, lat, lon, alt)
    tmp = urllib.request.urlopen(URL)
    ulist, vlist, __, __ = list(json.load(tmp))
    winds = list(zip(ulist, vlist))
    magnitudes = list(map(lambda x: math.sqrt(x[0]**2 + x[1]**2), winds))
    magnitude = sum(magnitudes)/20
    usum, vsum = sum(ulist), sum(vlist)
    normalizer = math.sqrt(usum**2 + vsum**2)
    udir, vdir = usum/normalizer, vsum/normalizer
    return magnitude * udir, magnitude * vdir


def wind(time, lat, lon, alt, model):
    '''
    Pass in a datetime object, lat, lon, alt, and model number.
    Returns a list [u-wind, v-wind, du/dh, dv/dh]
    '''
    time = time.timestamp()
    time = datetime.utcfromtimestamp(time)
    URL = ROOT_URL+'/wind?&yr={}&mo={}&day={}&hr={}&mn={}&lat={}&lon={}&alt={}&model={}'\
        .format(time.year, time.month, time.day, time.hour, time.minute, lat, lon, alt, model)
    tmp = urllib.request.urlopen(URL)
    return list(json.load(tmp))