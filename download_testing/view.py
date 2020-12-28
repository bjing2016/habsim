import numpy as np
import pygrib
import logging, argparse

parser = argparse.ArgumentParser()
parser.add_argument("filename",
        help='file name for npy file')
args = parser.parse_args()

def main():
    dataset = np.load(args.filename)
    print(dataset.shape)
    print(dataset[0][0][0][0])

if __name__ == "__main__":
    main()
