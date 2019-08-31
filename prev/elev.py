import numpy
import math

elevdir = '/gefs/elev/'

elev_cache = {} ## south_edge, west_edge

resolution = 120.0 ## points per degree

def load_elev(west_edge, south_edge):
    if (west_edge, south_edge) in elev_cache.keys():
        return elev_cache[(west_edge, south_edge)]
    
    path = str(abs(south_edge))
    if south_edge < 0:
        path = path + "S"
    else:
        path = path + "N"

    path = path + str(abs(west_edge)).zfill(3)

    if west_edge < 0:
        path = path + "W"
    else:
        path = path + "E"
    
    path = path + "_20101117_gmted_mea300.npy"

    data = numpy.load(elevdir + path, "r")
    elev_cache[(west_edge, south_edge)] = data
    return data

def getElevation(lat, lon):
    lat = round(lat * resolution) / resolution
    lon = round(lon * resolution) / resolution

    west_edge = math.floor(lon / 30.0) * 30

    lat_north_of_south_pole = lat + 90
    south_edge_north_of_south_pole = math.floor(lat_north_of_south_pole / 20.0) * 20
    south_edge = south_edge_north_of_south_pole - 90

    lat_index = int((20 - (lat - south_edge)) * resolution) - 1
    lon_index = int((lon - west_edge) * resolution)


    west_edge, south_edge = int(west_edge), int(south_edge)
    
    try:
        data = load_elev(west_edge, south_edge)
        result = data[lat_index][lon_index]
        return max(0, result)
    except (IOError, FileNotFoundError):
        return 0





'''
def getElevationOld(lat, lon):
    ### return 0
    ### Comment above line out ###
    rLat = int(round(-(lat - 50) * 240 - 1))
    rLon = int(round((lon - (-150)) * 240))

    ### Anchored at WEST edge. No data for east edge.
    ### Anchored at SOUTH edge. No data for noth edge.
    
    if rLat < 0 or rLat >= 4800:
        return 0
    
    if rLon < 0:
        return 0
    elif rLon < 7200:
        region = west
    elif rLon < 7200 * 2:
        region = central
        rLon = rLon - 7200
    elif rLon < 7200 * 3:
        region = east
        rLon = rLon - 7200 * 2
    else:
        return 0
  
    return region[rLat][rLon]

'''
#def distance_from_land():

    

# join.py

import numpy as np

def path(west_edge, south_edge):

    path = str(abs(south_edge))
    if south_edge < 0:
        path = path + "S"
    else:
        path = path + "N"
    path = path + str(abs(west_edge)).zfill(3)
    if west_edge < 0:
        path = path + "W"
    else:
        path = path + "E"
    path = path + "_20101117_gmted_mea300.npy"
    return path
import os
columns=list()

for left_edge in range(-180, 180, 30):
    column = list()
    for south_edge in range(70, -100, -20):
        mypath = path(left_edge, south_edge)
        print(mypath)
        block = np.load(mypath, 'r')
        column.append(block)
    columns.append(np.concatenate(column))

full = np.concatenate(columns, axis=1)
np.save('worldelev.npy', full)
