
from PIL import Image
import numpy


east = Image.open("30N090W_20101117_gmted_mea150.tif")
mid = Image.open("30N120W_20101117_gmted_mea150.tif")
west = Image.open("30N150W_20101117_gmted_mea150.tif")

east, mid, west = numpy.array(east), numpy.array(mid), numpy.array(west)

def getElevation(lat, lon):

    rLat = int(round(-(lat - 50) * 240 - 1))
    rLon = int(round((lon - (-150)) * 240))

    
    if rLat < 0 or rLat >= 4800:
        return 0
    
    if rLon < 0:
        return 0
    elif rLon < 7200:
        region = west
    elif rLon < 7200 * 2:
        region = mid
        rLon = rLon - 7200
    elif rLon < 7200 * 3:
        region = east
        rLon = rLon - 7200 * 2
    else:
        return 0
  
    return region[rLat][rLon]
