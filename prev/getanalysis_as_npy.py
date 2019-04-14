import matplotlib
import numpy as np
import pygrib
import h5py
import urllib.request
import os.path
import sys


### Current download as npy ###

levels = [1, 2, 3, 5, 7, 10, 20, 30, 50, 70,\
          100, 150, 200, 250, 300, 350, 400, 450,\
          500, 550, 600, 650, 700, 750, 800, 850,\
          900, 925, 950, 975, 1000]

default_dir = "../../gfsanl/"

def get_file_name(save_dir, y, m, d, h):
    return save_dir + "/" + str(y) + str(m).zfill(2) + str(d).zfill(2) + str(h).zfill(2)



def download_anl(y, m, d, h, save_dir):
    save_path = get_file_name(save_dir, y, m, d, h)

    url = "https://nomads.ncdc.noaa.gov/data/gfsanl/" + str(y) + str(m).zfill(2) + "/" + str(y) + str(m).zfill(2) + str(d).zfill(2) + \
              "/gfsanl_4_" + str(y) + str(m).zfill(2) + str(d).zfill(2) + "_" + str(h).zfill(2) + "00_000.grb2"

    if (not os.path.exists(save_path + ".grb2")) and (not os.path.exists(save_path + ".h5")):
        print("Retreiving " + url)
        urllib.request.urlretrieve (url, save_path + ".grb2")
    return save_path


def grb2_to_array(filename): 
    ## Array format: array[u,v][Pressure][Lat][Lon] ##
    ## Currently [lat 90 to -90][lon 0 to 395.5]
    grbs = pygrib.open(filename + ".grb2")
    dataset = np.zeros((2, len(levels), 180*2 + 1, 360*2))

    ### Thanks to KMarshland for pointers on using PyGrib ###
    for i in range(len(levels)):
        for grb in grbs.select(shortName='u',typeOfLevel='isobaricInhPa', level = levels[i]):
            dataset[0][i] = grb.data()[0]
        
    for i in range(len(levels)):
        for grb in grbs.select(shortName='v',typeOfLevel='isobaricInhPa', level = levels[i]):
            dataset[1][i] = grb.data()[0]

    return dataset


## Unfortunately, all the datasets are named test ##
def save_h5py(array, path):
    with h5py.File(path + ".h5", 'w') as hf:
        hf.create_dataset("test", data = array, dtype = 'f', compression = 'gzip')

def delete_grb2(path):
    os.remove(path + ".grb2")


def main_single_dataset(y, m, d, h, save_dir):
    path = download_anl(y, m, d, h, save_dir)
    if not os.path.exists(path + ".h5"):
        print("Downloaded " + path + ", unpacking")
        data = grb2_to_array(path)
        print("Saving " + path)
        np.save(path + ".npy", data)
        
        ### save_h5py(data, path)
        print("Deleting" + path)
        delete_grb2(path)
    else:
        print("Skipping " + path)


def main():
    args = sys.argv[1:]
    if len(args) == 5 or len(args) == 9:
        path = args.pop()
    else:
        path = default_dir
    if len(args) != 4 and len(args) != 8:
        print("Invalid number of arguments.")
        exit()

    if len(args) == 4:
        y, m, d, h = list(map(int, args))
        main_single_dataset(y, m, d, h, path)
        exit()

    y1, y2, m1, m2, d1, d2, h1, h2 = list(map(int, args))

    for y in range(y1, y2 + 1):
        for m in range(m1, m2 + 1):
            for d in range(d1, d2 + 1):
                for h in range(h1, h2 + 6, 6):
                    try:
                        main_single_dataset(y, m, d, h, path)
                    except (IOError, ValueError):
                        print("Error:" + get_file_name(path,y,m,d,h))
main()
