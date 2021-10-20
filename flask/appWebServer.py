from flask import Flask, render_template, send_from_directory
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta, date, datetime
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

def storeTempStatChart():
    title = ''
    conn = sqlite3.connect(dbPath)
    with conn:
        daysBefore = 6
        table = pd.read_sql_query("select datetime(timestamp, 'localtime') as ts, temp"
                                  + " from DHT_data"
                                  + " where ts >= date('now', 'localtime', '-" + str(daysBefore) + " day')",
                                  conn, parse_dates=['ts'])
        if not table.empty:
            #print(table)
            table.set_index('ts')
            resamp = table.resample('15T', on='ts').mean()
            # add datetime column temporarily and split it up
            resamp['datetime'] = resamp.index
            resamp['date'] = resamp['datetime'].dt.date
            resamp['time'] = resamp['datetime'].dt.time

            pivo_nice = resamp.pivot(index='time', columns='date', values='temp')
            print(pivo_nice)
            numDateCols = pivo_nice.columns.size

            fig, ax = plt.subplots()
            fig.autofmt_xdate()
            ax.xaxis_date()
            ax.xaxis.set_major_locator(mdates.HourLocator(interval = 4))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.xaxis.set_minor_locator(mdates.HourLocator(interval = 1))

            tdi = pd.date_range(date.today(), periods=(24 * 60 / 15), freq='15T')

            if (numDateCols > 2):
                    # calculate average and std deviation for earlier days
                pivo_nice['mean'] = pivo_nice.iloc[:, 0:(numDateCols - 1)].mean(axis=1)
                pivo_nice['std'] = pivo_nice.iloc[:, 0:(numDateCols - 1)].std(axis=1)
                pivo_nice['m-s'] = pivo_nice['mean'] - pivo_nice['std']
                pivo_nice['m+s'] = pivo_nice['mean'] + pivo_nice['std']

                plt.fill_between(tdi, pivo_nice['m-s'], pivo_nice['m+s'], color="palegoldenrod", alpha=0.5);
                plt.plot(tdi, pivo_nice['mean'], linestyle='dashed' ,color="goldenrod", alpha=0.7, label="Elmúlt heti átlag")

            if (numDateCols > 1):
                # print yesterday's values
                plt.plot(tdi, pivo_nice.iloc[:, (numDateCols - 2)], linestyle='dashed', color="slategrey", alpha=0.9, label="Tegnapi adatok")

            # plot the last day (today)
            plt.plot(tdi, pivo_nice.iloc[:, (numDateCols - 1)], color="navy", label="Mai mérés")

            #plt.plot(tdi, pivo_nice.iloc[:, 0:(numDateCols - 1)].min(axis=1))
            #plt.plot(tdi, pivo_nice.iloc[:, 0:(numDateCols - 1)].max(axis=1))
            plt.xlim([tdi[0], tdi[-1]])
            #plt.xlabel(date.today().strftime("%Y.%m.%d"))
            #plt.title("Mai hőmérséklet az elmúlt hét tükrében")
            plt.ylabel("hőmérséklet (°C)")
            plt.legend()
            plt.grid()
            fig.tight_layout()
            #title = "chart.png"
            title = datetime.now().strftime("%Y%m%d-%H%M%S.png")
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
    chart = storeTempStatChart()
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
