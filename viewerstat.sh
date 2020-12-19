#!/bin/bash
SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTPATH

FileName=`mktemp`
UserName=$(python3 config.py upload User) # how cool is this easy config read...
PrivateDir=$(python3 config.py app PrivateDir)
curl -s -o $FileName "https://www.idokep.hu/webkamera/$UserName"
Viewers=$(grep "a mai nap" $FileName | cut -d',' -f2 | sed -e 's/.*>\([0-9]\+\).*/\1/')
echo "$(date +'%Y-%m-%d %H:%M'), $Viewers" >> ${PrivateDir}/viewerstat.csv

