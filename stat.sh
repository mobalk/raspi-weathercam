#!/bin/bash

Dir=$(grep ImageStorePath config.ini | cut -d'=' -f 2 )
echo "date, count, total size (M), average size (K)"

for ff in `ls ${Dir}IMG*jpg | cut -d'-' -f 2| uniq`
do
	Count=$(ls ${Dir}IMG-${ff}*jpg | wc -l)
	Size=$(du -c ${Dir}IMG-${ff}*jpg | tail -1 | cut -f 1 )
	echo "$ff, $Count, $(( $Size / 1024 )), $(($Size / $Count))"
done

