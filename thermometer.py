""" Based on https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/python-setup
"""
import time
import board
import adafruit_dht
import sqlite3
import config

# Initial the dht device, with data pin connected to:
dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=False)

conf = config.init()
dbPath = conf.get('app', 'PathToDatabase')

conn = sqlite3.connect(dbPath)
with conn:
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS DHT_data (timestamp DATETIME, temp NUMERIC, hum NUMERIC)")

    # you can pass DHT22 use_pulseio=False if you wouldn't like to use pulseio.
    # This may be necessary on a Linux single board computer like the Raspberry Pi,
    # but it will not work in CircuitPython.
    # dhtDevice = adafruit_dht.DHT22(board.D18, use_pulseio=False)

    # Default sleep before retry in case of exception. After continous errors we'll increase that.
    sleepException = 3.0
    while True:
        try:
            # Print the values to the serial port
            temperature_c = dhtDevice.temperature
            humidity = dhtDevice.humidity
            print(
                time.strftime("%Y-%m-%d %H:%M:%S, ") 
                + "Temp: {:.1f} C,    Humidity: {}% ".format(
                    temperature_c, humidity
                )
            )
            cur.execute("INSERT INTO DHT_data values(datetime('now'), (?), (?))", (temperature_c, humidity))
            conn.commit()

        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            print(time.strftime("%Y-%m-%d %H:%M:%S"), error.args[0])
            time.sleep(sleepException)
            sleepException *= 2
            continue
        except Exception as error:
            dhtDevice.exit()
            raise error

        time.sleep(60)
        sleepException = 3.0
