#!/bin/bash
DATE=$(date +"%Y-%m-%d_%H%M%S")
rpicam-still -n --metering average --ev 0.5 -o /home/capri/Pictures/raw/$DATE.jpg

