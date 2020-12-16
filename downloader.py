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
    string = '{} {} {}\n'.format(datetime.utcnow(), os.getpid(), string)
    with open('log.txt', 'a+') as f:
        f.write(string)

levels = [1, 2, 3, 5, 7, 20, 30, 70, 150, 350, 450, 550, 600, 650, 750, 800, 900, 950, 975]

## Array format: array[u,v][Pressure][Lat][Lon] ##
## Currently [lat 90 to -90][lon 0 to 359]

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
                    log("Giving up {}".format(task))
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

    m, d, h, n = map(lambda x: str(x).zfill(2), [m, d, h, n])
    t = str(t).zfill(3)
    url = f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.{y}{m}{d}/{h}/atmos/pgrb2bp5/gep{n}.t{h}z.pgrb2b.0p50.f{t}"
    log("Downloading {} {}".format(savename, url))
    urllib.request.urlretrieve(url, path + savename + ".grb2")

    setBusy()

    log("Unpacking {}".format(savename))
    data = grb2_to_array(path + savename)
    data = np.float16(data)
    np.save(path + savename + ".npy", data)
    os.remove(path + savename + ".grb2")

def grb2_to_array(filename): 
    ## Array format: array[u,v][Pressure][Lat][Lon] ##
    ## Currently [lat 90 to -90][lon 0 to 359]
    grbs = pygrib.open(filename + ".grb2")
    
    dataset = np.zeros((2, len(levels), 181, 360))

    u = grbs.select(shortName='u', typeOfLevel='isobaricInhPa')
    v = grbs.select(shortName='v', typeOfLevel='isobaricInhPa')
    grbs.close()

    assert(len(u) == len(levels))

    for i, level in enumerate(levels):
        assert(u[i]['level'] == level)
        assert(v[i]['level'] == level)
        dataset[0][i] = u[i].data()[0][::2, ::2]
        dataset[1][i] = v[i].data()[0][::2, ::2]
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
