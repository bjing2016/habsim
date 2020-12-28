import numpy as np
import pygrib
import logging, argparse

parser = argparse.ArgumentParser()
parser.add_argument("filename",
	help='file name for grb file')
args = parser.parse_args()

def main():
    grbs = pygrib.open(args.filename)
    u = grbs.select(shortName='u', typeOfLevel='isobaricInhPa')
    v = grbs.select(shortName='v', typeOfLevel='isobaricInhPa')
    print(u)
    print(v)
    print("-----------------")

    data_u = u[0].data()
    print(data_u[0][::2, ::2].shape)
    print(data_u)
    print("-----------------")
    print(data_u[0][::2, ::2])



    dataset = np.zeros((181, 360, 19, 65, 2))

    print(dataset.shape)
    print(dataset)
    dataset = data_u[0][::2, ::2]
    print(dataset)
    print(dataset.shape)

    print("__________________")
    print(data_u)

if __name__ == "__main__":
    main()
