import numpy

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
        region = numpy.load("30N150W_20101117_gmted_mea150.npy")
    elif rLon < 7200 * 2:
        region = numpy.load("30N120W_20101117_gmted_mea150.npy")
        rLon = rLon - 7200
    elif rLon < 7200 * 3:
        region = numpy.load("30N090W_20101117_gmted_mea150.npy")
        rLon = rLon - 7200 * 2
    else:
        return 0
  
    return region[rLat][rLon]
