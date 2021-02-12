from windfile import WindFile
import math

EARTH_RADIUS = float(6.371e6)

class Balloon:
	# self.lat, self.lon, self.vrate, self.alt, self.time [datetime]
	# self.airvector -> m/s (2-tuple)
	# self.history = [Location, Location, Location, Location]
	# self.history = [{‘lat’: 37, ...}, {‘lat’: 39, ...}, {‘lat’: 41, ...}]
    # self.history = Trajectory	


    def __init__(self, lat, lon, alt, time, vrate=0, airvector=None):
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.time = time
        self.vrate = vrate
        self.airvector = airvector
        self.history = []

    def set(self, vrate, airvector=None):
        NotImplemented
    def set_bearing(self, bearing, airspeed: float):
        NotImplemented
	# set airvector, convert bearing + airspeed into airvector
    def getTrajectory(self):
        NotImplemented # returns entire history
wf = WindFile("2021012806_01.npz")
print(wf.get(30, 120, 50, 1612143049))

class Simulator:
    def __init__(self, wind_file):
        self.wind_file = wind_file
    def step(self, balloon, step_size: float):
        windvector = self.wind_file.get(balloon.lat, balloon.lon, balloon.alt, balloon.time)
        distance_moved = (windvector * step_size)
        balloon.alt = balloon.vrate * step_size
        balloon.time += step_size
        dlat, dlon = self.lin_to_angular_velocities(balloon.lat, balloon.lon, *distance_moved) 
        balloon.lat += dlat
        balloon.lon += dlon
        balloon.history.append((balloon.lat, balloon.lon))
		# get the wind at the location of the balloon
		# advance the location of the balloon
		# append the location to balloon.history

    def lin_to_angular_velocities(self, lat, lon, u, v): 
        dlat = math.degrees(v / EARTH_RADIUS)
        dlon = math.degrees(u / (EARTH_RADIUS * math.cos(math.radians(lat))))
        return dlat, dlon
		
    def simulate(self, balloon, step_size, until=None, dur=None): 
        NotImplemented
        # returns trajectory
        # call step repeatedly until either
		# 1) the balloon crashes
		# 2) if until is specified, the balloon reaches until (alt in meters)
		# 3) if dur is specified, after dur hours
		# throw an error if specified both
		# throw an error if step_size is negative or if dur is negative
balloon = Balloon(0, 30, 40, 1612143049)
simulate = Simulator(wf)
for i in range(1000):
    simulate.step(balloon, 1)
print(balloon.history)



