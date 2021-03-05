#!/bin/bash

# Call mjpstreamer
echo 'Initiate Streamer'
./mjpg-streamer.sh

# Call Python App
echo 'Starting python app'
python app.py
