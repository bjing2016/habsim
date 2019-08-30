import os
from datetime import datetime, timedelta
import time

mount = True

path = "/gefs/gefs/" if mount else "./gefs/"
whichpath = '/gefs/whichgefs' if mount else 'whichgefs'

def mostrecent():
    now = datetime.utcnow()
    return datetime(now.year, now.month, now.day, int(now.hour / 6) * 6) - timedelta(hours=6)

def nextgefs():
    try:
        f = open(whichpath)
        s = f.readline()
        f.close()
    except:
        return mostrecent()
    now = datetime.strptime(s, "%Y%m%d%H")
    return datetime(now.year, now.month, now.day, int(now.hour / 6) * 6) + timedelta(hours=6)
    
def main():
    try:
        os.mkdir('/gefs/gefs') if mount else os.mkdir("gefs")
    except FileExistsError:
        pass
            
    timestamp = nextgefs() if mount else mostrecent()
    while True:
        command = "nice -n 50 python3 downloader.py " + str(timestamp.year) + " " + str(timestamp.month) + " " + str(timestamp.day) + " " + str(timestamp.hour)
        while True:
            try: 
                os.system(command)
                break
            except:
                print("Error, restarting downloader process")
        f = open(whichpath, "w")
        f.write(timestamp.strftime("%Y%m%d%H"))
        f.close()
        
        time.sleep(300)
        prev_timestamp = timestamp - timedelta(hours=6)
        os.system("rm " + path + prev_timestamp.strftime("%Y%m%d%H") + "*")
        timestamp = timestamp + timedelta(hours=6)

if __name__ == "__main__":
    main()