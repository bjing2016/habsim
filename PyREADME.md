# HABSIM

This package provides an objected oriented client interface and accession utilities to HABSIM, Stanford SSI's high altitude prediction server, at http://habsim.org. (See https://github.com/SSI-MC/habsim.) Main features include:

- Custom flight profiles built from an arbitrary number of profile segments
- API calls abstracted away in a Prediction class
- Wind and elevation data accession utilities
- WebPlot class, which permits writing of trajectories on an OpenStreetMap layer for in-browser viewing
- Trajectory optimization utilities for chasing a StaticTarget or a MovingTarget

To install, run `pip3 install habsim` and include with `import habsim`. All classes and subpackages are imported in the package-level namespace. Unfortunately, Python 2 is not supported. For method-level documentation, use `help(...)` to view the docstrings.

A note about timestamps: this package manipulates UNIX timestamps extracted from user-supplied datetime objects. When you create a datetime object, its `timestamp()` method returns as if the datetime is in the local time zone of your machine --- this package expects such behavior. You should not worry about converting your datetime object to UTC time --- doing so may cause unexpected behavior.

`pytest` is used as the testing framework. To run tests, clone this repository and run `pytest` in the base directory.

### Classes
For usage examples, see section below.

- `Segment`             segment of a profile with a constant ascent or descent rate             
- `Profile`             list of segments
- `ControlledProfile`   optimizable profile expressed as altitude waypoints rather than a list of segments
- `Prediction`          container class which holds a profile, calls the server for predictions, and holds the resulting trajectory
- `Trajectory`          single trajectory predicted for a profile or created by user from existing data
- `StaticTarget`        a nonmoving target for trajectory optimization
- `MovingTarget`        a moving target for trajectory optimization

### Subpackage `util`
Provides data accession and common calculation utilies for both client and internal use. All API calls are wrapped in methods contained herein, although the user should not need to call them directly. Relevant methods and fields for common client use are as follows:

- `checkServer` should be called anytime before running a prediction.
- `closestPoint` implements a heuristic to quickly find the closest point to a Target object in the path specified by a Trajectory. The closest point, great circle distance, and compass bearing from the path to the point are returned.
- `optimize_step` takes in a `Prediction` object containing a `ControlledProfile` (and whose other parameters must all be specified) and a`Target` and modifies the `ControlledProfile` to decrease the distance to the target according to step size `alpha`. The closest point, distance, and bearing prior to the step are returned.
- `gefs_layers` is a list of altitudes corresponding to GEFS wind layers which may be useful in initializing a `ControlledProfile`.
- `average_wind` returns the expected wind for a certain time, location, and elevation based on the 20 ensemble models.
- `wind` returns the wind data for a certain time, location, and elevation for a specific model.

### Subpackage `ioutil`
This package primarily exports a `WebPlot` class which can plot an arbitrary number of multi-segment trajectories on an HTML OpenStreetMap interface for in-browser viewing. For sample usage, see below. For complete documentation, see the docstrings.

### Usage
Constructing a profile:
```
# Ascent 3 m/s.
ascent = Segment(3, stopalt=29000)         

# Segments may be specified by end altitude or duration.
equilibrate = Segment(0, dur=3)             
descent = Segment(-3, stopalt=0)

# Segments with a non-unity drift coefficient are supported.
floating = Segment(0, dur=3, coeff=0.5)   
profile = Profile(segments=[ascent, equilibrate, descent, floating])
```
Specifying launch parameters and running the prediction:
```
time = datetime(2019, 4, 17, 22, 30)

# Default time is current time
pred = Prediction(profile=profile,
                  launchsite=hollister,
                  launchtime=time)          

# Parameters can also be passed in at runtime.
traj = prediction.run(model=1).trajectory                     
```
Saving predictions to file:
```
plt = WebPlot()
plt.origin(*hollister.coords)
plt.add(pred.split())
plt.save('name.html')
```
Running and optimizing a `ControlledProfile`:
```
# 50 hours with waypoints at 5 hour intervals
profile = hs.ControlledProfile(50, 5)

# See docstring for argument details
profile.initialize(2000, 5000, 30000, seed=[79.0, 5000])
target = StaticTarget(40.7, -92.7)
pred.profile = profile
for i in range(N):
    pred.run(model=1)
    optimize_step(pred, hs.StaticTarget(40.7, -92.7), 20)
```
The package can also be used to analyze existing trajectories:
```
traj = Trajectory(data=data)
traj.length()            # Distance travelled in km
traj.duration()          # Duration in hours
traj.endtime()           # Endpoint in local time

# Points in the trajectory can be accessed directly.
timestamp, lat, lon, alt, u_wind, v_wind, __, __ = traj[15]
```
