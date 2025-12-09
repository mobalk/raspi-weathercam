#!/bin/bash
DATE=$(date +"%Y-%m-%d_%H%M%S")

CAMPARAM="--nopreview --rotation 180 --flicker-period 10000us --autofocus-mode manual --lens-position 2.7" 
TEMPFILE="/tmp/$DATE.jpg"

rpicam-still $CAMPARAM -o $TEMPFILE
echo "CAPTURED"

brightness=$(python3 brightness.py "$TEMPFILE")
echo "BRIGHTNESS $brightness"

daynnight="DAY  "
if (( $(echo "$brightness < 0.04" | bc -l) )); then
	# image too dark, shoot another one
	rm $TEMPFILE
	daynnight="NIGHT"
	rpicam-still $CAMPARAM --shutter 2500000 --gain 4 -o $TEMPFILE
	newbrightness=$(python3 brightness.py "$TEMPFILE")
fi

if (( $(echo "$newbrightness < 0.033" | bc -l) )); then
	# image still too dark, shoot another one
	rm $TEMPFILE
	daynnight="DARK "
	rpicam-still $CAMPARAM --shutter 3800000 --gain 4 -o $TEMPFILE
	new2brightness=$(python3 brightness.py "$TEMPFILE")
fi

echo "$DATE $daynnight $brightness $newbrightness $new2brightness" >> ~/timelapse.log
mv $TEMPFILE ~/Pictures/raw/$DATE.jpg
