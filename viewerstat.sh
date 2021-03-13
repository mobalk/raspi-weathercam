#!/bin/bash
SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTPATH

if [ -z "$1" ]
then
	FileName=`mktemp`
	UserName=$(python3 config.py upload User) # how cool is this easy config read...
	curl -s -o $FileName "https://www.idokep.hu/webkamera/$UserName"
else
	FileName="$1"
fi

Viewers=$(grep "látogató az elmúlt 5 percben" $FileName | cut -d',' -f2 | sed -e 's/.* \([0-9]\+\).*/\1/')

if [ -z "$Viewers" ]
then
	AlertMsg=$(grep "Utolsó képkocka" $FileName | sed -e 's/.*p>\(.*\)<\/p.*/\1/')
	if [ -n "AlertMsg" ]
	then
		#echo "$AlertMsg"
		if command -v msmtp &> /dev/null
		then
			echo "Subject: $AlertMsg" | msmtp $(python3 config.py email Address)
		fi
	fi
else
	PrivateDir=$(python3 config.py app PrivateDir)
	# echo "$(date +'%Y-%m-%d %H:%M'), $Viewers"
	echo "$(date +'%Y-%m-%d %H:%M'), $Viewers" >> ${PrivateDir}/viewerstat.csv
fi
