from flask import Flask, jsonify, request, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

import elev
from datetime import datetime, timezone
import simulate
import os

@app.route('/')
def home():  # pragma: no cover
    return Response(open("interface/home.html").read(), mimetype="text/html")

@app.route('/zpb')
def zpb():  # pragma: no cover
    return Response(open("interface/zpb.html").read(), mimetype="text/html")

@app.route('/float')
def floatonly():  # pragma: no cover
    return Response(open("interface/float.html").read(), mimetype="text/html")

@app.route('/common.js')
def commonjs():  # pragma: no cover
    return Response(open("interface/common.js").read(), mimetype="text/html")

@app.route('/which')
def whichgefs():
    f = open("whichgefs")
    s = f.readline()
    f.close()
    return s

@app.route('/status')
def status():
    f = open("serverstatus")
    s = f.readline()
    f.close()
    return s

'''
Returns a json object representing the flight path, given a UTC launch time (yr, mo, day, hr, mn),
a location (lat, lon), a launch elevation (alt), a drift coefficient (coeff),
a maximum duration in hrs (dur), a step interval in seconds (step), and a GEFS model number (model)


Return format is a list of [loc1, loc2 ...] where each loc is a list [lat, lon, altitude, u-wind, v-wind]

u-wind is wind towards the EAST: wind vector in the positive X direction
v-wind is wind towards the NORTH: wind vector in the positve Y direction
'''
@app.route('/singlepredicth')
def singlepredicth():
    args = request.args
    yr, mo, day, hr, mn = int(args['yr']), int(args['mo']), int(args['day']), int(args['hr']), int(args['mn'])
    lat, lon = float(args['lat']), float(args['lon'])
    rate, dur, step = float(args['rate']), float(args['dur']), float(args['step'])
    model = int(args['model'])
    coeff = float(args['coeff'])
    alt = float(args['alt'])
    simulate.refresh()
    try:
        path = simulate.simulate(datetime(yr, mo, day, hr, mn).replace(tzinfo=timezone.utc), lat, lon, rate, step, dur, alt, model, coefficient=coeff)
    except (IOError, FileNotFoundError, ValueError, IndexError):
        return "error"
    return jsonify(path)

@app.route('/singlepredict')
def singlepredict():
    args = request.args
    timestamp = datetime.utcfromtimestamp(float(args['timestamp'])).replace(tzinfo=timezone.utc)
    lat, lon = float(args['lat']), float(args['lon'])
    rate, dur, step = float(args['rate']), float(args['dur']), float(args['step'])
    model = int(args['model'])
    coeff = float(args['coeff'])
    alt = float(args['alt'])
    simulate.refresh()
    try:
        path = simulate.simulate(timestamp, lat, lon, rate, step, dur, alt, model, coefficient=coeff)
    except (IOError, FileNotFoundError, ValueError, IndexError):
        return "error"
    return jsonify(path)


def singlezpb(timestamp, lat, lon, alt, equil, eqtime, asc, desc, model):
    simulate.refresh()
    try:
        dur = 0 if equil == alt else (equil - alt) / asc / 3600
        rise = simulate.simulate(timestamp, lat, lon, asc, 240, dur, alt, model, elevation=False)
        if len(rise) > 0:
            timestamp, lat, lon, alt, __, __ = rise[-1]
            timestamp = datetime.utcfromtimestamp(timestamp).replace(tzinfo=timezone.utc)
        coast = simulate.simulate(timestamp, lat, lon, 0, 240, eqtime, alt, model)
        if len(coast) > 0:
            timestamp, lat, lon, alt, __, __ = coast[-1]
            timestamp = datetime.utcfromtimestamp(timestamp).replace(tzinfo=timezone.utc)
        dur = (alt) / desc / 3600
        fall = simulate.simulate(timestamp, lat, lon, -desc, 240, dur, alt, model)
        return (rise, coast, fall)
    except (IOError, FileNotFoundError, ValueError, IndexError):
        return "error"


@app.route('/singlezpb')
def singlezpbh():
    args = request.args
    timestamp = datetime.utcfromtimestamp(float(args['timestamp'])).replace(tzinfo=timezone.utc)
    lat, lon = float(args['lat']), float(args['lon'])
    alt = float(args['alt'])
    equil = float(args['equil'])
    eqtime = float(args['eqtime'])
    asc, desc = float(args['asc']), float(args['desc'])
    model = int(args['model'])
    path = singlezpb(timestamp, lat, lon, alt, equil, eqtime, asc, desc, model)
    return jsonify(path)


@app.route('/spaceshot')
def spaceshot():
    args = request.args
    timestamp = datetime.utcfromtimestamp(float(args['timestamp'])).replace(tzinfo=timezone.utc)
    lat, lon = float(args['lat']), float(args['lon'])
    alt = float(args['alt'])
    equil = float(args['equil'])
    eqtime = float(args['eqtime'])
    asc, desc = float(args['asc']), float(args['desc'])
    paths = list()
    for model in range(1,21):
        paths.append(singlezpb(timestamp, lat, lon, alt, equil, eqtime, asc, desc, model))
    return jsonify(paths)

'''
Given a lat and lon, returns the elevation as a string
'''
@app.route('/elev')
def elevation():
    lat, lon = float(request.args['lat']), float(request.args['lon'])
    return str(elev.getElevation(lat, lon))

@app.route('/ls')
def ls():
    return jsonify(os.listdir('gefs'))


'''
Given a time (yr, mo, day, hr, mn), a location (lat, lon), and an altitude (alt)
returns a json object of [u-wind, v-wind], where


u-wind = [u-wind-1, u-wind-2, u-wind-3...u-wind-20]
v-wind = [v-wind-1, v-wind-2, v-wind-3...v-wind-20]

where the numbers are the GEFS model from which the data is extracted.
'''
@app.route('/wind')
def wind():
    simulate.refresh()
    args = request.args
    lat, lon = float(args['lat']), float(args['lon'])
    alt = float(args['alt'])
    yr, mo, day, hr, mn = int(args['yr']), int(args['mo']), int(args['day']), int(args['hr']), int(args['mn'])
    time = datetime(yr, mo, day, hr, mn).replace(tzinfo=timezone.utc)
    uList = list()
    vList = list()

    for i in range(1, 21):
        u, v = simulate.get_wind(time,lat,lon,alt, i)
        uList.append(u)
        vList.append(v)
    
    return jsonify([uList, vList])

import downloaderd
from multiprocessing import Process
Process(target=downloaderd.main).start()