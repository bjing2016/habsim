# HABSIM
High Altitude Balloon Simulator
http://habsim.org

## Overview
This is a prediction server developed for the Stanford Space Initiative's Balloons team. The aims of the prediction server, in comparison to existing ones, are as follows:

- Offer probabilistic predictions based on the Monte-Carlo GEFS run set
- Offer predictions out to the maximum time window permitted by GEFS (+378 hrs)
- Offer finer and broader control over simulation parameters, including ascent rate, duration, simulation step, and drift coefficient
- Export an intuitive prediction API which can be used to simulate arbitrary flight profiles
- Offer a web-based UI which captures the functionality and flexibility of the API

## Status / Operation
The server automatically downloads and curates GEFS data from ftp://ftp.ncep.noaa.gov/pub/data/nccf/com/gens/prod every 6 hrs. Data is usually available 6 hrs after the GEFS timestamp; this can be checked at http://habsim.org/which.
Download progress may be manually checked at http://habsim.org/ls.

## API Usage
### `/singlepredicth`
#### Args
UTC launch time (`yr`, `mo`, `day`, `hr`, `mn`), location (`lat`, `lon`), launch elevation (`alt`), drift coefficient (`coeff`), maximum duration in hrs (`dur`), step interval in seconds (`step`), GEFS model number (`model`).

#### Returns
A list of `[loc1, loc2 ...]` where each loc is a list `[UNIX_timestamp, lat, lon, altitude, u-wind, v-wind]`. The list ends when the flight has exceeded its duration or the altitude goes below the ground elevation. An error is returned if the time boundaries of the dataset are exceeded.

Note:
`u-wind` is wind towards the EAST: wind vector in the positive X direction
`v-wind` is wind towards the NORTH: wind vector in the positve Y direction

### `/singlepredict`
As above, except time is passed as a UNIX timestamp (`timestamp`)

### `/spaceshot`
#### Args
Launch time as UNIX timestamp (`timestamp`), launch location (`lat`, `lon`), launch altitude (`alt`), equilibrium altitude (`equil`), time to stay at equilibrium (`eqtime`), ascent rate (`asc`), descent rate (`desc`).

Note that descent rate is -dh/dt. That is, if the balloon is falling, `desc` > 0.

#### Returns
A list of `[path1, path2, ... path20]` where each path is a list of three paths `[rise, equil, fall]`. Each path is a list `[loc1, loc2 ...]` and each `loc` is a list `[UNIX_timestamp, lat, lon, altitude, u-wind, v-wind]` as above.

If the equilibrium altitude is below the launch altitude, the rise path will be of zero length and the equilibrium path will begin at the launch altitude.

If the equilibrium time is zero, the equilibrium path will be of zero length and the fall path will begin at the altitude of the last data point in rise (unless rise is also of zero length, in which case it will begin at the launch altitude)

### `/elev`
#### Args
Lat, lon

#### Returns
Elevation at that location as a string. Elevation data has a resolution of 120 points per degree and is rounded, not interpolated. Not all elevation data is available; see https://web.stanford.edu/~bjing/elev. Locations outside these files are reported as elevation 0.

### `/windensemble`
#### Args
Time (`yr`, `mo`, `day`, `hr`, `mn`), a location (`lat`, `lon`), and an altitude (`alt`)

#### Returns
`[u-wind, v-wind, du/dh, dv/dh]`, where

- `u-wind = [u-wind-1, u-wind-2, u-wind-3...u-wind-20]`
- `v-wind = [v-wind-1, v-wind-2, v-wind-3...v-wind-20]`
- `du/dh = [du/dh-1, du/dh-2, du/dh-3...du/dh-20]`
- `dv/dh = [dv/dh-1, dv/dh-2, dv/dh-3...dv/dh-20]`

where the numbers are the GEFS model from which the data is extracted.

Note:
`u-wind` is wind towards the EAST: wind vector in the positive X direction
`v-wind` is wind towards the NORTH: wind vector in the positve Y direction

Derivatives are approximated by linearly interpolating (with respect to altitude) between wind layers. GEFS wind data has resolution 1 point per degree. Data is interpolated in all four dimensions; in particular, actual wind is interpolated with respect to pressure.

### `/wind`
Like /windensemble, except it takes a model parameter (`model`) and returns only the data for that model.

### `/which`
Returns GFS timestamp

### `/status`
Returns server status

## Files

### api.py
Exports API described above and initialized downloader service

### downloader.py
Takes command line args [year month day hour] and downloads the entire dataset corresponding to that GEFS timestamp in directory gefs/ from ftp://ftp.ncep.noaa.gov/pub/data/nccf/com/gens/prod. Implements multiprocessing and broad exception handling, including premature execution, corrupted data, and interrupted downloads. Converts entire dataset to npy.

### downloaderd.py
Daemon-like downloader service. Repeatedly executes downloader.py for each new dataset.

### elev.py
Tools for fetching elevation data from .npy files. File names and contents must be from the format in https://topotools.cr.usgs.gov/gmted_viewer/viewer.htm, converted into .npy format. Usage: exports getElevation(lat, lon) function. No interpolation; rounds to nearest 1/120 of a degree.

### interface
UI interface for the prediction server.

### simulate.py
Core sim module.

## Notes

### Installing eccodes/pygrib
The purpose of the server is to run eccodes/pygrib on one computer to unpack grb2 files so that not everyone has to do it.

If you still want to do this yourself, download and install eccodes: https://confluence.ecmwf.int//display/ECC/Releases.
Follow the instructions to unpack the tar and install eccodes. Make sure you have CMake and gfortran installed.

To expediate pygrib installation, make sure you install eccodes in your preprocessor/linker path, or otherwise set said path to the eccodes directory.

### Running the server
`docker build . -t habsim-root`
`docker run -d -v $(pwd):/home/run -v /gefs:/gefs --name=habsim-$USER -p 80:5000 habsim-root`
`python3 downloaderd.py --dlogfile=/var/log/downloaderd.log --logfile=/var/log/downloader.log --savedir=/gefs/gefs --statusfile=/gefs/whichgefs`
