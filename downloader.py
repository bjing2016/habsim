import numpy as np
import pygrib
import urllib.request
import time, logging, socket, sys, os, argparse, shutil, glob
from datetime import datetime, timedelta
socket.setdefaulttimeout(10)

parser = argparse.ArgumentParser()
parser.add_argument("timestamp", 
        help='Model timestamp in the format "yyymmddhh"')
parser.add_argument("--logfile", default=None, 
        help="Target path for logs; prints to stdout by default.")
parser.add_argument("--savedir", default="./gefs", 
        help="./gefs by default; should be /gefs/gefs in production.")
args = parser.parse_args()

logger = logging.getLogger(__name__)
logging.basicConfig(
        filename=args.logfile,
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s', 
        datefmt='%Y-%m-%d %H:%M:%S'
)

levels = [1, 2, 3, 5, 7, 20, 30, 70, 150, 350, 450, 550, 600, 650, 750, 800, 900, 950, 975]
NUM_MEMBERS = 20
MAX_HOURS = 384
FORECAST_INTERVAL = 6
TIMEOUT = timedelta(hours=12)
start = datetime.now()

def main():
    model_timestamp = datetime.strptime(args.timestamp, "%Y%m%d%H")
    try:
        complete_run(model_timestamp)
    except Exception as e:
        logger.exception(f"Uncaught exception {e}")
        exit(1)

def complete_run(model_timestamp):
    logger.info(f'Starting run {args.timestamp}')
    y, m = model_timestamp.year, model_timestamp.month
    d, h = model_timestamp.day, model_timestamp.hour
    
    if os.path.exists(f'{args.savedir}/temp'):
        shutil.rmtree(f'{args.savedir}/temp')
        
    os.mkdir(f'{args.savedir}/temp')

    for t in range(0, FORECAST_INTERVAL+MAX_HOURS, FORECAST_INTERVAL):
        for n in range(1, 1+NUM_MEMBERS):
            single_run(y, m, d, h, t, n)
        logger.info(f'Successfully completed {args.timestamp}+{t}')

    combine_files()
    shutil.rmtree(f'{args.savedir}/temp')
    logger.info(f'Downloader finished run {args.timestamp}')

def single_run(y,m,d,h,t,n):
    savename = get_savename(y,m,d,h,t,n)
    
    if os.path.exists(f"{args.savedir}/{savename}.npy"): 
        logger.debug("{} exists; skipping.".format(savename))
        return

    url = get_url(y,m,d,h,t,n)
    logger.debug("Downloading {}".format(savename))

    download(url, f"{args.savedir}/temp/{savename}.grb2")
    logger.debug("Unpacking {}".format(savename))
    data = grb2_to_array(f"{args.savedir}/temp/{savename}")
    data = np.float16(data)
    np.save(f"{args.savedir}/temp/{savename}.npy", data)
    os.remove(f"{args.savedir}/temp/{savename}.grb2")

def download(url, path):
    RETRY_INTERVAL = 10
    while datetime.now() - start < TIMEOUT:
        try:
            urllib.request.urlretrieve(url, path); return
        except Exception as e:
            logger.debug(f'{e} --- retrying in {RETRY_INTERVAL} seconds.')
        time.sleep(RETRY_INTERVAL)
    logger.warning(f"Run {args.timestamp} timed out on {url}.")
    exit(1)

def get_savename(y,m,d,h,t,n):
    base = datetime(y, m, d, h)
    base_string = base.strftime("%Y%m%d%H")
    pred = base + timedelta(hours=t)
    predstring = pred.strftime("%Y%m%d%H")
    savename = base_string + "_" + str(t).zfill(3) + "_" + predstring + "_" + str(n).zfill(2)
    return savename

def get_url(y,m,d,h,t,n):

    m, d, h, n = map(lambda x: str(x).zfill(2), [m, d, h, n])
    t = str(t).zfill(3)
    url = f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.{y}{m}{d}/{h}/atmos/pgrb2bp5/gep{n}.t{h}z.pgrb2b.0p50.f{t}"
    return url
    
def grb2_to_array(filename): 
    ## Array format: array[u,v][Pressure][Lat][Lon] ##
    ## Currently [lat 90 to -90][lon 0 to 359]
    grbs = pygrib.open(filename + ".grb2")
    dataset = np.zeros((2, len(levels), 181, 360)) # CHANGE: (181, 360, 19, 65, 2), need to add timestamp
    u = grbs.select(shortName='u', typeOfLevel='isobaricInhPa') # gets the wind data array, which comes in 181x360
    v = grbs.select(shortName='v', typeOfLevel='isobaricInhPa')
    grbs.close()
    
    assert(len(u) == len(levels))
    
    for i, level in enumerate(levels):
        assert(u[i]['level'] == level)
        assert(v[i]['level'] == level)
        dataset[0][i] = u[i].data()[0][::2, ::2] # Takes the second element of every second array in data
        dataset[1][i] = v[i].data()[0][::2, ::2]
    return dataset

## save data as npz file of ['data', 'timestamp (unix)', 'interval', 'levels']
def combine_files():
    filesets = []
    
    for i in range(1, NUM_MEMBERS+1):
        files = glob.glob(f'{args.savedir}/temp/{args.timestamp}_*_{str(i).zfill(2)}.npy')
        files.sort()
        filesets.append(files)

    for i in range(len(filesets)):
        data = combine_npy_for_member(filesets[i])
        
        savename = args.timestamp + "_" + str(i+1).zfill(2) + ".npz"
        dt = datetime.strptime(args.timestamp, "%Y%m%d%H")
        timestamp = (dt - datetime(1970, 1, 1)).total_seconds()
        
        np.savez(f'{args.savedir}/' + savename, data=data, timestamp=timestamp, interval=FORECAST_INTERVAL*3600, levels=levels)
        logger.info(f'Combined file for member {i+1} saved as {savename}')

    logger.info('Completed combining files')

## change shape of data from (2, 19, 181, 360) to (181, 360, 19, 65, 2), with the 65 timestamps added
def combine_npy_for_member(file_list):
    data = np.stack(list(map(np.load, file_list)))
    data = np.transpose(data, (3, 4, 2, 0, 1))
    data = np.append(data, data[:, 0:1], axis=1)
    return data

if __name__ == "__main__":
    main()
