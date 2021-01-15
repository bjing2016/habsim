import numpy as np
import math
import elev
import datetime
import bisect
import time
#from scipy import interpolate

class WindFile:
    def __init__(self, path):
        self.data_npz = np.load(path, "r")
        self.data = self.data_npz['data']
        self.time = self.data_npz['timestamp']
        self.levels = self.data_npz['levels']
        self.interval = self.data_npz['interval']
        # TODO calculate resolution

    def get(self, lat, lon, altitude, time):
        if lat < -90 or lat > 90:
            raise Exception(f"Latitude {lat} out of bounds")
        if lon < -180 or lon > 360:
            raise Exception(f"Longitude {lon} out of bounds")
        
        if lon < 0:
            lon = 360 + lon

        if isinstance(time, datetime.datetime):
            time = time.timestamp()

        if (time - self.time)/self.interval < 0 or (time - self.time)/self.interval > self.data.shape[-2]:
            raise Exception(f"Time {time} out of bounds")

        indices = self.get_indices(lat, lon, altitude, time)
        
        u, v = self.interpolate(*indices)
        
        return u, v

    def get_indices(self, lat, lon, alt, time):
        lat = 90 - lat
        lon = lon % 360

        time = (time - self.time)/self.interval
        pressure = self.get_pressure_index(alt)
        
        print("bounds:", lat, lon, pressure, time)
        return lat, lon, pressure, time

    def get_pressure_index(self, alt):

        # IGNORE: code for scipy interpolation
        #x = np.arange(range(len(self.levels)))
        #y = self.levels
        #f = interpolate.interp1d(y, x)

        pressure = self.alt_to_hpa(alt)

        if pressure < self.levels[0]:
            raise Exception(f"Altitude {alt} out of bounds")

        pressure_i = bisect.bisect_left(self.levels, pressure)
        if pressure_i == len(self.levels):
            return pressure_i-1
        return pressure_i-(self.levels[pressure_i]-pressure)/float(self.levels[pressure_i] - self.levels[pressure_i-1])

    def interpolate(self, lat, lon, level, time):
        pressure_filter = np.array([1-level % 1, level % 1]).reshape(1, 1, 2, 1, 1)
        time_filter = np.array([1-time % 1, time % 1]).reshape(1, 1, 1, 2, 1) 
        lat_filter = np.array([1-lat % 1, lat % 1]).reshape(2, 1, 1, 1, 1)
        lon_filter = np.array([1-lon % 1, lon % 1]).reshape(1, 2, 1, 1, 1)

        print("pressure_filt", pressure_filter)
        print("time_filt", time_filter)
        print("lat_filt", lat_filter)
        print("lon_filt", lon_filter)

        lat = int(lat)
        lon = int(lon)
        level = int(level)
        time = int(time)

        cube = self.data[lat:lat+2, lon:lon+2, level:level+2, time:time+2, :]
       
        print("data point 1", self.data[lat+1, lon+1, level+1, time+1, :])
        print("data point 2", self.data[lat, lon, level, time])
        print("-----------")
        print(cube * lat_filter * lon_filter * pressure_filter * time_filter) 
        print("----------")
        print("cube", cube)

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
    wind = WindFile("2021010100_01.npz")
    print(wind.time)

    date = datetime.datetime(2021, 1, 1, 6)
    print(wind.get(45, 90, 350, date))

    validation()

def validation():
    #data = np.load("downtest2/2021010100_01.npz")
    #datap = data['data'][45][90][17][1]

    #print(datap)

if __name__ == "__main__":
    main()

