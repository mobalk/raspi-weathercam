from flask import Flask, render_template, send_from_directory
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta
import os
import sys
sys.path.insert(0,'..')

import config
conf = config.init('../config.ini')
config.read(conf)
dbPath = conf.get('app', 'PathToDatabase')

def storeTodayChart():
    title = ''
    conn = sqlite3.connect(dbPath)
    with conn:
        table = pd.read_sql_query("""select datetime(timestamp, 'localtime') as ts, temp, hum
                                  from DHT_data where ts >= date('now', 'localtime')""",
                                  conn, parse_dates=['ts'])
        if not table.empty:
            print(table)
            table.plot(x='ts', subplots=True, grid=True, xlabel='')
            plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval = 4))
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval = 1))
            startDate = table['ts'].iloc[0].date()
            endDate = startDate + timedelta(days=1)
            plt.xlim([startDate, endDate])
            title = "chart.png"
            #title = strftime("%Y%m%d-%H%M%S.png")
            plt.savefig('static/' + title)
            return title

def secToDelta(sec):
    if sec < 60:
        return " (1 perce)"
    elif sec < 60 * 60:
        return " (" + str(int(sec / 60)) + " perce)"
    elif sec < 24 * 60 * 60:
        return " (" + str(int(sec / (60 * 60))) + " órája)"
    else:
        return " (" + str(int(sec / (24 * 60 * 60))) + " napja)"

def getLast():
    conn = sqlite3.connect(dbPath)
    with conn:
        curs=conn.cursor()

        for row in curs.execute("""SELECT datetime(timestamp, 'localtime'),
                                strftime('%s', 'now') - strftime('%s', timestamp),
                                temp, hum
                                FROM DHT_data ORDER BY timestamp DESC LIMIT 1"""):
            # format time: cut seconds and format date separator
            time = str(row[0])[:-3].replace('-', '.').replace(' ', ', ')
            delta = secToDelta(row[1])
            temp = row[2]
            hum = row[3]
        return time + delta, temp, hum

app = Flask(__name__)

@app.route('/')
def index():
    chart = storeTodayChart()
    time, temp, hum = getLast()
    templateData = {
        'time'	: time,
        'temp'	: temp,
        'hum'   : hum,
        'chart' : chart,
        'iframe' : conf.get('flask', 'usercontent', fallback="")
    }
    return render_template('index.html', **templateData)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.png', mimetype='image/png')
if __name__ == '__main__':
    app.run(debug=False, port=80, host='0.0.0.0')
