#!/bin/bash
set -o pipefail

LOG_DIR="/home/pi/logs/$(date +%Y-%m-%d)"
mkdir -p "$LOG_DIR"

cd /home/pi/receipt-printer
./bin/python3 main.py "$@" 2>&1 | tee -a "$LOG_DIR/reciept.log"
