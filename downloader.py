import numpy as np
import pygrib
import urllib.request
import time
from datetime import datetime, timedelta
from multiprocessing import Pool
import queue
import socket
import sys
import os

def log(string):
    string = '{} {} {}\n'.format.(datetime.utcnow(), os.getpid(), string)
    with open('log.txt', 'a+') as f:
        f.write(string)


levels = [10, 20, 30, 50, 70,\
          100, 150, 200, 250, 300, 350, 400, 450,\
          500, 550, 600, 650, 700, 750, 800, 850,\
          900, 925, 950, 975, 1000]

## Array format: array[u,v][Pressure][Lat][Lon] ##
## Currently [lat 90 to -90][lon 0 to 359]

## One-indexed positions of the above levels in the result of grbs.select
order = [1, 13, 14, 2, 15, 3, 16, 4, 5, 6, 17, 7, 18, 8, 19, 20, 21, 9, 22, 23, 10, 24, 11, 25, 26, 12]

mount = True
path = "/gefs/gefs/" if mount else "./gefs/"
statuspath = '/gefs/serverstatus' if mount else 'serverstatus'
socket.setdefaulttimeout(10)
skip_threshhold = timedelta(hours = 24)
skip_code = 3

def worker(tasks):
    log("Worker launched")
    for task in tasks:
        log("Worker assigned task {}".format(task))
        while True:
            try:
                log("Attempting {}".format(task))
                single_run(*task)
                log("Success {}".format(task))
                break
            except:
                log("Error {}".format(task))
                time.sleep(10)
                y, m, d, h, t, n = task
                if datetime.utcnow() - datetime(y, m, d, h) > skip_threshhold:
                    log("Giving up {}".format(, task))
                    print('Worker giving up'); return 1
    return 0
        
def complete_run(y, m, d, h):
    print("Starting run {} {} {} {}".format(y, m, d, h))
    log('Downloader starting run {}{}{}{}'.format(y,m,d,h))
    skip = False
    k = 4 # workers per pool
    max_tasks = 50 # number of tasks per pool
    tasks = [list() for i in range(k)]
    j = 0
    for t in range(0, 384+6, 6):
        for n in range(1, 21):
            tasks[j % k].append((y,m,d,h,t,n))
            j = j + 1
            if j % max_tasks == 0 or j == (384/6 + 1)*20:
                p = Pool(k)
                log('Starting pool {}'.format(tasks))
                codes = p.map(worker, tasks)
                log('Closing pool {}'.format(tasks))
                p.close()
                if sum(codes) > 0:
                    log('Pool gave up, breaking loop')
                    skip = True; break
                log('Pool success')
                tasks = [list() for i in range(k)]    
        if skip: break
    if skip:
        log("Skipping run {} {} {} {}".format(y, m, d, h))
        print("Skipping run {} {} {} {}".format(y, m, d, h))
        exit(skip_code)
    print("Finished run {} {} {} {}".format(y, m, d, h))
    log("Finished run {} {} {} {}".format(y, m, d, h))

def single_run(y,m,d,h,t,n):
    
    base = datetime(y, m, d, h)
    basestring = base.strftime("%Y%m%d%H")    
    pred = base + timedelta(hours=t)
    predstring = pred.strftime("%Y%m%d%H")
    savename = basestring + "_" + predstring + "_" + str(n).zfill(2)
    
    if os.path.exists(path+'/'+savename+".npy"): 
        log("Exists; skipping {}".format(savename))
        return

    url = "ftp://ftp.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.{}{}{}/{}/pgrb2/gep{}.t{}z.pgrb2f{}"\
        .format(y, str(m).zfill(2), str(d).zfill(2), str(h).zfill(2), str(n).zfill(2), str(h).zfill(2), str(t).zfill(2))
    log("Downloading {} {}".format(savename, url))
    urllib.request.urlretrieve(url, path + savename + ".grb2")

    setBusy()

    log("Unpacking {}".format(savename))
    data = grb2_to_array(path + savename)
    data = np.float32(data)
    np.save(path + savename + ".npy", data)
    os.remove(path + savename + ".grb2")

def grb2_to_array(filename): 
    ## Array format: array[u,v][Pressure][Lat][Lon] ##
    ## Currently [lat 90 to -90][lon 0 to 359]
    grbs = pygrib.open(filename + ".grb2")
    
    dataset = np.zeros((2, len(levels), 181, 360))

    u = grbs.select(shortName='u',typeOfLevel='isobaricInhPa', level = levels)
    v = grbs.select(shortName='v',typeOfLevel='isobaricInhPa', level = levels)
    grbs.close()

    for i in range(len(levels)):
        dataset[0][i] = u[order[i]-1].data()[0]
        dataset[1][i] = v[order[i]-1].data()[0]
    return dataset

def setBusy():
    try:
        g = open(statuspath, "r")
        line = g.readline()
        g.close()
    except:
        line = ''
    if line != "Data refreshing. Sims may be slower than usual." and line != "Initializing. Please check again later.":
        g = open(statuspath, "w")
        g.write("Data refreshing. Sims may be slower than usual.")
        g.close()

if __name__ == "__main__":
    y, m, d, h = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    complete_run(y,m,d,h)
    g = open(statuspath, "w")
    g.write("Ready")
    g.close()
    log("Setting status to ready")