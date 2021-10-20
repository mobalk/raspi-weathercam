import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta

import config
dbPath = config.get('app', 'PathToDatabase')

conn = sqlite3.connect(dbPath)

with conn:
    table = pd.read_sql_query("""select datetime(timestamp, 'localtime') as ts, temp, hum
                              from DHT_data where ts >= date('now', 'localtime', '-1 day')""",
                              conn, parse_dates=['ts'])
    print(table)

    table.plot(x='ts', subplots=True, grid=True, title='mai adatok', xlabel='')
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval = 4))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval = 1))
    startDate = table['ts'].iloc[0].date()
    endDate = startDate + timedelta(days=2)
    plt.xlim([startDate, endDate])

    plt.show()
