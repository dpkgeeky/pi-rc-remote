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
#set GPIO Pins
GPIO_TRIGGER = 16
GPIO_ECHO = 18

GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)


# status: 1 -> move; 0 -> stop
def car_move(cmd, status, disableLogs=False):
    if disableLogs:
        print("car_move - command value:" + str(cmd) + ", status value:" + str(status))
    pin = car_get_command(cmd)
    if disableLogs:
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
intervalDistance = 0.1
intervalLoop = 4
def myPeriodicFunction(interval):
    car_move('LEFT', 0, True) 
    car_move('RIGHT', 0, True) 
    car_move('FORWARD', 0, True) 
    car_move('BACK', 0, True) 

def startTimerLoop():
    threading.Timer(intervalLoop, startTimerLoop).start()
    myPeriodicFunction(intervalLoop)

def startTimerDistance():
    threading.Timer(intervalDistance, startTimerDistance).start()
    distCM = distance()
    # print "This loops on a timer every %d distance" % distCM
    if distCM <= 20:
        myPeriodicFunction(intervalDistance)

# distance calculator 

def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance    

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
    startTimerLoop()
    startTimerDistance()
    app.run(debug=True, host="0.0.0.0", port=8080)
 


