import numpy

west = numpy.load("30N150W_20101117_gmted_mea150.npy")
central = numpy.load("30N120W_20101117_gmted_mea150.npy")
east = numpy.load("30N090W_20101117_gmted_mea150.npy")
def getElevation(lat, lon):
    ### return 0
    ### Comment above line out ###
    rLat = int(round(-(lat - 50) * 240 - 1))
    rLon = int(round((lon - (-150)) * 240))

    
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

def distance_from_land():
    pass

    ## Implement using haversine, argwhere, argmin
    ### Approximate -- find closest index based on coordinate diff
    ### Evaluates true distance


