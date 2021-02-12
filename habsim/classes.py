import datetime
from . import util
import math
import random
import bisect

class Prediction:
    '''
    A single instance of a profile and its associated trajectory.

    Users may create Prediction objects by passing it a profile
    and then run the prediction, which calls the HABSIM server.
    '''
    def __init__(self, profile=None, model=None, launchtime=None, launchsite=None, step=240):
        '''
        Prediction objects keep track of their associated profile,
        the model number (1-20) they are based on,
        a launchtime as a datetime object, a LaunchSite, and a simulation step size in seconds.
        '''
        self.trajectory = Trajectory()
        self.model = model
        self.profile = profile
        self.launchtime = datetime.datetime.now() if not launchtime else launchtime
        self.launchsite = launchsite
        self.step = step

    
    def setLaunchSite(self, launchsite):
        '''
        Set new launch sites using this method, not by modifying the field.
        This is because the profile needs to be updated with new elevation information.
        '''    
        self.launchsite = launchsite
        if self.profile is not None:
            self.profile.setLaunchAlt(launchsite.elev)

    
    def split(self):
        '''
        Splits and returns the Trajectory into segments based on the Profile.
        '''
        if self.trajectory == None:
            raise Exception("No trajectory to split")
        return [self.trajectory[self.indices[i]:self.indices[i+1]+1] \
            for i in range(len(self.indices) - 1)]

    def run(self, model=None, launchtime=None, launchsite=None, step=None):
        '''
        If no parameters are passed in, looks in instance fields. The site passed in 
        to the Prediction object will override the launch altitude, if any, set in the 
        Profile object.

        The Trajectory will be stored in the Prediction object as its Trajectory field. Returns self (the Prediction object).
        '''
        self.trajectory = Trajectory()
        if step != None:
            self.step = step
        if launchtime != None:
            self.launchtime = launchtime
        if launchsite != None:
            self.launchsite = launchsite
        if model != None:
            self.model = model
        if self.profile == None:
            raise Exception("Profile not specified.")
        if self.launchsite == None:
            raise Exception("Launchsite not specified.")
        if self.launchtime == None:
            raise Exception("Launchtime not specified.")
        if self.model == None or self.model < 1 or self.model > 20:
            raise Exception("Model not specified or invalid.")
        self.profile.setLaunchAlt(self.launchsite.elev)


        time = self.launchtime.timestamp()
        lat, lon = self.launchsite.coords
        rates, durs, coeffs = self.profile.segmentList()
        __, alts = self.profile.waypoints()
        
        self.indices = list()

        if type(self.profile) == ControlledProfile:
            if (self.profile.interval * 3600) % self.step != 0:
                raise Exception("Simulation step must evenly divide ControlledProfile interval.")

        for i in range(len(rates)):
            self.indices.append(len(self.trajectory))
            newsegment = util.predict(time, lat, lon, alts[i], coeffs[i], self.model, rates[i], durs[i], self.step)
            if alts[i] > 31000:
                print("Warning: model inaccurate above 31km.")
            self.trajectory.append(newsegment)
            if len(newsegment) != math.ceil(durs[i] * 3600 / self.step) + 1:
                if i is len(rates)-1:
                    print("Warning: early termination of last profile segment.")
                else:
                    print("Warning: flight terminated before last profile segment.")
                    break
            time, lat, lon = self.trajectory.endpoint()[:3]
        self.indices.append(len(self.trajectory))

        return self

class LaunchSite:
    '''
    A LaunchSite keeps track of its coordinates and elevation.
    The elevation is ground elevation by default,
    but may be specified to be higher.
    ''' 
    def __init__(self, coords, elev=None):
        self.coords = coords
        self.elev = elev
        if self.elev == None:
            self.elev = util.getElev(self.coords)
        elif not util.checkElev(self):
            raise Exception("Launch site cannot be underground.")

