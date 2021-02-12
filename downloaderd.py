import os, time, logging, argparse, glob, shutil
import urllib.request
from datetime import datetime, timedelta

parser = argparse.ArgumentParser()
parser.add_argument("--dlogfile", default=None, 
        help="Target path for daemon logs; stdout by default.")
parser.add_argument("--logfile", default=None,
        help="Target path for downloader logs; stdout by default")
parser.add_argument("--savedir", default="./gefs", 
        help="./gefs by default; should be /gefs/gefs in production.")
parser.add_argument("--statusfile", default="./whichgefs",
        help="./whichgefs by default; should be /gefs/whichgefs in production.")
args = parser.parse_args()

logger = logging.getLogger(__name__)
logging.basicConfig(
        filename=args.dlogfile,
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s', 
        datefmt='%Y-%m-%d %H:%M:%S'
)

fmt = lambda x: x.strftime("%Y%m%d%H")

def main():
    try:
        os.mkdir(args.savedir)
    except FileExistsError:
        pass

    manager = DownloadManager()
    while True:
        manager.download()

class DownloadManager:
    def __init__(self):
        curr = curr_gefs()
        if curr:
            self.next = curr + timedelta(hours=6)
            logger.info(f"Reading current gefs as {fmt(curr)}")
        else:
            self.next = most_recent()
            logger.info(f"No current gefs found; computing next run as {fmt(self.next)}")

        logger.info(f"Initializing download manager with next run {fmt(self.next)}")

    # Attempts to download the next run
    def download(self):
        logger.info(f"Initializing download with run {fmt(self.next)}")

        if self.should_skip():
           self.next = most_recent()
           logger.warning(f"Current next is too old, setting to {fmt(self.next)}")
        
        ready = self.wait()
        if not ready: return
        logger.info(f"Run {fmt(self.next)} ready to start")
        
        cmd = f"python3 downloader.py --savedir={args.savedir} {fmt(self.next)}"
        if args.logfile: cmd += f" --logfile={args.logfile}"
        logger.info(cmd)
        
        retval = os.system(cmd)
        if retval == 0:
            logger.info(f"Run {fmt(self.next)} completed successfully.")
            self.update()

        else:
            logger.warning(f"Run {fmt(self.next)} failed.")
            self.clean()

        self.next += timedelta(hours=6)

    def wait(self):
        INTERVAL = 300

        logger.info(f"Waiting for run {fmt(self.next)} to become available.")
        url = get_url(self.next)
        logger.info(f"Checking URL {url}")

        while True:
            try:
                urllib.request.urlopen(url)
                logger.info(f"Found URL {url}")
                return True
            except Exception as e:
                logger.debug(f"{e} --- waiting {INTERVAL} seconds")
            time.sleep(INTERVAL)
            if self.should_skip():
                logger.warning(f"Waited too long; skipping run {fmt(self.next)}")
                self.next += timedelta(hours=6)
                return False

    def should_skip(self):
        return self.next < datetime.utcnow() - timedelta(hours=12)
    
    def update(self):
        curr = curr_gefs()

        with open(args.statusfile, "w") as f:
            f.write(fmt(self.next))
        logger.info(f"Writing {fmt(self.next)} into {args.statusfile}")

        if curr:
            logger.info(f"Removing previous download {fmt(curr)}")
            for f in glob.glob(f"{args.savedir}/{fmt(curr)}*"):
                os.remove(f)

    def clean(self):
        logger.warning(f"Removing incomplete download {fmt(self.next)}")
        for f in glob.glob(f"{args.savedir}/{fmt(self.next)}*"):
            os.remove(f)
        if os.path.exists(f"{args.savedir}/temp"):
            shutil.rmtree(f"{args.savedir}/temp")

def curr_gefs():
    if not os.path.exists(args.statusfile): return None
    with open(args.statusfile) as f:
        curr = datetime.strptime(f.read(), "%Y%m%d%H")
    return curr
        
def get_url(model_timestamp):
    y, m = model_timestamp.year, model_timestamp.month
    d, h = model_timestamp.day, model_timestamp.hour
    n, t = 1, 0
    m, d, h, n = map(lambda x: str(x).zfill(2), [m, d, h, n])
    t = str(t).zfill(3)
    url = f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.{y}{m}{d}/{h}/atmos/pgrb2bp5/gep{n}.t{h}z.pgrb2b.0p50.f{t}"
    return url
        
def most_recent():
    now = datetime.utcnow()
    return datetime(now.year, now.month, now.day, int(now.hour / 6) * 6) - timedelta(hours=6)

if __name__ == "__main__":
    main()
