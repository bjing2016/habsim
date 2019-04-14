import os
from datetime import datetime, timedelta

path = "./gefs/"

def main():

    f = open("downloaderstatus", 'r')
    if f.readline() == "Running":
        print("Downloader process already running, quitting")
        return
    f.close()
    f = open("downloaderstatus", 'w')
    if not __name__ == "__main__":
        f.write("Running")
    f.close()

    try:
        os.mkdir("gefs")
    except FileExistsError:
        pass
    
    now = datetime.utcnow()
    timestamp = datetime(now.year, now.month, now.day, int(now.hour / 6) * 6) - timedelta(hours=6)
    while True:
        command = "python3 downloader.py " + str(timestamp.year) + " " + str(timestamp.month) + " " + str(timestamp.day) + " " + str(timestamp.hour)
        os.system(command)
        f = open("whichgefs", "w")
        f.write(timestamp.strftime("%Y%m%d%H"))
        f.close()
        prev_timestamp = timestamp - timedelta(hours=6)
        os.system("rm " + path + prev_timestamp.strftime("%Y%m%d%H") + "*")
        timestamp = timestamp + timedelta(hours=6)

if __name__ == "__main__":
    main()