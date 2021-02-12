"""
HABSIM
=====

Provides a client interface to Stanford SSI's high-altitude balloon prediction server at predict.stanfordssi.org.

For detailed documentation, see docstrings or README.md.

A note about timestamps: this package manipulates UNIX timestamps extracted from user-supplied datetime objects. When you create a datetime object,
its timestamp() method returns as if the datetime is in the local time zone of your machine --- this package expects such behavior. You should not worry about
converting your datetime object to UTC time --- doing so may cause unexpected behavior.

Classes
-------------------
Segment             segment of a profile with a constant ascent or descent rate             
Profile             list of segments
ControlledProfile   optimizable profile expressed as altitude waypoints rather than a list of segments
Prediction          container class which holds a profile and calls the server for predictions
Trajectory          single trajectory predicted for a profile or created by user from existing data
StaticTarget        a nonmoving target for trajectory optimization
MovingTarget        a moving target for trajectory optimization

Subpackages
-------------------
util
ioutil
"""

from . import util
from .classes import *
from . import ioutil