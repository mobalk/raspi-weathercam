#!/bin/bash
DATE=$(date +"%Y-%m-%d_%H%M%S")

rpicam-still --nopreview --metering average --ev 0.5 -o /tmp/$DATE.jpg
brightness=$(convert "/tmp/$DATE.jpg" -colorspace Gray -format "%[fx:mean]" info:)

daynnight="DAY  "
if (( $(echo "$brightness < 0.03" | bc -l) )); then
	# image too dark, shoot another one
	rm /tmp/$DATE.jpg
	daynnight="NIGHT"
	# exp = 1.4 sec, ISO 400
	rpicam-still --nopreview -o /tmp/$DATE.jpg --shutter 1400000 --gain 4
	brightness=$(convert "/tmp/$DATE.jpg" -colorspace Gray -format "%[fx:mean]" info:)
fi

echo "$DATE $daynnight $brightness" >> ~/timelapse.log
mv /tmp/$DATE.jpg ~/Pictures/raw/$DATE.jpg
