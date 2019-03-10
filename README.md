# HABSIM
High Altitude Balloon Simulator

This is a collection of tools and utilities developed for the Stanford Space Initiative's Project Spaceshot and Project Cycloon.

## Fully implemented features
-Historical batch simulator supporting standard, ZPB, and cycloon profile flights, variation in launch time, and ascent rate: https://web.stanford.edu/~bjing/hist
-GFS ensemble-based, full 384-hour launch window search with probabilistic outputs: https://web.stanford.edu/~bjing/

## Modules

### elev
Tools for fetching elevation data from .npy files. File names and contents must be from the format in https://topotools.cr.usgs.gov/gmted_viewer/viewer.htm, converted into .npy format. Usage: exports getElevation(lat, lon) function. No interpolation; rounds to nearest 1/120 of a degree.

### get_gefs
Fetches, unpacks, and converts the entire result set of a single GEFS model run (pgrb2 version) from ftp://ftp.ncep.noaa.gov/pub/data/nccf/com/gens/prod. Usage: pass in year, month, day, and hour as command line args.

### getanalysis_as_npy
Fetches, unpacks, and converts the GFS analysis from a particular time range from https://nomads.ncdc.noaa.gov/data/gfsanl/ftp://ftp.ncep.noaa.gov/pub/data/nccf/com/gens/prod Usage: pass in year_start, year_end, month_start, month_end, day_start, day_end, target_path as command line args. Ranges are parsed as Python-style slices, not consecutive timestamps. Pass in year, month, day, hour for single analysis.

### historical_batch
Runs a full historical batch sim and prints HTML file as output. Currently constants are set to work on data at https://web.stanford.edu/~bjing, which has been trimmed. Usage as follows:

simulate.py gefs_data_path y mo d h mi t_neighbors, t_interval, lat, lon, ascent_rate, ascent_neighbors, ascent_var, timestep_s, stop_alt, descent_rate, max_t_h
  

### simulate_py2
Core sim module. Must set constants before use. Exports get_wind(simtime, lat, lon, alt),  get_wind(simtime, lat, lon, alt), single_step(simtime, lat, lon, alt, ascent_rate, step), and simulate(starttime, slat, slon, ascent_rate, step, stop_alt, descent_rate, max_duration).

simulate(...) returns a TUPLE of (rise, fall, coast) for each stage of a flight, where each is a python LIST of tuples (simtime, lat, lon, alt, u_wind, v_wind).

### tif_to_npy
When run from command line, converts all .tif in local directory to .npy

### trim_data
Trims .npy files as needed. Currently set to trim analysis files to northwestern quadrant

### webutils
Exports HTML templates utility functions for generating JS and HTML strings from flight paths.

### windowsearch
Search utility for projects Cycloon and Spaceshot. Outputs html trajectories for each launch time and location and master result file.



## Notes


### Installing eccodes/pygrib
Eccodes/pygrib will be run on one computer to unpack the relevant info from grb files to csv (so that not everyone has to do it).

If you want to do this yourself, download and install eccodes: https://confluence.ecmwf.int//display/ECC/Releases.
Follow the instructions to unpack the tar and install eccodes. Make sure you have CMake and gfortran installed.

To expediate pygrib installation, make sure you install eccodes in your preprocessor/linker path, or otherwise set said path to the eccodes directory.