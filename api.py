from flask import Flask, jsonify, request
app = Flask(__name__)
import elev
from datetime import datetime
import simulate
import os

@app.route('/whichgefs')
def whichgefs():
    f = open("whichgefs")
    s = f.readline()
    f.close()
    return s

@app.route('/predict')
def predict():
    args = request.args
    yr, mo, day, hr, mn = int(args['yr']), int(args['mo']), int(args['day']), int(args['hr']), int(args['mn'])
    lat, lon = float(args['lat']), float(args['lon'])
    rate, dur, step = float(args['rate']), float(args['dur']), float(args['step'])
    model = int(args['model'])
    coeff = float(args['coeff'])
    elev_flag = bool(args['elev'])
    alt = float(args['alt'])
    simulate.set_constants(simulate.GEFS, whichgefs() + "_", "_" + str(model).zfill(2) + ".npy")
    try:
        path = simulate.simulate(datetime(yr, mo, day, hr, mn), lat, lon, rate, step, dur, alt, coeff, elev_flag)
    except (IOError, FileNotFoundError, ValueError, IndexError):
        return "error"
    return jsonify(path)

@app.route('/elev')
def elevation():
    lat, lon = float(request.args.get('lat')), float(request.args.get('lon'))
    return jsonify(int(elev.getElevation(lat, lon)))

@app.route('/ls')
def ls():
    return jsonify(os.listdir('gefs'))

import downloader
from threading import Thread
Thread(target=downloader.main).start()