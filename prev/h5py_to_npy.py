import h5py
import numpy as np
import sys



def get_timestamp(y,m,d,h):
    return str(y) + str(m).zfill(2) + str(d).zfill(2) + str(h).zfill(2);

def convert(y, m, d, h):
    path = get_timestamp(y,m,d,h)
    
    data = h5py.File(path + ".h5", 'r')['test']
    np.save(path, data)
    
def main():
    args = sys.argv[1:]
    if len(args) != 8:
        print("Invalid number of arguments.")
        exit()


    y1, y2, m1, m2, d1, d2, h1, h2 = list(map(int, args))

    for y in range(y1, y2 + 1):
        for m in range(m1, m2 + 1):
            for d in range(d1, d2 + 1):
                for h in range(h1, h2 + 6, 6):
                    try:
                        convert(y, m, d, h)
                        print("Success " + get_timestamp(y,m,d,h))
                    except (IOError, ValueError):
                        print("Error " + get_timestamp(y,m,d,h))

main()
