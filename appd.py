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
from multiprocessing import Process

DEVICE = None
DEVICE_TYPE = None

distCMConstant = 20
backRotationTime = 0.01

usernameValue = 'pi'
passwordValue = 'Welcome123'

isPi = True
enableLogs = False
intervalSensor = 0.5
intervalLoop = 4

# isPi = False
# enableLogs = True
# intervalSensor = 10
# intervalLoop = 20

#set GPIO Pins
GPIO_TRIGGER = 16
GPIO_ECHO = 18

#
# Car Code
#
if isPi:
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(13, GPIO.OUT)
    GPIO.setup(15, GPIO.OUT)
    GPIO.setup(21, GPIO.OUT)
    GPIO.setup(19, GPIO.OUT)
    GPIO.setup(40, GPIO.OUT)
    GPIO.setup(8, GPIO.OUT)
    GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
    GPIO.setup(GPIO_ECHO, GPIO.IN)


# status: 1 -> move; 0 -> stop
def car_move(cmd, status):
    if enableLogs:
        print("car_move - command value:" + str(cmd) + ", status value:" + str(status))
    pin = car_get_command(cmd)
    if enableLogs:
        print("car_move - command pin:" + str(pin))
    if isPi:  
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
def periodicFunction(interval):
    if enableLogs or True:
        print "periodicFunction loops on a timer every %d seconds" % interval
    car_move('LEFT', 0) 
    car_move('RIGHT', 0) 
    car_move('FORWARD', 0) 
    car_move('BACK', 0) 

def sensorFunction(distance):
    print "sensorFunction loops on a timer with %d cm" % distance
    car_move('FORWARD', 0) 
    car_move('BACK', 1)
    time.sleep(backRotationTime)
    car_move('BACK', 0) 

def startTimerLoop():
    threading.Timer(intervalLoop, startTimerLoop).start()
    periodicFunction(intervalLoop)

def startTimerDistance():
    threading.Timer(intervalSensor, startTimerDistance).start()
    distCM = distance()
    if enableLogs or True:
        print "startTimerDistance loops on a timer every %d distance" % distCM
    if distCM <= distCMConstant:
        sensorFunction(distCM)


# distance calculator 

def distance():

    if isPi:
        # set Trigger to HIGH
        GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    if isPi:
        GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    if isPi:
        # save StartTime
        while GPIO.input(GPIO_ECHO) == 0:
            StartTime = time.time()
 
    if isPi:
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
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    if username == usernameValue and password == passwordValue:
        return username

@app.before_first_request
def setup():
    # Set up USB drive for missile launcher
    try:
        print("Code for initial setup")
        startTimerLoop()
        # startTimerDistance()
        print("Loop and Sensor started")
    except Exception:
        print("Exception occured in initial setup")

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.route("/")
@auth.login_required
def index():
    return render_template("rc.html")

@app.route("/<string:name>")
@auth.login_required
def remote(name):
    if name == 'favicon.ico':
        return ''
    return render_template(name + ".html")

@app.route("/car", methods=["POST"])
@auth.login_required
def car():
    data = json.loads(request.form.get("data"))
    cmd = data["value"]
    status = data["status"]
    print("car_move - command value:" + str(cmd) + ", status value:" + str(status))
    car_move(cmd, status)  
    return "success"

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=80)



