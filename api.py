from flask import Flask, jsonify, request, Response
app = Flask(__name__)
import elev
from datetime import datetime
import simulate
import os

@app.route('/')
def home():  # pragma: no cover
    return Response(open("home.html").read(), mimetype="text/html")
    
@app.route('/which')
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
    #elev_flag = bool(args['elev'])
    alt = float(args['alt'])
    simulate.reset()
    simulate.set_constants(simulate.GEFS, whichgefs() + "_", "_" + str(model).zfill(2) + ".npy")
    try:
        path = simulate.simulate(datetime(yr, mo, day, hr, mn), lat, lon, rate, step, dur, alt, coeff)
    except (IOError, FileNotFoundError, ValueError, IndexError):
        return "error"
    return jsonify(path)

@app.route('/test')
def test():
    result = list()
    for i in range(10):
        result.append((i, 2*1, 3*i, 4*i, 5*i))
    return jsonify(result)

@app.route('/elev')
def elevation():
    lat, lon = float(request.args['lat']), float(request.args['lon'])
    return str(elev.getElevation(lat, lon))

@app.route('/ls')
def ls():
    return jsonify(os.listdir('gefs'))

@app.route('/wind')
def wind():
    args = request.args
    lat, lon = float(args['lat']), float(args['lon'])
    alt = float(args['alt'])
    yr, mo, day, hr, mn = int(args['yr']), int(args['mo']), int(args['day']), int(args['hr']), int(args['mn'])
    time = datetime(yr, mo, day, hr, mn)
    uList = list()
    vList = list()

    for i in range(1, 21):
        simulate.reset()
        simulate.set_constants(simulate.GEFS, whichgefs() + "_", "_" + str(i).zfill(2) + ".npy")
        u, v = simulate.get_wind(time,lat,lon,alt)
        uList.append(u)
        vList.append(v)
    
    return jsonify([uList, vList])


import downloaderd
from multiprocessing import Process
Process(target=downloaderd.main).start()