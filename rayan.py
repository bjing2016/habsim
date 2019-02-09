from matplotlib import pyplot as plt
import numpy as np
import math

def filename(year, month, day, hour):
    return "new-data/wind-%04d-%02d-%02d-%03d.txt"%(year, month, day, hour)

def hpa_to_alt(hpa):
    return (1.0 - (hpa / 1013.25) ** (1.0 / 5.255)) * 44330.0

def alt_to_hpa(alt):
    return 1013.25*(1.0 - alt/44330.0) ** (5.255)

data = {
    'u': [],
    'v': [],
    't': []
}

years = [2018]
months = [3, 4]
days = range(1, 31)
hours = range(0, 24, 3)
levels = [1, 2, 3, 5, 7, 10, 20, 30, 50, 70, 80, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 925, 950, 975, 1000]


print("Loading data...")
levels = []
for year in years:
    for month in months:
        for day in days:
            for hour in hours:
                f = open(filename(year, month, day, hour), 'r')
                rows = [row.split() for row in f.read().split('\n')[1:-1]]
                f.close()
                for val, typ, lev in rows:
                    data[typ].append((year, month, day, hour, float(val), hpa_to_alt(int(lev)), int(lev)))
                    if int(lev) not in levels:
                        levels.append(int(lev))

data = [(yr, mn, dy, hr, u, v, t, alt, hpa)\
    for (yr, mn, dy, hr, u, alt, hpa),\
        (_, _, _, _, v, _, _),\
        (_, _, _, _, t, _, _)\
        in zip(data['u'], data['v'], data['t'])]


print("Writing CSV...")
import csv
with open('wind.csv', 'w') as f:
    w = csv.writer(f)
    w.writerow(['Year', 'Month', 'Day', 'Hour (UTC)', 'EW (m/s)', 'NS (m/s)', 'Temperature (K)', 'Altitude (m)', 'Pressure (hPa)'])
    for d in data:
        w.writerow(d)


def make_csv:
    def mean(xs):
        return sum(xs)/len(xs)

    avgs = {}
    for level in levels:
        avgs[level] = (
            str(hpa_to_alt(level)),
            str(max([u for (yr, mv, dy, hr, u, v, t, alt, hpa) in data if hpa == level])),
            str(np.std([u for (yr, mv, dy, hr, u, v, t, alt, hpa) in data if hpa == level])),
            str(max([abs(v) for (yr, mv, dy, hr, u, v, t, alt, hpa) in data if hpa == level])),
            str(np.std([abs(v) for (yr, mv, dy, hr, u, v, t, alt, hpa) in data if hpa == level]))
        )

    print "wind_alts   = [", ", ".join(avgs[level][0] for level in levels), "]"
    print "wind_ew_max = [", ", ".join(avgs[level][1] for level in levels), "]"
    #print "wind_ew_std = [", ", ".join(avgs[level][2] for level in levels), "]"
    print "wind_ns_max = [", ", ".join(avgs[level][3] for level in levels), "]"
    #print "wind_ns_std = [", ", ".join(avgs[level][4] for level in levels), "]"




exit()

print "Graphing!"

for level in levels:
    plt.clf()
    plt.xlabel('EW velocity (m/s)')
    plt.ylabel('NS velocity (m/s)')
    plt.xlim(-100, 100)
    plt.ylim(-100, 100)
    plt.title('Atmosphere Profile (Mar/Apr 2018, Spaceport America, %d km)' % math.floor(hpa_to_alt(level) / 1000))
    for year in years:
        for month in months:
            for day in days:
                pts = []
                for hour in hours:
                    pts = [(u, v) for (yr, mn, dy, hr, u, v, t, alt, hpa) in data if yr == year and mn == month and dy == day and hr == hour and hpa == level]
                    plt.plot([p[0] for p in pts], [p[1] for p in pts], '.')
    plt.savefig('gif/out-%05d.pdf'%(level))
    print level, "done!"

#plt.plot([p[0] for p in pts][1:], [np.imag(i) for i in np.fft.fft([p[1] for p in pts])][1:], 'y')
#plt.plot([p[0] for p in pts][1:], [np.real(i) for i in np.fft.fft([p[1] for p in pts])][1:], 'k')
#from math import cos, pi
#plt.plot([i*3 for i in xrange(len(pts))], [(cos(20*i *2*pi / 160) + cos(140*i *2*pi / 160))*5 + 300 for i in xrange(len(pts))])

