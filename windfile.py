import numpy as np
import math
import elev
import datetime
import bisect
import time
from scipy import interpolate

class WindFile:
    def __init__(self, path):
        self.data_npz = np.load(path, "r")
        self.data = self.data_npz['data']
        self.time = self.data_npz['timestamp']
        self.levels = self.data_npz['levels']
        self.interval = self.data_npz['interval']
        self.resolution_lat_multiplier = (self.data.shape[-5] - 1) / 180
        self.resolution_lon_multiplier = (self.data.shape[-4] - 1) / 360

    def get(self, lat, lon, altitude, time):
        if lat < -90 or lat > 90:
            raise Exception(f"Latitude {lat} out of bounds")
        if lon < -180 or lon > 360:
            raise Exception(f"Longitude {lon} out of bounds")
        
        if lon < 0:
            lon = 360 + lon

        if isinstance(time, datetime.datetime):
            time = time.timestamp()
        
        tmax = self.time + self.interval * (self.data.shape[-2]-1)
        if time < self.time or time > tmax:
            raise Exception(f"Time {time} out of bounds")

        indices = self.get_indices(lat, lon, altitude, time)
        
        u, v = self.interpolate(*indices)
        
        return u, v

    def get_indices(self, lat, lon, alt, time):
        lat = (90 - lat) * self.resolution_lat_multiplier
        lon = (lon % 360) * self.resolution_lon_multiplier

        time = (time - self.time)/self.interval
        pressure = self.get_pressure_index(alt)
        
        return lat, lon, pressure, time

    def get_pressure_index(self, alt):
        indices = np.arange(0, len(self.levels))
        interp_function = interpolate.interp1d(self.levels, indices, bounds_error=False, fill_value=(0, len(self.levels)-1))
        pressure = self.alt_to_hpa(alt)

        if pressure < self.levels[0]:
            raise Exception(f"Altitude {alt} out of bounds")
        
        return interp_function(pressure)

    def interpolate(self, lat, lon, level, time):
        pressure_filter = np.array([1-level % 1, level % 1]).reshape(1, 1, 2, 1, 1)
        time_filter = np.array([1-time % 1, time % 1]).reshape(1, 1, 1, 2, 1) 
        lat_filter = np.array([1-lat % 1, lat % 1]).reshape(2, 1, 1, 1, 1)
        lon_filter = np.array([1-lon % 1, lon % 1]).reshape(1, 2, 1, 1, 1)

        lat = int(lat)
        lon = int(lon)
        level = int(level)
        time = int(time)

        cube = self.data[lat:lat+2, lon:lon+2, level:level+2, time:time+2, :]
       
        u, v = np.sum(cube * lat_filter * lon_filter * pressure_filter * time_filter, axis=(0,1,2,3))

        return u, v

    def alt_to_hpa(self, altitude):
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
    wind = WindFile("downtest/2021011600_01.npz")
    print(wind.time)

    date = datetime.datetime(2021, 1, 16, 6)
    print(wind.get(45, 90, 350, date))

    validation()

def validation():
    data = np.load("downtest/2021011600_01.npz")
    datap = data['data'][45][90][17][1]

    print(datap)

if __name__ == "__main__":
    main()