class Trajectory:
    '''
    Data must be a list of tuples. The tuple fields may be arbitrary, but the first four
    must be UNIX TIME, LAT, LON, ALT.
    '''
    def __init__(self, data=list()):
        self.data = data

    def append(self, new):
        '''
        Adds a list of points to the trajectory, not duplicating the common point. Do NOT use this to add Trajectory objects!
        '''
        self.data = self.data[:-1] + new

    def endpoint(self):
        '''
        Last data tuple.
        '''
        return self.data[-1]

    def startpoint(self):
        '''
        First data tuple.
        '''
        return self.data[0]

    def duration(self):
        '''
        Returns duration in hours, assuming the first field of each tuple is a UNIX timestamp.
        '''
        return (self.endpoint()[0] - self.startpoint()[0]) / 3600

    def length(self):
        '''
        Distance travelled by trajectory in km.
        '''
        res = 0
        for i in range(len(self)-1):
            u, v = util.angular_to_lin_distance(self[i][1], self[i+1][1], self[i][2], self[i+1][2])
            res += math.sqrt(u**2 + v**2)
        return res

    def endtime(self):
        '''
        Datetime of trajectory end point in local time zone.
        '''
        timestamp = self.endpoint()[0]
        return datetime.datetime.fromtimestamp(timestamp)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        return self.data[key]
    
    def __str__(self):
        return str(self.data)


class ControlledProfile:

    '''
    Series of altitude waypoints at regular intervals which define a controlled profile.
    Floating segments are not yet supported. 
    '''

    def __init__(self, dur, interval):
        self.dur = dur
        self.interval = interval
    
    def initialize(self, step, lower, upper, seed=[0]):
            
        '''
        Initializes a list of waypoints beginning with seed, and then performing a Gaussian
        random walk with std.dev step bounded in [lower, upper]
        '''
        self.waypoints_data = seed
        i = len(self)
        while (i < math.ceil(self.dur / self.interval) + 1):
            self.waypoints_data.append(self[-1] + step*random.gauss(0,1))
            if self[i] < lower:
                self[i] = lower
            elif self[i] > upper:
                self[i] = upper
            i += 1

    def limit(self, lower, upper, start=0):
        '''
        Trims the profile such that any waypoints, starting with index start,
        below lower or above upper are reassigned to be equal to lower and upper, respecitively.
        '''
        for i in range(start, len(self)):
            if self[i] < lower:
                self[i] = lower
            elif self[i] > upper:
                self[i] = upper
    
    def waypoints(self):
        '''
        Returns a tuple (times, waypoints), where times is a list of hours from launch and waypoints is elevations.
        '''
        return [self.interval * i for i in range(len(self))], self.waypoints_data

    def segmentList(self):
        '''
        Returns a list of rates, dur, coeffs representing the profile. This is used to actually call the server.
        '''
        rates = [(self[i+1] - self[i])/self.interval/3600 for i in range(len(self) - 1)]
        dur = [self.interval]*(len(self)-1)
        coeff = [1]*(len(self)-1)
        return rates, dur, coeff

    def setLaunchAlt(self, alt):
        '''
        Sets the launch altitude of the ControlledProfile. Does not do much, in contrast to a normal Profile.
        '''
        self[0] = alt
    
    def __len__(self):
        return len(self.waypoints_data)

    def __getitem__(self, key):
        return self.waypoints_data[key]

    def __setitem__(self, key, item):
        self.waypoints_data[key] = item

    def __str__(self):
        return str(self.waypoints_data)


