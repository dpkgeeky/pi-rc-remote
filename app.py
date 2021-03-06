#
# Missile Launcher Code
#
import struct
import os
import sys
import platform
import time
import socket
import re
import json
import base64
import threading

DEVICE = None
DEVICE_TYPE = None

#
# Car Code
#

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
GPIO.setup(40, GPIO.OUT)
GPIO.setup(8, GPIO.OUT)


# status: 1 -> move; 0 -> stop
def car_move(cmd, status):
    print("car_move - command value:" + str(cmd) + ", status value:" + str(status))
    pin = car_get_command(cmd)
    print("car_move - command pin:" + str(pin))
    GPIO.output(pin, bool(int(status)))

def car_get_command(key):
    mapping = {
        "LEFT": 19, 
        "RIGHT": 21,
        "FORWARD": 13,
        "BACK": 15,
        "FLIGHT": 40,
        "BLIGHT": 8
    }
    return mapping.get(key)

# periodic
interval = 3

def myPeriodicFunction():
    print "This loops on a timer every %d seconds" % interval
    car_move('LEFT', 0) 
    car_move('RIGHT', 0)
    car_move('FORWARD', 0)
    car_move('BACK', 0) 

def startTimer():
    threading.Timer(interval, startTimer).start()
    myPeriodicFunction()

# 
# Flask Code
# 
from flask import Flask, render_template, request, json

app = Flask(__name__)

@app.before_first_request
def setup():
    # Set up USB drive for missile launcher
    try:
        print("Code for initial setup")
    except Exception:
        print("Exception occured in initial setup")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/<string:name>")
def remote(name):
    return render_template(name + ".html")

@app.route("/car", methods=["POST"])
def car():
    data = json.loads(request.form.get("data"))
    cmd = data["value"]
    status = data["status"]
    car_move(cmd, status)  
    return "success"

if __name__ == "__main__":
    startTimer()
    app.run(debug=True, host="0.0.0.0", port=8080)
 


