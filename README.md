# Spaceshot sims
Platform ascent optimization

1) Eccodes will be run on one computer to unpack the relevant info from grb files to csv (so that not everyone has to do it).

    If you want to do this yourself, download and install eccodes: https://confluence.ecmwf.int//display/ECC/Releases
    Follow the instructions to unpack the tar.
    Make sure you have CMake and gfortran installed.
    Follow the instructions to install eccodes.

2) Csv files will be hosted on a public server at web.stanford.edu/~bjing
3) Distributed users may run simulation code without installing eccodes.
