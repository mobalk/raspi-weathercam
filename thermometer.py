""" Based on
https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/python-setup
"""
import time
import sqlite3
import logging

import board
import adafruit_dht
from gpiozero.pins.rpigpio import RPiGPIOFactory, RPiGPIOPin

import config

LOGFILE = "temperature.log"

logging.basicConfig(filename=LOGFILE, level=logging.INFO)
#logging.basicConfig(level=logging.INFO)
print("Logging to " + LOGFILE)

def get_power_pin():
    """ Return BCM number of the power pin - if configured so """
    configured_pin = config.getint('thermo', 'PowerPin', fallback=-1)
    if configured_pin != -1:
        return RPiGPIOPin(RPiGPIOFactory(),22)
    return None

def power_switch(pin, state):
    """ Turn on or off the given GPIO pin """
    if pin:
        pin.output_with_state(state)

def have_you_tried_turning_it_off_and_on_again(pin):
    """ Hello, IT. Have you tried turning it off ans on again? """
    logging.error("%s Sensor malfunction. Turn it OFF and ON again.",
                  time.strftime("%Y-%m-%d %H:%M:%S,"))
    power_switch(pin, 0)
    time.sleep(3)
    power_switch(pin, 1)
    time.sleep(3)

powerPin = get_power_pin()
power_switch(powerPin, 1)

# Initiate the dht device, with data pin connected to:
dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=False)

dbPath = config.get('app', 'PathToDatabase')

conn = sqlite3.connect(dbPath)
with conn:
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS DHT_data"
                + " (timestamp DATETIME, temp NUMERIC, hum NUMERIC)")

    # Default sleep before retry in case of exception. After continous errors we'll increase that.
    sleep_exception = 3.0
    sensor_not_found = 0
    while True:
        try:
            # Print the values to the serial port
            temperature_c = dhtDevice.temperature
            humidity = dhtDevice.humidity
            logging.info("{} Temp: {:.1f} C,    Humidity: {}% ".format(
                time.strftime("%Y-%m-%d %H:%M:%S,"),temperature_c, humidity))
            cur.execute("INSERT INTO DHT_data values(datetime('now'), (?), (?))",
                        (temperature_c, humidity))
            conn.commit()

        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            logging.warning("%s %s", time.strftime("%Y-%m-%d %H:%M:%S"), error.args[0])
            time.sleep(sleep_exception)
            sleep_exception *= 2
            if "DHT sensor not found" in error.args[0]:
                sensor_not_found += 1
                if sensor_not_found == 5:
                    have_you_tried_turning_it_off_and_on_again(powerPin)
            else:
                sensor_not_found = 0
            continue
        except Exception as error:
            dhtDevice.exit()
            raise error

        time.sleep(45)
        sleep_exception = 3.0
        sensor_not_found = 0
