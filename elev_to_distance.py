import numpy
import haversine

### Generate list of ALL land coordinates

import elev



### 


files = [
    (30, -120),
    (30, -150)
]


### 
cache = list()


'''
d10N180W = numpy.load("10N180W_20101117_gmted_mea300.npy")
d10N150W = numpy.load("10N150W_20101117_gmted_mea300.npy")
d10N120W = numpy.load("10N120W_20101117_gmted_mea300.npy")
d10N090W = numpy.load("10N090W_20101117_gmted_mea300.npy")
d10N060W = numpy.load("10N060W_20101117_gmted_mea300.npy")
d10N030W = numpy.load("10N030W_20101117_gmted_mea300.npy")

d10N = numpy.append(d10N180W, d10N150W, 1)
d10N = numpy.append(d10N, d10N120W, 1)
d10N = numpy.append(d10N, d10N090W, 1)
d10N = numpy.append(d10N, d10N060W, 1)
d10N = numpy.append(d10N, d10N030W, 1)



d30N180W = numpy.load("30N180W_20101117_gmted_mea300.npy")'''
d30N150W = numpy.load("30N150W_20101117_gmted_mea300.npy")
d30N120W = numpy.load("30N120W_20101117_gmted_mea300.npy")


data = numpy.append(d30N150W, d30N120W, 1)

'''d30N090W = numpy.load("30N090W_20101117_gmted_mea300.npy")
d30N060W = numpy.load("30N060W_20101117_gmted_mea300.npy")
d30N030W = numpy.load("30N030W_20101117_gmted_mea300.npy")

d30N = numpy.append(d30N180W, d30N150W, 1)
d30N = numpy.append(d30N, d30N120W, 1)
d30N = numpy.append(d30N, d30N090W, 1)
d30N = numpy.append(d30N, d30N060W, 1)
d30N = numpy.append(d30N, d30N030W, 1)

d50N180W = numpy.load("50N180W_20101117_gmted_mea300.npy")
d50N150W = numpy.load("50N150W_20101117_gmted_mea300.npy")
d50N120W = numpy.load("50N120W_20101117_gmted_mea300.npy")
d50N090W = numpy.load("50N090W_20101117_gmted_mea300.npy")
d50N060W = numpy.load("50N060W_20101117_gmted_mea300.npy")
d50N030W = numpy.load("50N030W_20101117_gmted_mea300.npy")


d50N = numpy.append(d50N180W, d50N150W, 1)
d50N = numpy.append(d50N, d50N120W, 1)
d50N = numpy.append(d50N, d50N090W, 1)
d50N = numpy.append(d50N, d50N060W, 1)
d50N = numpy.append(d50N, d50N030W, 1)

data = numpy.append(d50N, d30N, 0)
data = numpy.append(data, d10N, 0)'''


lat, lon = numpy.nonzero(data)


lat = 50 - (lat + 1) / 120 ### array
lon = lon / 120 - 150

'''
exit()
for i in range(10*120, 70*120): 
    print("Outer loop, i = " + str(i))
    print(len(cache))
    for j in range(-180*120, 0):
        lat, lon = i/120, j/120
        elevation = elev.getElevation(lat, lon)
        if elevation > 0:
            cache.append((lat, lon))

print(len(cache))
'''
for (slat, slon) in files:
    
    name = str(slat) + "N" + str(abs(slon)) + "W" + "_km_to_land.npy"
    print(name)
    result = numpy.zeros((2400, 3600))

    for i in range(0, 2400): ## lat range
        for j in range(0, 3600): ## lon range
            mylat = slat + (2400 - i - 1) / 120
            mylon = slon + j / 120
            print()
            print(mylat)
            print(mylon)
            closest_land = ((lat-mylat)**2 + (lon-mylon)**2).argmin()
            closest_lat = lat[closest_land]
            closest_lon = lon[closest_land]
            
            dist = haversine.haversine((closest_lat, closest_lon), (mylat, mylon))
            result[i][j] = dist
            print(dist)
    
    numpy.save(name, result)



        
