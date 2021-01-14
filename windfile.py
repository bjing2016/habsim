import numpy as np
import math
import elev
from datetime import datetime, timedelta, timezone
import bisect
import time

class WindFile:
    def __init__(self, path: str):
        self.data_npz = np.load("downtest2/" + path, "r")
        self.data = self.data_npz['data']
        self.time = self.data_npz['timestamp']
        self.altitude = self.data_npz['levels']
        self.interval = self.data_npz['interval']//3600
        # TODO calculate resolution

    def get(self, lat: float, lon: float, altitude: float, time: float):
        if lat < -90 or lat > 90 or lon < -180 or lon > 360 or altitude > 975: # TODO cannot know altitude
            raise Exception("Invalid input value") # TODO more precise (which axis)

        # TODO wrap longitude

        bounds = self.get_bounds_and_fractions(lat, lon, altitude, time)
        
        #diffs = GEFS_ALT_DIFFS if levels == GEFS else GFSHIST_ALT_DIFFS # ???? not sure if this is still needed
        
        u, v = self.get_wind_helper(*bounds)
        
        return u, v

    def get_bounds_and_fractions(self, lat: float, lon: float, alt: float, time: float):
        lat_res, lon_res, pressure_res = None, None, None
        
        lat = 90 - lat
        lon = lon % 360

        base_time = int(datetime.fromtimestamp(self.time).strftime("%Y%m%d%H"))
        time = (time - base_time)/self.interval

        pressure = self.get_pressure_bounds(alt)
        
        print("bounds:", lat, lon, pressure, time)
        return lat, lon, pressure, time

    def get_pressure_bounds(self, alt: float):
        pressure = self.alt_to_hpa(alt)
        pressure_i = bisect.bisect_left(self.altitude, pressure)
        if pressure_i == len(self.altitude):
            return pressure_i-2
        if pressure_i == 0:
            return 0
        return pressure_i-(self.altitude[pressure_i]-pressure)/float(self.altitude[pressure_i] - self.altitude[pressure_i-1])

    def get_wind_helper(self, lat: float, lon: float, level: float, time: float):
        lat = int(lat)
        lon = int(lon)
        level = int(level)
        time = int(time)
        
        pressure_filter = np.array([1-level % 1, level % 1]).reshape(1, 1, 2, 1, 1)
        time_filter = np.array([1-time % 1, time % 1]).reshape(1, 1, 1, 2, 1) 
        lat_filter = np.array([1-lat % 1, lat % 1]).reshape(2, 1, 1, 1, 1)
        lon_filter = np.array([1-lon % 1, lon % 1]).reshape(1, 2, 1, 1, 1)

        print("pressure_filt", pressure_filter)
        print("time_filt", time_filter)
        print("lat_filt", lat_filter)
        print("lon_filt", lon_filter)

        cube = self.data[lat:lat+2, lon:lon+2, level:level+2, time:time+2, :]
       
        print("data point 1", self.data[lat+1, lon+1, level+1, time+1, :])
        print("data point 2", self.data[lat, lon, level, time])
        print("-----------")
        print(cube * lat_filter * lon_filter * pressure_filter * time_filter) 
        print("----------")
        print("cube", cube)

        u, v = np.sum(cube * lat_filter * lon_filter * pressure_filter * time_filter, axis=(0,1,2,3))

        return u, v

    def alt_to_hpa(self, altitude): # TODO if < 1, then exception, not in this function
        pa_to_hpa = 1.0/100.0
        if altitude < 11000:
            return pa_to_hpa * (1-altitude/44330.7)**5.2558 * 101325
        else:
            return pa_to_hpa * math.exp(altitude / -6341.73) * 128241

    def hpa_to_alt(self, p):
        if p >  226.325:
            return 44330.7 * (1 - (p / 1013.25) ** 0.190266)
        else:
            return -6341.73 * (math.log(p) - 7.1565)

def main():
    wind = WindFile("2021010100_01.npz")
    print(wind.time)
    print(wind.get(45, 90, 350, 2021010106))

    validation()

def validation():
    data = np.load("downtest2/2021010100_01.npz")
    datap = data['data'][45][90][17][1]

    print(datap)

if __name__ == "__main__":
    main()

