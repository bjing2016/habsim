import numpy as np
import pygrib
import urllib.request
import os.path
import time
import urllib
import sys
from datetime import datetime, timedelta

from threading import Thread
import queue
import socket

levels = [10, 20, 30, 50, 70,\
          100, 150, 200, 250, 300, 350, 400, 450,\
          500, 550, 600, 650, 700, 750, 800, 850,\
          900, 925, 950, 975, 1000]

## Array format: array[u,v][Pressure][Lat][Lon] ##
## Currently [lat 90 to -90][lon 0 to 359]

## One-indexed positions of the above levels in the result of grbs.select
order = [1, 13, 14, 2, 15, 3, 16, 4, 5, 6, 17, 7, 18, 8, 19, 20, 21, 9, 22, 23, 10, 24, 11, 25, 26, 12]

q = queue.Queue()
socket.setdefaulttimeout(10)

def worker():
    while not q.empty():
        item = q.get()
        single_run(*item)
        q.task_done()

def complete_run(y, m, d, h, path):
    for t in range(0, 384+6, 6):
        for n in range(1, 21):
            q.put((y,m,d,h,t,n,path))
            
    for i in range(1):
        th = Thread(target=worker)
        th.start()
    q.join()

def single_run(y,m,d,h,t,n, path):

    base = datetime(y, m, d, h)
    basestring = base.strftime("%Y%m%d%H")    
    pred = base + timedelta(hours=t)
    predstring = pred.strftime("%Y%m%d%H")
    savename = basestring + "_" + predstring + "_" + str(n).zfill(2)

    if os.path.exists(path+'/'+savename+".npy"):
        print("Skipping " + savename)
        return

    print("Downloading " + savename)
    url = "ftp://ftp.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.{}{}{}/{}/pgrb2/gep{}.t{}z.pgrb2f{}"\
        .format(y, str(m).zfill(2), str(d).zfill(2), str(h).zfill(2), str(n).zfill(2), str(h).zfill(2), str(t).zfill(2))
    while True:
        try:
            #os.system("wget " + url + " -O " + path + "/" + savename + ".grb2")
            urllib.request.urlretrieve(url, path + "/" + savename + ".grb2")
            break
        except (TimeoutError, urllib.error.URLError, ConnectionResetError, socket.timeout):
            print("Error " + savename + ", trying again in 10s")
            time.sleep(10)
    
    print("Unpacking " + savename)
    data = grb2_to_array(path + "/" + savename)
    data = np.float32(data)
    
    print("Saving " + savename)
    np.save(path + "/" + savename + ".npy", data)
    
    print("Deleting " + savename)
    os.remove(path + "/" + savename + ".grb2")

def grb2_to_array(filename): 
    ## Array format: array[u,v][Pressure][Lat][Lon] ##
    ## Currently [lat 90 to -90][lon 0 to 359]
    grbs = pygrib.open(filename + ".grb2")
    
    dataset = np.zeros((2, len(levels), 181, 360))

    u = grbs.select(shortName='u',typeOfLevel='isobaricInhPa', level = levels)
    v = grbs.select(shortName='v',typeOfLevel='isobaricInhPa', level = levels)

    for i in range(len(levels)):
        dataset[0][i] = u[order[i]-1].data()[0]
        dataset[1][i] = v[order[i]-1].data()[0]

    ### Thanks to KMarshland for pointers on using PyGrib ###
    #for i in range(len(levels)):
        ### [lat, lat, lon, lon]
     #   for grb in grbs.select(shortName='u',typeOfLevel='isobaricInhPa', level = levels[i]):
      #      dataset[0][i] = grb.data()[0]

    #for i in range(len(levels)):
     #   for grb in grbs.select(shortName='v',typeOfLevel='isobaricInhPa', level = levels[i]):
      #      dataset[1][i] = grb.data()[0]

    return dataset

if __name__ == "__main__":
    year, month, day, hour = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    complete_run(year, month, day, hour, "../gefs")
    yesterday = datetime(year, month, day-1)
    yesterday_string = yesterday.strftime("%Y%m%d")
    os.system("rm ../gefs/" + yesterday_string + "*")