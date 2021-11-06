# -*- coding: utf-8 -*-
import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import date
import sqlite3
import config

def _read_db(col, daysBefore):
    dbPath = config.get('app', 'PathToDatabase')
    conn = sqlite3.connect(dbPath)
    table = pd.read_sql_query("select datetime(timestamp, 'localtime') as ts, " + col
                              + " from DHT_data"
                              + " where ts >= date('now', 'localtime', '-" + str(daysBefore) + " day')",
                              conn, parse_dates=['ts'])
    return table

def _create_time_pivot(table, onvalue, gran):
    resamp = table.resample(gran, on='ts').mean()
    # add datetime column temporarily and split it up
    resamp['datetime'] = resamp.index
    resamp['date'] = resamp['datetime'].dt.date
    resamp['time'] = resamp['datetime'].dt.time
    time_pivot = resamp.pivot(index='time', columns='date', values=onvalue)
    return time_pivot

def _compile_chart(data, y_label, gran):
    table = _read_db(data, 6)
    if not table.empty:
        table.set_index('ts')
        pivo_nice = _create_time_pivot(table, data, gran)
        numDateCols = pivo_nice.columns.size

        fig, ax = plt.subplots()
        fig.autofmt_xdate()
        ax.xaxis_date()
        ax.xaxis.set_major_locator(mdates.HourLocator(interval = 4))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_minor_locator(mdates.HourLocator(interval = 1))

        tdi = pd.date_range(date.today(), periods=(24 * 60 / int(gran[0:-1])), freq=gran)

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

        plt.xlim([tdi[0], tdi[-1]])
        plt.ylabel(y_label)
        plt.legend()
        plt.grid()
        fig.tight_layout()

def show_hum_plot():
    _compile_chart('hum', 'páratartalom (%)', '15T')
    plt.show()

def save_hum_plot(path, gran='15T'):
    _compile_chart('hum', 'páratartalom (%)', gran)
    plt.savefig(path)

def show_temp_plot():
    _compile_chart('temp', "hőmérséklet (°C)", '15T')
    plt.show()

def save_temp_plot(path, gran='15T'):
    _compile_chart('temp', "hőmérséklet (°C)", gran)
    plt.savefig(path)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'hum':
            show_hum_plot()
    else:
        show_temp_plot()
