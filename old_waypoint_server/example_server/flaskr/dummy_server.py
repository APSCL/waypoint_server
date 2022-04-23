import os, sys
import requests
import random

from flask import request, Blueprint, render_template, redirect

req_bp = Blueprint('req_bp', __name__)

#default values
x1, y1 = 0.5, 2.0
x2, y2 = 2.0, 0.0
waypointDict = {'latitude0':x1, 'longitude0':y1,
                'latitude1':x2, 'longitude1':y2,
                }


@req_bp.route('/getwaypoint', methods=('GET', 'POST'))
def get_waypoint():
    if request.method == 'GET':
        # print('this is waypointDict', waypointDict)
        return waypointDict

@req_bp.route('/choosewaypoint', methods=('GET', 'POST'))
def choose_waypoint():
    if request.method == 'POST':
        x1, y1 = request.form.get('inputX1'), request.form.get('inputY1')
        x2, y2 = request.form.get('inputX2'), request.form.get('inputY2')
        waypointDict['latitude0'], waypointDict['longitude0'] = x1, y1
        waypointDict['latitude1'], waypointDict['longitude1'] = x2, y2

        r = requests.post(url="http://192.168.0.102:5000/receiveWaypoints", data=waypointDict)

    return render_template('waypointForm.html', error = None)

@req_bp.route('/cancel', methods=('GET', 'POST'))
def cancel():
    if request.method == 'GET':
        print('cancelling nav...')
        r = requests.get(url="http://192.168.0.102:5000/cancelNav")
        # r = requests.get(url="http://localhost:5001/cancelNav")

    return redirect(url="http://localhost:5000/choosewaypoint")

@req_bp.route('/agvlocation', methods=('GET','POST'))
def agv_location():
    if request.method == 'POST' or request.method == 'GET':
        lat = request.args.get('latitude')
        lon = request.args.get('longitude')
        print('coordinates received:', lat, lon, file=sys.stdout)
        return {'latitude':lat, 'longitude':lon}

