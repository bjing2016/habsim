import numpy as np
import pygrib
import urllib.request
import os.path
import sys
import h5py
from datetime import datetime, timedelta

## [1, 2, 3, 5, 7, 

levels = [10, 20, 30, 50, 70,\
          100, 150, 200, 250, 300, 350, 400, 450,\
          500, 550, 600, 650, 700, 750, 800, 850,\
          900, 925, 950, 975, 1000]


### ftp://ftp.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.20190225/00/pgrb2bp5/gep01.t00z.pgrb2a.0p50.f150

def get_file_name(y, m, d, h, yt, mt, dt, ht, n):
    return str(y) + str(m).zfill(2) + str(d).zfill(2) + str(h).zfill(2) + "_" + str(y) + str(m).zfill(2) + str(d).zfill(2) + str(h).zfill(2) + "_" + str(n).zfill(3)


### https://nomads.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.20190224/18/pgrb2/gep03.t18z.pgrb2f222
### ftp://ftp.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.20190225/00/pgrb2bp5/gep01.t00z.pgrb2b.0p50.f099 ###

def get_url(y, m, d, h, t, n):
    url = "ftp://ftp.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs." + str(y) + str(m).zfill(2) + str(d).zfill(2) + "/"
    url = url +  str(h).zfill(2) + "/pgrb2bp5/gep" + str(n).zfill(2)
    url = url + ".t" + str(h).zfill(2) + "z.pgrb2b.0p50.f" + str(h).zfill(3) 
    return url

def grb2_to_array(filename): 
    ## Array format: array[u,v][Pressure][Lat][Lon] ##
    ## Currently [lat 90 to -90][lon 0 to 359.5]
    grbs = pygrib.open(filename + ".grb2")
    
    
    dataset = np.zeros((2, len(levels), 180*2 + 1, 360*2))

    ### Thanks to KMarshland for pointers on using PyGrib ###
    for i in range(len(levels)):
        
        for grb in grbs.select(shortName='u',typeOfLevel='isobaricInhPa', level = levels[i]):
            dataset[0][i] = grb.data()[0]
        print(i)

    for i in range(len(levels)):
        for grb in grbs.select(shortName='v',typeOfLevel='isobaricInhPa', level = levels[i]):
            dataset[1][i] = grb.data()[0]

    return dataset



def single_run(y, m, d, h, t, path):
    for n in range(1, 21):
        url = get_url(y, m, d, h, t, n)
        time = datetime(y, m, d, h + t)
        yt, mt, dt, ht = time.year, time.month, time.date, time.hour
        save_string = get_file_name(y, m, d, h, yt, mt, dt, ht, n)
        
        print("Downloading " + save_string)

        urllib.request.urlretrieve (url, path + "/" + save_string + ".grb2")

        print("Unpacking " + save_string)

        data = grb2_to_array(path + "/" + save_string)

        print("Saving " + save_string)

        np.save(path + "/" + save_string + ".npy", data)

        print("Deleting " + save_string)

        os.remove(path + "/" + save_string + ".grb2")




def main():
    y, m, d, h, path = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    
    timestamp = datetime(y, m, d, h)
    base_timestamp = timestamp

    base_string = timestamp.strftime("%Y%m%d%H")    
    
    t = 0
    while t <= 384:
        single_run(y, m, d, h, t, path)
        t = t + 3


main()