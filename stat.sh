#!/bin/bash

# Prints a small statistics about the image files that has been captured so far.
# For each day:
#	Number of images
#	Total size in MiB
#	Average file size in KiB

SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTPATH

Dir=$(python3 config.py app ImageStorePath)
echo "date, count, total size (M), average size (K)"

for ff in `ls ${Dir}IMG*jpg | cut -d'-' -f 2| uniq`
do
	Count=$(ls ${Dir}IMG-${ff}*jpg | wc -l)
	Size=$(du -c ${Dir}IMG-${ff}*jpg | tail -1 | cut -f 1 )
	echo "$ff, $Count, $(( $Size / 1024 )), $(($Size / $Count))"
done

