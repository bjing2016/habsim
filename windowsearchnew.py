import requests 
from datetime import datetime, timedelta
from webutils import *
URL = "http://predict.stanfordssi.org/predict"
duration = 72 ## hours
step = 240 ## seconds

coeffs = [0.5, 0.75, 1]

locations = {"MillCreek" :(35.9832,-121.5),
    "Limantour": (38.024,-122.88),
    "BigSur": (36.2988, -121.9035),
    "ElJarro": (37.0127, -122.222),
    "AnoNuevo": (37.1046, -122.3249),
    "PigeonPoint":  (37.179, -122.39)
}


def main():

    start = requests.get(url = "http://predict.stanfordssi.org/which").text
    start = datetime.strptime(start, "%Y%m%d%H")
    start = datetime(2019, 4, 18, 4)
    time = start
    end1 = datetime(2019, 4, 18, 15)
    interval1 = timedelta(hours = 1)
    end2 = datetime(2019, 4, 30, 9)
    interval2 = timedelta(hours = 3)
    
    times = list()
    while time <= end1:
        times.append(time)
        time = time + interval1

    while time <= end2:
        times.append(time)
        time = time + interval2

    for time in times:
        print()
        for coeff in coeffs:
            print( str(time) + " with floating coeffient " + str(coeff))
            paths = list()
            for n in range(1,21):
                path = predict(time, "PigeonPoint", coeff, n)
                paths.append(path)
            generate_html(paths, "res/", time.strftime("%Y%m%d%H") + "_" + str(coeff), start.strftime("%Y%m%d%H"), time.strftime("%Y%m%d%H"), 24, 240)

def predict(timestamp, location, drift_coeff, model):
    PARAMS = {'yr': timestamp.year, 'mo': timestamp.month , "day" : timestamp.day, "hr" : timestamp.hour, "mn" : timestamp.minute,
                    "rate" : 0, 'coeff' : drift_coeff, 'model' : model, 'alt' : 0, "lat" : locations[location][0], "lon" : locations[location][1],
                    "dur" : duration, "step": step}
    
    data = requests.get(url = URL, params = PARAMS)
    print(data.text)
    return data.json()


def generate_html(pathcache, folder, filename, model_timestamp, sim_timestamp, marker_interval, timestep):
    ## As hours --- only works if time_step goes evenly into one hour
    slat, slon, __, __, __ = pathcache[0][0]

    path = folder + "/" + filename + ".html"
    f = open(path, "w")

    f.write(part1 + str(slat) + "," + str(slon))
    f.write(part2)

    text_output = "Model time: " + model_timestamp + ", launchtime: " + sim_timestamp + "<br/><br/>"

    marker_interval_in_waypoints = marker_interval * 3600 / timestep
    sum = 0
    lengths = list()
    for i in range(len(pathcache)):
        
        path = pathcache[i]
        sum += len(path)-1
        lengths.append(float((str("%.1f" % ((len(path)-1) * timestep / 3600)))))
        for j in range(len(path)):
            lat, lon, alt, u, v = path[j]
            if (j % marker_interval_in_waypoints == 0 and j != 0) or j == len(path)-1:
                f.write(get_marker_string(lat, lon, str(i+1), str(j * timestep / 3600) + "h"))
        
        f.write(get_path_string(path, "#000000"))
    lengths.sort(reverse=True)
    print(lengths, end=" ")
    print("Average " + str("%.1f" % (sum * timestep / 3600/ 20)))
    f.write(part3short)
    f.write(text_output)
    f.write(part4 + part5)

if __name__ == "__main__":
    main()