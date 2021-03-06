#!/usr/bin/env python3

import sqlite3
import time
import config
import requests
import logging
from os import path

# Lookup config.ini, in same directory with this script.
conf = config.init(path.join(path.split(path.realpath(__file__))[0], 'config.ini'))
config.read(conf)

LOGFILE = path.join(conf.get('app', 'PrivateDir'), 'sendTemp.log')
logging.basicConfig(filename=LOGFILE, level=logging.INFO)

dbPath = conf.get('app', 'PathToDatabase')
conn = sqlite3.connect(dbPath)
with conn:
    cur = conn.cursor()
    # calculate the average of last 3 minutes
    cur.execute("""select round(avg(temp),1), round(avg(hum))
                from DHT_data
                where timestamp > datetime('now', '-3 minutes');""")
    (temp, hum) = cur.fetchone()
    if temp and hum:
        logging.info(time.strftime("%Y.%m.%d %H:%M   temp=") + str(temp) + ', hum=' + str(hum))
        url = ('http://pro.idokep.hu/sendws.php?user='
               + conf.get('upload', 'User')
               + '&pass='
               + conf.get('upload', 'Pwd')
               + '&tipus=RaspberryPi&hom='
               + str(temp)
               + '&rh='
               + str(int(hum)))
        logging.debug(url)
        r = requests.get('http://pro.idokep.hu/sendws.php?user='
                         + conf.get('upload', 'User')
                         + '&pass='
                         + conf.get('upload', 'Pwd')
                         + '&tipus=RaspberryPi&hom='
                         + str(temp)
                         + '&rh='
                         + str(hum))
        if r.status_code == 200 and b'sikeres' in r.content:
            logging.info('OK')
        else:
            logging.error(r.status_code)
            logging.error(r.content)
    else:
        logging.warning("ERROR, no results from last 10 minutes")
