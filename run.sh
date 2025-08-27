#!/bin/bash

LOG_DIR="/home/pi/logs/$(date +Y-%m-%d)"
mkdir -p "$LOG_DIR"

cd /home/pi/reciept
./bin/python3 main.py >> "$LOG_DIR/reciept.log" 2>&1
