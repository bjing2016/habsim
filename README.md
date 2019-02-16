# Spaceshot sims
Primarily designed for platform ascent optimization, this repo offers tools for simulating batches of historical flights in several modes, GFS ensemble based predictions, and spatial and temporal optimizations, all via a browser-based interface.

## Usage

simulate.py path_timestamp t_offset lat lon launch_alt ascent_rate timestep_s stop_alt


h5py_to_npy y1 y2 m1 m2 d1 d2 h1 h2

getanalysis.py y1 \(y2\) m1 \(m2\) d1 \(d2\) h1 \(h2\) target_path

## Installing eccodes/pygrib
Eccodes/pygrib will be run on one computer to unpack the relevant info from grb files to csv (so that not everyone has to do it).

If you want to do this yourself, download and install eccodes: https://confluence.ecmwf.int//display/ECC/Releases.
Follow the instructions to unpack the tar and install eccodes. Make sure you have CMake and gfortran installed.

To expediate pygrib installation, make sure you install eccodes in your preprocessor/linker path, or otherwise set said path to the eccodes directory.


## Data format
Full hdf5 format: dataframe="test" [u,v][Pressure][lat 90 to -90 step .5][long 0 to 359.5 step .5]

levels = [1, 2, 3, 5, 7, 10, 20, 30, 50, 70, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 925, 950, 975, 1000]


### Notes

gens-a_3_20190209_0000_018_03.grb2