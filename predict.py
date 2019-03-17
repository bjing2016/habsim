import sys
from simulate_py2 import *
from webutils import *
import elev
import math
import os
import numpy as np
from datetime import datetime, timedelta

### Establish global constants ###
lon_offset = 0
points_per_degree = 1
hrs = 6
sourcepath = "../gefs"
mylvls = GEFS
'''
def predict(y, m, d, h, slat, slon, ascent_rate, step, stop_alt, descent_rate, max_duration, start_alt = None):
    model_time = datetime(y,m,d,h)
    model_timestamp = model_time.strftime("%Y%m%d%H")

    reset()
    for n in range(21):
        set_constants(points_per_degree, lon_offset, hrs, mylvls, sourcepath, model_timestamp + "_", "_" + str(n).zfill(2) + ".npy")
'''
def dummy_predict(y, m, d, h, slat, slon, ascent_rate, step, stop_alt, descent_rate, max_duration, start_alt = None):
    paths = list()
    for i in range(20):
        rise = list()
        rise = [(37, -122), (48, -129), (35, -118)]
        fall = [(35, -118), (36, -120), (35, -121)]
        coast = [(35, -121), (34, -127), (33, -130)]
        singlepath = (rise, fall, coast)
        paths.append(singlepath)
    
    markers = [(37, -122, "label", "title"), (36, -125, "another one", "another title")]
    text = "some sample text to display"

    return paths, markers, text