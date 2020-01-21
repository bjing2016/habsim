import os
from datetime import datetime, timedelta
import time

mount = True

def log(string):
    string = '{} {} {}\n'.format(datetime.utcnow(), os.getpid(), string)
    with open('log.txt', 'a+') as f:
        f.write(string)

path = "/gefs/gefs/" if mount else "./gefs/"
whichpath = '/gefs/whichgefs' if mount else 'whichgefs'
skip_code = 3

def mostrecent():
    now = datetime.utcnow()
    return datetime(now.year, now.month, now.day, int(now.hour / 6) * 6) - timedelta(hours=6)

def currgefs():
    try:
        f = open(whichpath)
        s = f.readline()
        f.close()
    except:
        return mostrecent() - timedelta(hours=6)
    now = datetime.strptime(s, "%Y%m%d%H")
    return datetime(now.year, now.month, now.day, int(now.hour / 6) * 6)
    
def download(timestamp):
    while True: # Loop so that we can skip, if necessary
        log('Daemon launching run {}'.format(timestamp))
        command = "nice -n 50 python3 downloader.py " + str(timestamp.year) + " " + str(timestamp.month) + " " + str(timestamp.day) + " " + str(timestamp.hour)
        err = os.system(command)
        if err == 0: 
            log('Daemon registering success {}'.format(timestamp))
            return timestamp
        if err == 256 * skip_code:
            log('Daemon registering skip {}'.format(timestamp))
            os.system("rm " + path + timestamp.strftime("%Y%m%d%H") + "*")
            timestamp += timedelta(hours=6)

def move(prev, new):
    to_keep = new - timedelta(hours=384)
    while to_keep < new:
        for model in range(1, 21):
            cmd = 'mv ' + path + prev.strftime("%Y%m%d%H")+'_'+to_keep.strftime("%Y%m%d%H")+'_'+str(model).zfill(2)+'.npy ' \
                + path + new.strftime("%Y%m%d%H")+'_'+to_keep.strftime("%Y%m%d%H")+'_'+str(model).zfill(2)+'.npy'
            os.system(cmd)
        to_keep += timedelta(hours=6)
    while prev < new:
        os.system("rm " + path + prev.strftime("%Y%m%d%H") + "*")
        prev += timedelta(hours=6)

def main():
    try:
        os.mkdir('/gefs/gefs') if mount else os.mkdir("gefs")
    except FileExistsError:
        pass
    
    while True:
        curr_run = currgefs()
        next_run = curr_run + timedelta(hours=6)
        actual_run = download(next_run)
    
        f = open(whichpath, "w")
        f.write(actual_run.strftime("%Y%m%d%H"))
        f.close()
        log('Daemon updating which to {}'.format(actual_run))
        time.sleep(300)

        log('Daemon moving and deleting files')
        move(curr_run, actual_run)

if __name__ == "__main__":
    main()