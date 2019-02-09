# Spaceshot sims
Platform ascent optimization

1) Eccodes/pygrib will be run on one computer to unpack the relevant info from grb files to csv (so that not everyone has to do it).

    If you want to do this yourself, download and install eccodes: https://confluence.ecmwf.int//display/ECC/Releases.
    Follow the instructions to unpack the tar and install eccodes. Make sure you have CMake and gfortran installed.

    To expediate pygrib installation, make sure you install eccodes in your preprocessor/linker path, or otherwise set said path to the eccodes directory.

2) Csv files will be hosted on a public server at web.stanford.edu/~bjing
3) Distributed users may run simulation code without installing eccodes.