class Profile:

    '''
    A Profile object keeps track of a full flight profile for prediction.
    It is not meant to be optimized --- use ControlledProfile instead.

    A Profile consists of segments of a flight, which can be ascent, descent,
    equilibration, or floating (marine anchor).
    '''

    def __init__(self, segments=None, launchalt=None):
        self.segments = list()
        if segments != None:
            for i in range(len(segments)):
                self.append(segments[i])
        self.launchalt = launchalt
        if self.launchalt != None:
            self.setLaunchAlt(launchalt)

    def setLaunchAlt(self, alt):

        '''
        When you set the launch altitude, the information is used to populate
        altitude waypoints for each segment, propogating forward in time.
        '''

        self.launchalt = alt
        curralt = alt
        for i in range(len(self)):
            if self[i].type == "alt":
                self[i].dur = (self[i].stopalt - curralt)/self[i].rate/3600
                if self[i].dur < 0:
                    raise Exception("Profile inconsistency: altitude changes in opposite direction of movement.")
                return
            else:
                self[i].stopalt = curralt + self[i].dur * 3600 * self[i].rate
                curralt = self[i].stopalt    


    def append(self, segment):
        '''
        Runs a few checks are run to make sure the profile remains self-consistent.
        '''
        if len(self) > 0 and self[-1].stopalt != None:
                lastalt = self[-1].stopalt
                if segment.type == "alt":
                    if segment.stopalt != lastalt and segment.rate == 0:
                        raise Exception("Profile inconsistency: nonzero altitude change while equilibrated.")
                    segment.dur = (segment.stopalt - lastalt) / segment.rate / 3600
                    if segment.dur < 0:
                        raise Exception("Profile inconsistency: altitude changes in opposite direction of movement.")
                if segment.type == "dur":
                    segment.stopalt = lastalt + (segment.dur * 3600 * segment.rate)
                
        if segment.stopalt != None and segment.stopalt < 0:
            raise Exception("Profile inconsistency: altitude is negative.")
            
        self.segments.append(segment)


    def waypoints(self):

        '''
        A pair of lists [hours, altitudes] specifying the profile.
        '''

        if self.launchalt == None:
            raise Exception("Full altitude profile not specified.")
        hours = [0]
        for i in range(len(self)):
            hours.append(hours[-1] + self[i].dur)
        altitudes = [self.launchalt] + [self[i].stopalt for i in range(len(self))]
        return hours, altitudes

    def segmentList(self):
        '''
        List of rates, durs, coeffs.
        '''
        if self.launchalt == None:
            raise Exception("Full altitude profile not specified.")
        return [self[i].rate for i in range(len(self))], [self[i].dur for i in range(len(self))], [self[i].coeff for i in range(len(self))]
        

    def __len__(self):
        return len(self.segments)

    def __getitem__(self, key):
        return self.segments[key]

    def __str__(self):
        res = f"Launch alt:{self.launchalt}\n"
        for i in range(len(self)):
            res += str(self[i]) + "\n"
        return res[:-1]

class Segment:

    '''
    A single part of a profile with a constant ascent/descent rate.
    Segments may be of type "dur" (specified duration) or type "alt" (specified stopping altitude).

    Segments default to motion coefficient 1, which can be modified in the case of
    marine anchor segments.
    '''

    def __init__(self, rate, dur=None, stopalt=None, coeff=1):
        if stopalt == None and dur == None:
            raise Exception("A duration or a stopping altitude must be specified.")
        if stopalt != None and dur != None:
            raise Exception("Duration and stopping altitude both specified.")
        if dur != None and dur < 0:
            raise Exception("Segment cannot have negative duration.")
        self.rate = rate
        self.type = "dur" if dur else "alt"
        self.dur = dur
        self.stopalt = stopalt
        self.coeff = coeff
    def __str__(self):
        if self.type == "alt":
            return f'Rate:{self.rate}, Type:alt, Stopalt:{self.stopalt}, Coeff:{self.coeff} (Dur:{self.dur})'
        else:
            return f'Rate:{self.rate}, Type:dur, Dur:{self.dur}, Coeff:{self.coeff} (Stopalt:{self.stopalt})'

class StaticTarget():
    '''
    A Target is used in trajectory optimization. A StaticTarget has a constant location at all times.
    '''
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon
    
    def location(self, time):
        '''
        Returns the constant location of the StaticTarget.
        '''
        return self.lat, self.lon

class MovingTarget():
    '''
    A MovingTarget moves according to a list of times and waypoints, and intermediate locations are linearly interpolated.
    The location is not defined outside the bounds of the waypoints.
    '''
    def __init__(self, times, lats, lons):
        '''
        Pass in times in the format of timestamps in the Trajectory (usually UNIX).
        '''
        
        self.times = times
        self.lats = lats
        self.lons = lons
    
    def location(self, time):
        '''
        Interpolates the waypoints to the specified time.
        '''
        if time == self.times[-1]:
            return self.lats[-1], self.lons[-1]
        if time >= self.times[-1]:
            raise Exception("Target location not specified at given time.")
        elif time < self.times[0]:
            raise Exception("Target location not specified at given time.")
        else:
            idx = bisect.bisect_left(self.times, time)
            mod = (time-self.times[idx-1])/(self.times[idx]-self.times[idx-1])
            lat = (1-mod) * self.lats[idx-1] + mod * self.lats[idx]
            lon = (1-mod) * self.lons[idx-1] + mod * self.lons[idx]
            return lat, lon