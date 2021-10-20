import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import date
import sqlite3
import config

dbPath = config.get('app', 'PathToDatabase')
conn = sqlite3.connect(dbPath)
daysBefore = 6
table = pd.read_sql_query("select datetime(timestamp, 'localtime') as ts, temp"
                          + " from DHT_data"
                          + " where ts >= date('now', 'localtime', '-" + str(daysBefore) + " day')",
                          conn, parse_dates=['ts'])
table.set_index('ts')
resamp = table.resample('15T', on='ts').mean()
# add datetime column temporarily and split it up
resamp['datetime'] = resamp.index
resamp['date'] = resamp['datetime'].dt.date
resamp['time'] = resamp['datetime'].dt.time

pivo_nice = resamp.pivot(index='time', columns='date', values='temp')
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

plt.xlim([tdi[0], tdi[-1]])
plt.ylabel("hőmérséklet (°C)")
plt.legend()
plt.grid()
fig.tight_layout()
plt.show()
