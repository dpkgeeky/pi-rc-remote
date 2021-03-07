#!/bin/bash

# Call mjpstreamer
echo 'Initiate Streamer'
./mjpg-streamer.sh start

# Call Python App
echo 'Starting python app'
sudo python appd.py
