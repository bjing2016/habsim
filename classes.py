from windfile import WindFile

class Balloon:
	# self.lat, self.lon, self.vrate, self.alt, self.time [datetime]
	# self.airvector -> m/s (2-tuple)
	# self.history = [Location, Location, Location, Location]
	# self.history = [{‘lat’: 37, ...}, {‘lat’: 39, ...}, {‘lat’: 41, ...}]
    # self.history = Trajectory	


    def __init__(self, location=None, time=None, vrate=None, airvector=None):
        NotImplemented

    def set(vrate, airvector=None):
        NotImplemented
    def set_bearing(bearing, airspeed: float):
        NotImplemented
	# set airvector, convert bearing + airspeed into airvector
    def getTrajectory(self):
        NotImplemented # returns entire history
wf = WindFile("2021012806_01.npz")
print(wf.get(30, 120, 50, 1612143049))

