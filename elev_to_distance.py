import numpy
import haversine

### Generate list of ALL land coordinates

import elev



### 


files = [
    (10, -30),
    (10, -60),
    (10, -90),
    (10, -120),
    (10, -150),
    (10, -180),

    (30, -30),
    (30, -60),
    (30, -90),
    (30, -120),
    (30, -150),
    (30, -180),

    (50, -30),
    (50, -60),
    (50, -90),
    (50, -120),
    (50, -150),
    (50, -180)
]


### 
cache = list()
for i in range(10*120, 90*120): 
    print("Outer loop, i = " + str(i))
    for j in range(-180*120, 0):
        lat, lon = i/120, j/120
        elevation = elev.getElevation(lat, lon)
        if elevation > 0:
            cache.append((lat, lon))

print(len(cache))

for (slat, slon) in files:
    
    name = str(lat) + "N" + str(abs(lon)) + "W" + "_km_to_land.npy"
    print(name)
    result = numpy.zeros((2400, 3600))

    for i in range(0, 2400): ## lat range
        for j in range(0, 3600): ## lon range
            lat = slat + (2400 - i - 1) * 120
            lon = slon + j * 120
            distances = [haversine.haversine((lat, lon), (slat, slon))]
            result[i][j] = numpy.min(distances)
    
    numpy.save(name, result)

print(distances)


        
