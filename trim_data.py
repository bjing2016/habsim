import numpy
import sys

def get_timestamp(y,m,d,h):
    return str(y) + str(m).zfill(2) + str(d).zfill(2) + str(h).zfill(2);


def trim(y,m,d,h):
    data = numpy.load(get_timestamp(y,m,d,h) + ".npy")
    data = data[:,:,0:182,360:]
    numpy.save("trim/" + get_timestamp(y,m,d,h)+".npy", data)


## Format: [u,v][Pressure][lat 90 to -90 step .5][long 0 to 359.5 step .5]
def main():
    args = sys.argv[1:]
    if len(args) != 4 and len(args) != 8:
        print("Invalid number of arguments.")
        exit()


    y1, y2, m1, m2, d1, d2, h1, h2 = list(map(int, args))

    for y in range(y1, y2 + 1):
        for m in range(m1, m2 + 1):
            for d in range(d1, d2 + 1):
                for h in range(h1, h2 + 6, 6):
                    try:
                        trim(y, m, d, h)
                        print("Success " + get_timestamp(y,m,d,h))
                    except (IOError, ValueError):
                        print("Error " + get_timestamp(y,m,d,h))

main()
